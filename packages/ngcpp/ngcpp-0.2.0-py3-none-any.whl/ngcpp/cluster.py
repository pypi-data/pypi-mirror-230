import os
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from typing import List, Tuple

import pandas as pd
from loguru import logger as logging
from omegaconf import OmegaConf

from ngcpp.utils import run_command

__all__ = ["Cluster", "CLUSTER_SETTING"]

pd.set_option("display.max_colwidth", 150)

CLUSTER_SETTING = OmegaConf.load(
    os.path.join(os.path.dirname(__file__), "cluster.yaml")
)

ALIAS_TO_CLUSTER = {v.alias: k for k, v in CLUSTER_SETTING.items()}


class Cluster:
    def __init__(self, alias="10"):
        self.name = ALIAS_TO_CLUSTER[alias]
        info = CLUSTER_SETTING[self.name]
        self.ace = info["ace"]
        self.team = info["team"]
        self.gpu_memory = info["memory"]

    def check_one_job_hang(self, job_id):
        dir_fp = f"/tmp/ngcpp/{job_id}"
        if not os.path.exists(dir_fp):
            os.makedirs(dir_fp)
        run_command(
            f"ngc batch telemetry --interval-time 30 --interval-unit MINUTE --format_type csv"
            f" --team {self.team} --ace {self.ace} {job_id} > {dir_fp}/telemetry.csv"
        )
        telemetry_data = pd.read_csv(f"{dir_fp}/telemetry.csv")
        telemetry_data["Time"] = pd.to_datetime(telemetry_data["Time"])
        # Checking the latest value of GPU_FI_PROF_PIPE_TENSOR_ACTIVE
        tensor_core_value = telemetry_data["GPU_FI_PROF_PIPE_TENSOR_ACTIVE"].iloc[-1]

        # If the latest value is non-zero, the hang time is zero
        if tensor_core_value > 0.01:
            hang_time = timedelta(0)
        else:
            # Finding the timestamp of the latest non-zero 'GPU_FI_PROF_PIPE_TENSOR_ACTIVE'
            non_zero = telemetry_data.loc[
                telemetry_data["GPU_FI_PROF_PIPE_TENSOR_ACTIVE"] > 0.01, "Time"
            ]
            if non_zero.empty:
                latest_non_zero_time = telemetry_data["Time"].iloc[0]
            else:
                latest_non_zero_time = non_zero.iloc[-1]

            # Finding the timestamp of the latest entry in the data
            latest_time = telemetry_data["Time"].iloc[-1]

            # Calculating the duration from now to the latest non-zero 'GPU_FI_PROF_PIPE_TENSOR_ACTIVE'
            hang_time = latest_time - latest_non_zero_time

        return hang_time, tensor_core_value

    def check_jobs_hang_in_parallel(
        self, job_ids: List[str], max_workers: int = None
    ) -> List[Tuple[timedelta, float]]:
        """
        Check multiple jobs for hang in parallel.

        Parameters:
        - job_ids (List[str]): List of job IDs to check.
        - max_workers (int, optional): Maximum number of threads to use. \
            Default is None which lets ThreadPoolExecutor decide.

        Returns:
        - List[Tuple[timedelta, float]]: List of hang times and tensor core values for each job ID.
        """

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            results = list(executor.map(self.check_one_job_hang, job_ids))

        return results

    def report_hangs(self, verbose=True):
        run_command(
            f"ngc batch list --format_type csv --team {self.team} --ace {self.ace}"
            f" --status RUNNING > /tmp/ngcpp_{self.name}.csv"
        )
        df = pd.read_csv(f"/tmp/ngcpp_{self.name}.csv").dropna(subset=["Id"])
        df["Id"] = df["Id"].astype(int)
        # if df is empty, return
        if df.empty:
            logging.info("No running jobs")
            return df

        # Collect all job IDs into a list
        job_ids_list = df["Id"].tolist()

        # Call check_jobs_hang_in_parallel once with the list of job IDs
        results = self.check_jobs_hang_in_parallel(job_ids_list)

        # Update the DataFrame df with the results
        for job_id, (hang_time, tensor_core_value) in zip(job_ids_list, results):
            df.loc[df["Id"] == job_id, "HangTime"] = hang_time
            df.loc[df["Id"] == job_id, "TensorCore"] = tensor_core_value
            # print(f"Job {job_id} \n HangTime: {hang_time} and TensorCore: {tensor_core_value}")

        # filter out non-hangs
        _df = df[df["HangTime"] > timedelta(0)].copy()
        # if no hangs, return
        if _df.empty:
            logging.info("No hanging jobs")
        else:
            if verbose:
                # Adding the 'ngc_web' column with the desired URL format
                _df["ngc_web"] = _df["Id"].apply(
                    lambda row_id: f"https://bc.ngc.nvidia.com/jobs/{row_id}?tab=telemetry"
                )

                # Printing the specified columns, including the new 'ngc_web' column if needed
                print(
                    _df[
                        [
                            "Id",
                            "Name",
                            "HangTime",
                            "TensorCore",
                            "Duration",
                            "Replicas",
                            "ngc_web",
                        ]
                    ].to_string(index=False)
                )

        return _df

    def report_user_usage(self):
        run_command(
            f"ngc batch list --all --format_type csv --team {self.team} --ace {self.ace} "
            f"--status RUNNING > /tmp/ngcpp_{self.name}.csv"
        )
        df = pd.read_csv(f"/tmp/ngcpp_{self.name}.csv")
        df = df.dropna(subset=["Id"])
        df["Id"] = df["Id"].astype(int)

        # Grouping the data by the 'Submitted By' column and summing the 'Replicas' for each user
        df = df.groupby("Submitted By")["Replicas"].sum().reset_index()

        # Sorting the result by Replicas usage in descending order
        df = df.sort_values(by="Replicas", ascending=False)

        # Displaying the result
        print(df.to_string(index=False))
        return df

    def jobs(
        self,
    ):
        run_command(
            f"ngc batch list --format_type csv --team {self.team} --ace {self.ace}"
            f" > /tmp/ngcpp_{self.name}.csv"
        )
        df = pd.read_csv(f"/tmp/ngcpp_{self.name}.csv").dropna(subset=["Id"])
        df["Id"] = df["Id"].astype(int)
        df = df.sort_values("Id", ascending=False)
        # Adding the 'ngc_web' column with the desired URL format
        df["ngc_web"] = df["Id"].apply(
            lambda row_id: f"https://bc.ngc.nvidia.com/jobs/{row_id}?tab=telemetry"
        )

        return df
