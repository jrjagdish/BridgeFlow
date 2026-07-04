from dotenv import load_dotenv

import inngest
from debug import logger

load_dotenv()

inngest_client = inngest.Inngest(
    app_id="bridgeflow",
    logger=logger,
)
