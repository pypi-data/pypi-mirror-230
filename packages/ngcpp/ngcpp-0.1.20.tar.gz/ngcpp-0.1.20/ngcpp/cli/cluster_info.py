import typer

from ngcpp.cluster import ALIAS_TO_CLUSTER, Cluster

app = typer.Typer()

# pylint: disable=redefined-outer-name
@app.command()
def usage(
    alias: str = typer.Argument(
        "10",
        help="cluster alias, e.g. 10 for prd10, "
        "use alias command to list all available aliases",
    )
):
    """
    List user usage
    """
    cluster = Cluster(alias)
    cluster.report_user_usage()


@app.command()
def hang(
    alias: str = typer.Argument(
        "10",
        help="cluster alias, e.g. 10 for prd10, "
        "use alias command to list all available aliases",
    )
):
    """
    List all hanging jobs
    """
    cluster = Cluster(alias)
    cluster.report_hangs(verbose=True)


@app.command()
def alias():
    """
    List all available cluster aliases
    """
    for k, v in ALIAS_TO_CLUSTER.items():
        print(f"{k} : {v}")


@app.command()
def list(  # pylint: disable=redefined-builtin
    alias: str = typer.Argument(
        "10",
        help="cluster alias, e.g. 10 for prd10, "
        "use alias command to list all available aliases",
    )
):
    """
    List user jobs
    """
    cluster = Cluster(alias)
    df = cluster.jobs()
    del df["Team"]
    del df["Status Details"]
    df = df.sort_values(by=["Status", "Id"])
    print(df.to_string(index=False))


def main():
    app()
