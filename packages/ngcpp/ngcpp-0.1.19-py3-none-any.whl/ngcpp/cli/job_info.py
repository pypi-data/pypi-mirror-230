# pylint: disable=redefined-outer-name
import os
import sys
import time

import click
import tqdm
import typer
from loguru import logger as logging
from plumbum.commands.processes import ProcessExecutionError
from pyfzf.pyfzf import FzfPrompt

from ngcpp.cluster import Cluster
from ngcpp.utils import run_batch_commands, run_command

app = typer.Typer()


@app.command()
def kill(
    alias: str = typer.Argument(
        "10",
        help="cluster alias, e.g. 10 for prd10, "
        "use alias command to list all available aliases",
    ),
    is_fzf: bool = typer.Option(
        True,
        "-i/-I",
        help="use iteractive fzf to select job, default true. otherwise delete all jobs",
    ),
    confirm: bool = typer.Option(
        False, "-c/-C", help="confirm to kill job, default false -> only print"
    ),
):
    """
    Select one or more jobs and ngc batch kill
    """
    cluster = Cluster(alias)
    df = cluster.jobs()
    df = df[df["Status"].isin(["QUEUED", "STARTING", "RUNNING"])]
    df = df[["Id", "Name", "Status", "Duration", "Replicas"]]
    # if df is empty, return
    if df.empty:
        logging.info("No jobs to kill")
        return df

    if is_fzf:
        fzf_str = df.to_string(index=False).split("\n")
        try:
            fzf = FzfPrompt()
            select_runs_str = fzf.prompt(fzf_str, "-m")
        except ProcessExecutionError:
            sys.exit(1)
        except Exception as error:  # pylint: disable=broad-except
            raise RuntimeError(  # pylint: disable=raise-missing-from
                "FZF error: {}".format(error)
            )

        selected_ids = [
            int(select_run_str.split(" ")[0]) for select_run_str in select_runs_str
        ]
    else:
        selected_ids = df["Id"].tolist()

    # filter df based on selected ids
    df = df[df["Id"].isin(selected_ids)]
    logging.warning(f"will kill jobs. Confirmed : {confirm} ")
    print(df[["Id", "Name", "Duration", "Replicas"]].to_string(index=False))
    if confirm:
        if click.confirm("Do you really want to kill?", default=True):
            shell_cmds = [f"ngc batch kill {job}" for job in selected_ids]
            results = run_batch_commands(shell_cmds)
            for selected_id, result in zip(selected_ids, results):
                logging.warning(f"ngc batch kill {selected_id} : {result}")

    return df


@app.command()
def result(  # pylint: disable=too-many-locals
    alias: str = typer.Argument(
        "10",
        help="cluster alias, e.g. 10 for prd10, "
        "use alias command to list all available aliases",
    ),
    is_fzf: bool = typer.Option(
        False,
        "-i/-I",
        help="use iteractive fzf to select job, default false -> use latest job",
    ),
    rank0_only: bool = typer.Option(
        True, "-m/-M", help="download rank0 for multinode, default true"
    ),
):
    """
    Select one job and ngc result download
    """
    cluster = Cluster(alias)
    df = cluster.jobs()
    df = df[
        df["Status"].isin(["RUNNING", "KILLED_BY_USER", "FINISHED_SUCCESS", "FAILED"])
    ]
    df = df[["Id", "Name", "Status", "Duration", "Replicas"]]
    # if df is empty, return
    if df.empty:
        logging.info("No jobs to download results")
        return df
    if is_fzf:
        fzf_str = df.to_string(index=False).split("\n")
        try:
            fzf = FzfPrompt()
            select_run_str = fzf.prompt(fzf_str)[0]
            selected_id = int(select_run_str.split(" ")[0])
        except ProcessExecutionError:
            sys.exit(1)
        except Exception as error:  # pylint: disable=broad-except
            raise RuntimeError(  # pylint: disable=raise-missing-from
                "FZF error: {}".format(error)
            )
    else:
        selected_id = df["Id"].tolist()[-1]

    select_run = df[df["Id"] == selected_id].iloc[0]
    job_id = select_run["Id"]
    save_dir = os.path.expanduser("~/ngc_results")
    logging.warning(f"\n {select_run}")
    if not os.path.exists(save_dir):
        os.makedirs(save_dir, exist_ok=True)
    if os.path.exists(f"{save_dir}/{job_id}"):
        os.system(f"rm -rf {save_dir}/{job_id}")

    if select_run["Replicas"] == 1 or rank0_only:
        logging.warning(f"ngc result download {job_id} --dest {save_dir}")
        run_command(f"ngc result download {job_id} --dest {save_dir}")
        dir_list = os.listdir(f"{save_dir}/{job_id}")
        for file_name in dir_list:
            logging.info(f"{save_dir}/{job_id}/{file_name}")
    else:
        save_dir = f"{save_dir}/{job_id}"
        logging.warning(
            f'ngc result download {job_id} --dest {save_dir} with {select_run["Replicas"]} replicas'
        )
        os.makedirs(save_dir, exist_ok=True)
        for replica in tqdm.tqdm(range(select_run["Replicas"])):
            run_command(f"ngc result download {job_id}:{replica} --dest {save_dir}")

        dir_list = os.listdir(save_dir)
        for file_name in dir_list:
            logging.info(f"{save_dir}/{file_name}")

    return df


@app.command()
def bash(
    alias: str = typer.Argument(
        "10",
        help="cluster alias, e.g. 10 for prd10, "
        "use alias command to list all available aliases",
    ),
    is_fzf: bool = typer.Option(
        True,
        "-i/-I",
        help="use iteractive fzf to select job, default false -> use latest job",
    ),
    replica: int = typer.Option(
        0, help="which node to exec for multinode, default master node"
    ),
):
    """
    select one job and ngc batch exec
    """
    cluster = Cluster(alias)
    df = cluster.jobs()
    df = df[df["Status"].isin(["RUNNING", "QUEUED", "STARTING"])]
    df = df[["Id", "Name", "Status", "Duration", "Replicas"]]
    # if df is empty, return
    if df.empty:
        logging.info("No jobs to download results")
        return df
    if is_fzf:
        fzf_str = df.to_string(index=False).split("\n")
        try:
            fzf = FzfPrompt()
            select_run_str = fzf.prompt(fzf_str)[0]
            selected_id = int(select_run_str.split(" ")[0])
        except ProcessExecutionError:
            sys.exit(1)
        except Exception as error:  # pylint: disable=broad-except
            raise RuntimeError(  # pylint: disable=raise-missing-from
                "FZF error: {}".format(error)
            )
    else:
        selected_id = df["Id"].tolist()[-1]

    select_run = df[df["Id"] == selected_id].iloc[0]
    job_id = select_run["Id"]
    logging.warning(f"\n {select_run}")
    logging.warning(f"ngc batch exec {job_id}")
    while True:
        if select_run["Replicas"] == 1:
            rtn_value = os.system(f"ngc batch exec {job_id}")
        else:
            rtn_value = os.system(f"ngc batch exec {job_id}:{replica}")
        if rtn_value != 0:
            logging.warning(
                f"ERROR VALUE {rtn_value}: ngc batch exec {job_id} failed, retrying..."
            )
            time.sleep(1)
        else:
            break

    return df


def main():
    app()
