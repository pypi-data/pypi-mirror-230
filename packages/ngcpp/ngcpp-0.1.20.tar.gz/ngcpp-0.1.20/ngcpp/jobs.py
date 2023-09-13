import re
from datetime import timedelta
from typing import Dict

import pandas as pd
from loguru import logger as logging

from ngcpp.cluster import Cluster
from ngcpp.utils import parse_duration, run_command

# pylint: disable=W0640, W1401


def resume_jobs_cluster(
    job_resume_cmd: Dict[str, str],
    alias="10",
):
    if job_resume_cmd is None:
        return
    cluster = Cluster(alias)

    jobs_all_df = cluster.jobs()
    jobs_all_df["Duration"] = jobs_all_df["Duration"].apply(parse_duration)
    for job_name, cmd in job_resume_cmd.items():
        # job name must follow the format: job_name or job_name + _ngcpp_resubmit_ + resubmit_number
        # Define a function to check if the name matches the desired pattern
        def filter_job_name(name):
            return name == job_name or bool(  # pylint: disable=W0640
                re.match(f"{job_name}_ngcpp_resubmit_\d+", name)
            )

        # Use the function to filter the DataFrame
        cur_jobs_df = jobs_all_df[jobs_all_df["Name"].apply(filter_job_name)].copy()

        # Extract the resubmit_number from the 'Name' column
        def extract_resubmit_number(name):
            match = re.search(
                f"{job_name}_ngcpp_resubmit_(\d+)", name  # pylint: disable=W0640
            )
            return int(match.group(1)) if match else 0

        cur_jobs_df.loc[:, "resubmit_number"] = cur_jobs_df.loc[:, "Name"].apply(
            extract_resubmit_number
        )

        # Sort the cur_jobs_df by resubmit_number, largest first
        cur_jobs_df = cur_jobs_df.sort_values(by="resubmit_number", ascending=False)

        if cur_jobs_df.empty:
            logging.info(f"No job found for {job_name}, let us submit the first one")
            cmd = cmd.replace(job_name, f"{job_name}_ngcpp_resubmit_0")
            result = run_command(cmd)
            logging.trace(f"\n \t stdout: {result.stdout}")
        else:
            latest_job_row = cur_jobs_df.iloc[0]

            if is_resubmit_job(latest_job_row, cluster):
                resubmit_number = latest_job_row["resubmit_number"] + 1
                cmd = cmd.replace(
                    job_name, f"{job_name}_ngcpp_resubmit_{resubmit_number}"
                )
                logging.info(f"Resubmitting job {job_name} \n {cmd}")
                if latest_job_row["Status"] == "RUNNING":
                    logging.info(
                        f"Killing job \n {latest_job_row} \n \
                                ngc_telemetry \t https://bc.ngc.nvidia.com/jobs/{latest_job_row['Id']}?tab=telemetry"
                    )
                    run_command(f"ngc batch kill {latest_job_row['Id']}")
                result = run_command(cmd)
                logging.trace(f"\n \t stdout: {result.stdout}")


def is_resubmit_job(
    job_row: pd.Series, cluster: Cluster, hang_thres: float = 0.8
) -> bool:
    """
    Determines if a job should be resubmitted.

    * If the job is in QUEUED / STARTING / FINISHED_SUCCESS, it should not be resubmitted.
    * If the job is RUNNING and has been running for less than 1 hour, it should not be resubmitted.
    * If the job is RUNNING and has been running for more than 1 hour, we check if it's hung.
    """
    # Check for QUEUED, STARTING, or FAILED status
    if job_row["Status"] in [
        "QUEUED",
        "STARTING",
        "PENDING_STORAGE_CREATION",
    ]:
        logging.debug(f"Job {job_row['Id']} is in {job_row['Status']} status, skip")
        return False
    if job_row["Status"] == "RUNNING" and job_row["Duration"] < 1:
        # Check for RUNNING status with duration less than 1 hour
        logging.debug(
            f"Job {job_row['Id']} is in {job_row['Status']} status and less than 1h, skip"
        )
        return False
    if job_row["Status"] in [
        "FAILED",
        "KILLED_BY_SYSTEM",
        "KILLED_BY_USER",
        "KILLED_BY_ADMIN",
        "FINISHED_SUCCESS",
    ]:
        logging.info(f"Job {job_row['Id']} is in {job_row['Status']} status, resubmit")
        return True
    if job_row["Status"] == "RUNNING" and job_row["Duration"] >= 1:
        hang_time, _ = cluster.check_one_job_hang(job_row["Id"])
        if hang_time > timedelta(hours=hang_thres):
            logging.info(
                f"Job {job_row['Id']} is in {job_row['Status']} status but hang for more than {hang_thres}h, resubmit"
            )
            return True
        logging.debug(f"Job {job_row['Id']} is in {job_row['Status']}, skip")
        return False

    raise NotImplementedError(f"Unexpected job status: {job_row['Status']}")
