#!/usr/bin/env python3
# pylint: disable=global-variable-not-assigned, global-statement
import json
import os
import os.path as osp
import time

import hydra
from loguru import logger
from omegaconf import DictConfig, OmegaConf

from ngcpp.cluster import ALIAS_TO_CLUSTER, CLUSTER_SETTING
from ngcpp.utils import run_command, yes_or_no

job_cmd = []
job_cfg = {
    "aceId": 257,
    "aceInstance": "dgx1v.16g.1.norm",
    "aceName": "nv-us-west-2",
    "name": "to-file",
    "publishedContainerPorts": [9999, 8888],
    "dockerImageName": "nvidian/lpr-imagine/imaginaire_qsh:1.1",
    "command": "sleep 7d",
    "minAvailability": 1,
    "replicaCount": 1,
    "arrayType": "PYTORCH",
    "runPolicy": {"totalRuntimeSeconds": 604800, "preemptClass": "RUNONCE"},
    "resultContainerMountPoint": "/result",
    "workspaceMounts": [],
    "datasetMounts": [],
}


def parse_all(cfg):
    cfg.user = cfg.user or os.getlogin()
    user = cfg.user

    if cfg.img is not None:
        job_cfg["dockerImageName"] = cfg.img
    if cfg.name is not None:
        job_cfg["name"] = f"ml-model.ngcpp_{user}." + cfg.name
    else:
        job_cfg[
            "name"
        ] = f"ml-model.ngcpp_{user}.{cfg.nnode}node-{time.strftime('%Y%m%d_%H%M%S')}"
    parse_device(cfg)
    parse_cmd(cfg)
    parse_ws(cfg)
    parse_dataset(cfg)


def parse_device(cfg):
    cluster_name = ALIAS_TO_CLUSTER[str(cfg.ngc)]
    cluster = CLUSTER_SETTING[cluster_name]
    num_node = cfg.nnode
    gpu_per_node = cfg.ngpu
    if num_node > 1 and gpu_per_node != 8:
        raise ValueError(f"Multinode job demands 8 gpus per node, got {gpu_per_node}")
    job_cfg["aceInstance"] = f"{cluster.device}.{cluster.memory}g.{gpu_per_node}.norm"
    job_cfg["minAvailability"] = job_cfg["replicaCount"] = num_node

    job_cmd.append(
        f"--team {cluster.team} --ace {cluster.ace} --label _wl___computer_vision --label "
        "subacct___nvr_nvr_picasso --priority HIGH --order 1 --preempt RUNONCE"
    )

    cfg.ace = cluster.ace


def parse_cmd(cfg: DictConfig) -> None:
    """
    Parses the given configuration to generate a list of commands. The generated
    commands are then joined into a single string command separated by semicolons
    and stored in the global 'job_cfg' dictionary under the 'command' key.

    Parameters:
        cfg (object): Configuration object with attributes:
            - jupyter (bool): If True, adds the jupyter lab command to the commands list.
            - workdir (str): Directory path to change to before running other commands.
            - cmd (Union[str, List[str]]): Command or list of commands to run.
            - sleep (bool): If True, appends a sleep command to the commands list.

    Returns:
        None: Modifies the global 'job_cfg' dictionary in-place.
    """

    cmds = []

    # Append Jupyter lab command if required
    if cfg.jupyter:
        jupyter_cmd = (
            'tmux new-session -d -s jlab "jupyter lab --port 9999 --ip=0.0.0.0 '
            "--allow-root --no-browser --NotebookApp.token='' --notebook-dir=/ "
            "--NotebookApp.allow_origin='*' \""
        )
        cmds.append(jupyter_cmd)

    # Change to working directory if specified
    if cfg.workdir:
        cmds.append(f"cd {cfg.workdir}")

    # Append command(s) if provided
    if cfg.cmd:
        if isinstance(cfg.cmd, str):
            cmds.append(cfg.cmd)
        else:
            for item in cfg.cmd:
                cmds.append(item)

    # Append sleep command if required
    if cfg.sleep:
        cmds.append("sleep 7d")

    # Update the global job_cfg dictionary
    job_cfg["command"] = ";".join(cmds)


def parse_ws(cfg):
    # create ace specific workspace
    user, ace = cfg.user, cfg.ace
    id_list = [
        f"{user}_{ace}",
        f"{user}__{ace}",
    ]
    for ws_id in id_list:
        # Always try to create a new NGC workspace. If the workspace already exists, it won't create a new one.
        cmd = f"ngc workspace create --ace {ace} --name {ws_id}"
        result = run_command(cmd, max_retry_counter=1, is_raise=False)

        # Check for 'already exists' in the error message
        if "already exists" in result.stderr:
            break

    job_cfg["workspaceMounts"].append(
        {"containerMountPoint": "/root", "id": ws_id, "mountMode": "RW"}
    )

    if cfg.ws is not None:
        for _ws, target_loc in cfg.ws.items():
            job_cfg["workspaceMounts"].append(
                {"containerMountPoint": target_loc, "id": _ws, "mountMode": "RW"}
            )


def parse_dataset(cfg):
    if cfg.dataset is not None:
        for dataset_id, target_loc in cfg.dataset.items():
            job_cfg["datasetMounts"].append(
                {
                    "containerMountPoint": target_loc,
                    "id": dataset_id,
                }
            )


def read_local_cfg(cfg):
    cfg_path = hydra.utils.to_absolute_path(cfg.file)
    if not osp.exists(cfg_path):
        return cfg
    logger.info("readding config from: " + cfg_path)
    local_cfg = OmegaConf.load(cfg_path)
    cli_cfg = OmegaConf.from_cli()
    cfg = OmegaConf.merge(cfg, local_cfg, cli_cfg)
    return cfg


@hydra.main(config_path="conf", config_name="debug", version_base="1.1.0")
def main(cfg: DictConfig) -> None:
    OmegaConf.set_struct(cfg, False)
    cfg = read_local_cfg(cfg)
    parse_all(cfg)

    job_name = job_cfg["name"]
    json_fname = f"/tmp/{job_name}.json"
    os.makedirs(os.path.dirname(json_fname), exist_ok=True)
    with open(json_fname, "w", encoding="utf-8") as file:
        json.dump(job_cfg, file, indent=4)

    system_cmd = f"ngc batch run -f {json_fname} " + " ".join(job_cmd)
    logger.info(system_cmd)
    is_submit = cfg.submit
    if not is_submit and cfg.debug:
        is_submit = yes_or_no("submit job?", default="yes")
    if is_submit:
        result = run_command(system_cmd)

        if cfg.debug and cfg.exec:
            print(result.stdout)
            id_info = result.stdout.split("\n")[2]
            job_id = id_info.split(" ")[-1]
            logger.warning(f"ngc batch exec {job_id}")
            while True:
                rtn_value = os.system(f"ngc batch exec {job_id}")
                if rtn_value != 0:
                    logger.warning(
                        f"ERROR VALUE {rtn_value}: ngc batch exec {job_id} failed, retrying..."
                    )
                    time.sleep(5)
                else:
                    break


if __name__ == "__main__":
    main()  # pylint: disable=no-value-for-parameter
