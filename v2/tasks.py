"""
v2/tasks.py — Celery tasks for Google Sheets -> Notion sync.

Each task uses asyncio.run() because Tortoise ORM is async but Celery workers
are synchronous by default. Every task call gets a fresh event loop with its
own Tortoise connection pool, which is closed in the finally block.

Running the worker:
  celery -A v2.celery_app worker --loglevel=info -P solo   (Windows dev)
  celery -A v2.celery_app worker --loglevel=info            (Linux / prod)

Running the beat scheduler:
  celery -A v2.celery_app beat --loglevel=info
"""

import asyncio
import hashlib
import json
import uuid as uuid_mod
from datetime import datetime, timezone, timedelta

from debug import logger
from v2.celery_app import celery_app


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _run(coro):
    """Run an async coroutine from a synchronous Celery task."""
    return asyncio.run(coro)


async def _init_db():
    from tortoise import Tortoise
    from v2.models import get_db_config
    await Tortoise.init(config=get_db_config())


async def _close_db():
    from tortoise import Tortoise
    await Tortoise.close_connections()


def _row_hash(row: dict) -> str:
    return hashlib.sha256(json.dumps(row, sort_keys=True).encode()).hexdigest()


# ---------------------------------------------------------------------------
# Core sync logic (async — runs inside asyncio.run())
# ---------------------------------------------------------------------------

async def _do_sync(user_id: str, sync_job_id: str, manage_db: bool = True):
    if manage_db:
        await _init_db()
    try:
        from v2.models import UserConfig, SyncJob, SyncedRow
        from v2.sheets_service import fetch_all_sheet_rows
        from v2.notion_service import upsert_notion_row

        job = await SyncJob.get(id=sync_job_id)
        job.status = "running"
        job.started_at = datetime.now(timezone.utc)
        await job.save()

        config = await UserConfig.get_or_none(user_id=user_id)
        if not config or not config.spreadsheet_id or not config.notion_database_id or not config.column_mappings:
            job.status = "failed"
            job.errors = ["Sync config incomplete — set spreadsheet_id, notion_database_id, id_column, and column_mappings via POST /config"]
            job.finished_at = datetime.now(timezone.utc)
            await job.save()
            return

        mappings = config.column_mappings  # [{sheet_col, notion_property, type}]

        # Determine which sheet column is the unique row identifier
        id_col = config.id_column
        if not id_col and mappings:
            id_col = mappings[0]["sheet_col"]

        if not id_col:
            job.status = "failed"
            job.errors = ["No id_column configured — set it via POST /config"]
            job.finished_at = datetime.now(timezone.utc)
            await job.save()
            return

        # Fetch all rows from Google Sheets
        try:
            _headers, rows = await fetch_all_sheet_rows(
                user_id, config.spreadsheet_id, config.sheet_name or "Sheet1"
            )
        except Exception as e:
            job.status = "failed"
            job.errors = [f"Failed to fetch sheet data: {e}"]
            job.finished_at = datetime.now(timezone.utc)
            await job.save()
            logger.error(f"[sync] Job {sync_job_id}: sheet fetch error: {e}")
            return

        job.rows_fetched = len(rows)
        await job.save()

        errors = []
        rows_created = 0
        rows_updated = 0
        rows_skipped = 0
        seen_ids: set = set()

        for i, row in enumerate(rows):
            row_id = str(row.get(id_col, "")).strip()
            if not row_id:
                errors.append(f"Row missing value in id_column '{id_col}': {row}")
                continue

            if row_id in seen_ids:
                errors.append(f"Duplicate id_column value '{row_id}' in sheet — second occurrence skipped")
                continue
            seen_ids.add(row_id)

            row_hash = _row_hash(row)

            try:
                synced_row = await SyncedRow.filter(user_id=user_id, row_id=row_id).first()

                if synced_row is None:
                    # Brand new row — create a Notion page
                    notion_page_id = await upsert_notion_row(
                        user_id, config.notion_database_id, None, row, mappings
                    )
                    await SyncedRow.create(
                        id=uuid_mod.uuid4(),
                        user_id=user_id,
                        row_id=row_id,
                        row_hash=row_hash,
                        notion_page_id=notion_page_id,
                        last_sync_job_id=sync_job_id,
                        status="synced",
                    )
                    rows_created += 1
                    logger.info(f"[sync] Created row '{row_id}' -> notion_page={notion_page_id}")

                elif synced_row.row_hash != row_hash:
                    # Row changed — update the existing Notion page
                    await upsert_notion_row(
                        user_id, config.notion_database_id,
                        synced_row.notion_page_id, row, mappings
                    )
                    synced_row.row_hash = row_hash
                    synced_row.last_synced_at = datetime.now(timezone.utc)
                    synced_row.last_sync_job_id = sync_job_id
                    synced_row.status = "synced"
                    synced_row.error_message = None
                    await synced_row.save()
                    rows_updated += 1
                    logger.info(f"[sync] Updated row '{row_id}'")

                else:
                    # Row unchanged — skip to avoid redundant Notion API calls
                    rows_skipped += 1

            except Exception as e:
                error_msg = f"Row '{row_id}': {e}"
                errors.append(error_msg)
                logger.error(f"[sync] Job {sync_job_id}: {error_msg}")

                # Preserve previous synced data — only update error fields
                if synced_row := await SyncedRow.filter(user_id=user_id, row_id=row_id).first():
                    synced_row.status = "error"
                    synced_row.error_message = str(e)
                    synced_row.last_sync_job_id = sync_job_id
                    await synced_row.save()

            # Flush progress to DB every 10 rows so SSE stream shows live counts
            if (i + 1) % 10 == 0:
                job.rows_created = rows_created
                job.rows_updated = rows_updated
                job.rows_skipped = rows_skipped
                job.errors = errors
                await job.save()

        job.rows_created = rows_created
        job.rows_updated = rows_updated
        job.rows_skipped = rows_skipped
        job.errors = errors
        job.status = "completed_with_errors" if errors else "completed"
        job.finished_at = datetime.now(timezone.utc)
        await job.save()

        logger.info(
            f"[sync] Job {sync_job_id} done — "
            f"fetched={job.rows_fetched} created={rows_created} "
            f"updated={rows_updated} skipped={rows_skipped} errors={len(errors)}"
        )
    finally:
        if manage_db:
            await _close_db()


