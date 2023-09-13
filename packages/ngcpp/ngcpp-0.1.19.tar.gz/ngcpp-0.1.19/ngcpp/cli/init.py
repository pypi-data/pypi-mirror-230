import os

import typer
from omegaconf import OmegaConf

app = typer.Typer()


@typer.run
def main():
    if not os.path.exists(".ngcpp"):
        os.makedirs(".ngcpp")
    init_cfg = {
        "pbss_account": "team-lpr-imagine",
        "ngc_path": None,
    }
    OmegaConf.save(OmegaConf.create(init_cfg), ".ngcpp/sync.yaml")
