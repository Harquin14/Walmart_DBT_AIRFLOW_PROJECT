"""Utilities for triggering and waiting for Databricks jobs."""

import os
import time

from databricks.sdk import WorkspaceClient
from databricks.sdk.service.jobs import RunLifeCycleState, RunResultState


def run_databricks_job(job_id: str, poll_interval_seconds: int = 10) -> int:
    workspace = WorkspaceClient(
        host=os.environ["DATABRICKS_HOST"],
        token=os.environ["DATABRICKS_TOKEN"],
    )
    triggered_run = workspace.jobs.run_now(job_id=job_id)
    run_id = triggered_run.run_id
    if run_id is None:
        raise RuntimeError(f"Databricks did not return a run ID for job {job_id}")

    terminal_states = {
        RunLifeCycleState.TERMINATED,
        RunLifeCycleState.SKIPPED,
        RunLifeCycleState.INTERNAL_ERROR,
    }

    while True:
        run = workspace.jobs.get_run(run_id=run_id)
        state = run.state
        if state is not None and state.life_cycle_state in terminal_states:
            if state.result_state == RunResultState.SUCCESS:
                return run_id
            raise RuntimeError(
                f"Databricks job {job_id} run {run_id} finished with "
                f"lifecycle state {state.life_cycle_state} and "
                f"result state {state.result_state}"
            )

        time.sleep(poll_interval_seconds)
