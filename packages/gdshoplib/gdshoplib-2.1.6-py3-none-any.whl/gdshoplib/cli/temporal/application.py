import asyncio
import random
import string

import typer
from temporalio.client import Client
from temporalio.worker import Worker

from gdshoplib.core.settings import EcosystemSettings

app = typer.Typer()


@app.command()
def workflow():
    async def action():
        client = await Client.connect(EcosystemSettings().TEMPORAL_URL)

        # Run activity worker
        async with Worker(
            client, task_queue="say-hello-task-queue", activities=["say-hello-activity"]
        ):
            # Run the Go workflow
            workflow_id = "".join(
                random.choices(string.ascii_uppercase + string.digits, k=30)
            )
            result = await client.execute_workflow(
                "say-hello-workflow",
                "Temporal",
                id=workflow_id,
                task_queue="say-hello-task-queue",
            )

            print(result)

    asyncio.run(action())


if __name__ == "__main__":
    app()