# ---------------------------------------------------------------------------
# Standalone async dispatcher (used by the /cron/sync endpoint on Vercel)
# ---------------------------------------------------------------------------

async def dispatch_all_syncs_async():
    """
    Dispatch syncs for all eligible users without Celery.
    Runs each user's sync concurrently via asyncio.gather.
    Call this from a FastAPI route (Tortoise already connected — manage_db=False).
    """
    from v2.models import UserConfig, SyncJob
    from datetime import datetime, timezone, timedelta
    import uuid as uuid_mod

    stale_cutoff = datetime.now(timezone.utc) - timedelta(minutes=30)
    stale_jobs = await SyncJob.filter(
        status__in=["pending", "running"],
        created_at__lt=stale_cutoff,
    )
    for stale in stale_jobs:
        stale.status = "failed"
        stale.errors = ["Marked failed — job was stuck for >30 minutes"]
        stale.finished_at = datetime.now(timezone.utc)
        await stale.save()
        logger.warning(f"[cron] Marked stale job {stale.id} as failed")

    configs = await UserConfig.all().prefetch_related("user")
    logger.info(f"[cron] Checking {len(configs)} user config(s)")
    sync_tasks = []
    for config in configs:
        user = config.user
        if not config.spreadsheet_id or not config.notion_database_id or not config.column_mappings:
            continue
        has_completed = await SyncJob.filter(
            user_id=user.id, status__in=["completed", "completed_with_errors"]
        ).exists()
        if not has_completed:
            continue
        already_running = await SyncJob.filter(
            user_id=user.id, status__in=["pending", "running"]
        ).exists()
        if already_running:
            continue
        job = await SyncJob.create(
            id=uuid_mod.uuid4(),
            user_id=user.id,
            status="pending",
            triggered_by="scheduler",
        )
        logger.info(f"[cron] Queuing sync for {user.email} job={job.id}")
        sync_tasks.append(_do_sync(str(user.id), str(job.id), manage_db=False))

    if sync_tasks:
        await asyncio.gather(*sync_tasks, return_exceptions=True)
    logger.info(f"[cron] dispatch_all_syncs_async done — {len(sync_tasks)} job(s) started")


# ---------------------------------------------------------------------------
# Celery tasks
# ---------------------------------------------------------------------------

@celery_app.task(name="v2.tasks.sync_user", bind=True, max_retries=3)
def sync_user(self, user_id: str, sync_job_id: str):
    """Sync one user's Google Sheet -> Notion DB. Retries up to 3 times on failure."""
    try:
        _run(_do_sync(user_id, sync_job_id))
    except Exception as exc:
        logger.error(f"[celery] sync_user failed user={user_id} job={sync_job_id}: {exc}")
        raise self.retry(exc=exc, countdown=60)


@celery_app.task(name="v2.tasks.dispatch_all_syncs")
def dispatch_all_syncs():
    """
    Celery Beat task — runs every 5 minutes.
    Dispatches a sync_user task for every user who:
      1. Has a complete sync config
      2. Has completed at least one manual sync (first sync must be manual)
      3. Does NOT already have a pending/running sync job
    """
    async def _dispatch():
        await _init_db()
        try:
            from v2.models import UserConfig, SyncJob

            # Mark jobs stuck in pending/running for >30 min as failed
            stale_cutoff = datetime.now(timezone.utc) - timedelta(minutes=30)
            stale_jobs = await SyncJob.filter(
                status__in=["pending", "running"],
                created_at__lt=stale_cutoff,
            )
            for stale in stale_jobs:
                stale.status = "failed"
                stale.errors = ["Marked failed by Beat — job was stuck for >30 minutes"]
                stale.finished_at = datetime.now(timezone.utc)
                await stale.save()
                logger.warning(f"[beat] Marked stale job {stale.id} as failed")

            configs = await UserConfig.all().prefetch_related("user")
            logger.info(f"[beat] Checking {len(configs)} user config(s)")
            for config in configs:
                user = config.user
                if not config.spreadsheet_id or not config.notion_database_id or not config.column_mappings:
                    logger.warning(
                        f"[beat] Skipping {user.email} — incomplete config: "
                        f"spreadsheet={bool(config.spreadsheet_id)} "
                        f"database={bool(config.notion_database_id)} "
                        f"mappings={bool(config.column_mappings)}"
                    )
                    continue

                has_completed = await SyncJob.filter(
                    user_id=user.id,
                    status__in=["completed", "completed_with_errors"],
                ).exists()
                if not has_completed:
                    logger.warning(f"[beat] Skipping {user.email} — no completed sync yet")
                    continue

                already_running = await SyncJob.filter(
                    user_id=user.id,
                    status__in=["pending", "running"],
                ).exists()
                if already_running:
                    logger.warning(f"[beat] Skipping {user.email} — sync already in flight")
                    continue

                job = await SyncJob.create(
                    id=uuid_mod.uuid4(),
                    user_id=user.id,
                    status="pending",
                    triggered_by="scheduler",
                )
                sync_user.delay(str(user.id), str(job.id))
                logger.info(f"[beat] Dispatched sync for {user.email} job={job.id}")
        finally:
            await _close_db()

    _run(_dispatch())
