import json
import os
import socket

import hydra
from loguru import logger as logging
from omegaconf import DictConfig, OmegaConf

from ngcpp.utils import run_batch_commands, run_command

# the app rync local codebase to aws s3
# meanwhile, it generate a script to sync from s3 to ngc cluster machine

INCLUDE_EXTS = ["py", "sh", "secret", "yaml", "yml", "json", "txt", "md", "txt.gz"]


def read_local_cfg(cfg):
    cfg_path = cfg.file
    if not os.path.exists(cfg_path):
        return cfg
    logging.info("readding config from: " + cfg_path)
    local_cfg = OmegaConf.load(cfg_path)
    cli_cfg = OmegaConf.from_cli()
    cfg = OmegaConf.merge(cfg, local_cfg, cli_cfg)
    return cfg


@hydra.main(config_path="conf", config_name="sync", version_base="1.1.0")
def main(cfg: DictConfig) -> None:
    OmegaConf.set_struct(cfg, False)
    cfg = read_local_cfg(cfg)
    # TODO: a better way do this?
    # Check if `aws s3 ls` with the profile works
    _ = run_command(f"aws s3 ls --profile {cfg.pbss_account}")

    # Check if the secret file exists
    secret_path = f"scripts/s3/{cfg.pbss_account}.secret"
    if not os.path.exists(secret_path):
        raise AssertionError(
            f'Missing secret file at "{secret_path}". Ensure the file is present.'
        )

    ngcpp_root = ".ngcpp"
    if not os.path.exists(ngcpp_root):
        os.mkdir(ngcpp_root)
    # use user name and current path relative to home to generate a unique name
    pbss_snapshot_path = os.path.join(
        "s3://",
        "code_snapshots",
        os.getlogin(),
        socket.gethostname(),
        os.path.relpath(os.getcwd(), os.path.expanduser("~")),
    )

    snapshot_temp = f"{ngcpp_root}/snapshot"
    rsync_base_cmd = "rsync -arzh --prune-empty-dirs --no-links"
    include_code_exts = " ".join(f"--include=*.{ext}" for ext in INCLUDE_EXTS)

    aws_sync_base_cmd = "aws s3 sync --exact-timestamps --quiet"
    logging.info("Snapshotting the codebase to PBSS...")
    rsync_cmds = [
        f"{rsync_base_cmd} --include=*/ {include_code_exts} --exclude=* imaginaire projects scripts "
        + f"third_party {snapshot_temp}/ --delete",
        f"{rsync_base_cmd} --include=*.py --exclude=* . {snapshot_temp}/ --delete",
    ]
    # Sync from /tmp copy to PBSS.
    rsync_cmds.append(
        f"{aws_sync_base_cmd} {snapshot_temp} {pbss_snapshot_path} --delete "
        f"--profile {cfg.pbss_account}"
    )
    run_batch_commands(rsync_cmds)
    with open(f"{snapshot_temp}/ngc_local_sync.sh", "w", encoding="utf-8") as file:
        for cmd in rsync_cmds:
            file.write(f"{cmd}\n")
    logging.debug(
        f"Writing sync script to {os.path.join(os.getcwd(), snapshot_temp)}/ngc_local_sync.sh"
    )

    # generate a script to sync from s3 to ngc cluster machine
    sync_cmd = []
    with open(f"scripts/s3/{cfg.pbss_account}.secret", encoding="utf-8") as fin:
        credentials = json.load(fin)
    sync_cmd.append("rm -rf ~/.aws")
    sync_cmd.append("mkdir ~/.aws")
    sync_cmd.append("aws configure set plugins.endpoint awscli_plugin_endpoint")
    sync_cmd.append(
        f"aws configure set aws_access_key_id {credentials['aws_access_key_id']}"
    )
    sync_cmd.append(
        f"aws configure set aws_secret_access_key {credentials['aws_secret_access_key']}"
    )
    sync_cmd.append(f"aws configure set region {credentials['region_name']}")
    sync_cmd.append(f"aws configure set s3.endpoint_url {credentials['endpoint_url']}")
    sync_cmd.append("aws configure set s3.signature_version s3v4")
    sync_cmd.append("aws configure set s3.payload_signing_enabled true")
    sync_cmd.append(
        f"aws configure set s3api.endpoint_url {credentials['endpoint_url']}"
    )
    sync_cmd.append("aws configure set s3api.payload_signing_enabled true")
    ngc_path = getattr(cfg, "ngc_path", None)
    if not ngc_path:
        ngc_path = os.path.join(
            "/root", os.path.relpath(os.getcwd(), os.path.expanduser("~"))
        )
    sync_cmd.append(
        f"aws s3 sync {pbss_snapshot_path} {ngc_path} --exact-timestamps --quiet"
    )
    sync_cmd.append(f"cd {ngc_path}")
    with open(f"{snapshot_temp}/ngc_remote_sync.sh", "w", encoding="utf-8") as file:
        for cmd in sync_cmd:
            file.write(f"{cmd}\n")
    logging.debug(
        f"Writing sync script to {os.path.join(os.getcwd(), snapshot_temp)}/ngc_remote_sync.sh"
    )
