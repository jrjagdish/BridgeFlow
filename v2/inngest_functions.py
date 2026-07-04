"""
Inngest functions — replaces Celery Beat for time-based (scheduled) runs.

Inngest calls into this app over HTTP (POST /api/inngest, wired up in main.py
via inngest.fast_api.serve), so no separate worker/beat process is needed —
this runs fine on Vercel's serverless functions.
"""

import inngest

from v2.inngest_client import inngest_client


@inngest_client.create_function(
    fn_id="dispatch-all-syncs",
    trigger=inngest.TriggerCron(cron="*/5 * * * *"),
)
async def dispatch_all_syncs_scheduled(ctx: inngest.Context) -> dict:
    """Runs every 5 minutes. Dispatches sync jobs for all eligible users."""
    from v2.tasks import dispatch_all_syncs_async

    await ctx.step.run("dispatch-syncs", dispatch_all_syncs_async)
    return {"status": "ok"}


functions = [dispatch_all_syncs_scheduled]
