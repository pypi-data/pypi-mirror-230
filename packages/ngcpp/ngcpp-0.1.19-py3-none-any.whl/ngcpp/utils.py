import subprocess
from concurrent.futures import ThreadPoolExecutor
from typing import List, Optional

import pandas as pd
from loguru import logger as logging

LOG_FORMAT = (
    "[<green>{time:MM-DD HH:mm:ss}</green>|"
    "<red>{process.name}</red>|"
    "<level>{level: <8}</level>|"
    "<cyan>{file.path}</cyan>:<cyan>{line}</cyan>:<cyan>{function}</cyan>]"
    "<level>{message}</level>"
)


def run_command(
    cmd: str, max_retry_counter: int = 3, is_raise: bool = True
) -> subprocess.CompletedProcess:
    """
    Runs a shell command with the ability to retry upon failure.

    Parameters:
    - cmd (str): The shell command to run.
    - max_retry_counter (int): Maximum number of retries if the command fails.
    - is_raise (bool): Whether to raise an exception and exit the program if the command fails after all retries.

    Returns:
    - subprocess.CompletedProcess: The result of the command execution.
    """

    retry_counter = 0
    while retry_counter < max_retry_counter:
        try:
            result = subprocess.run(
                cmd, shell=True, capture_output=True, text=True, check=False
            )

            # Check if the command was successful (returncode = 0)
            if result.returncode == 0:
                return result

            retry_counter += 1
            logging.debug(
                f"Retry {retry_counter}/{max_retry_counter}: Command '{cmd}' failed with error"
                f" code {result.returncode}. Error message: {result.stderr.strip()}"
            )

        except Exception as e:  # pylint: disable=broad-except
            retry_counter += 1
            logging.debug(
                f"Retry {retry_counter}/{max_retry_counter}: Command '{cmd}' raised an exception: {e}"
            )

    # If reached here, all retries have failed
    error_message = (
        f"Command '{cmd}' failed after {max_retry_counter} retries. Error code: {result.returncode}. "
        f"Error message: {result.stderr.strip()}"
    )
    if is_raise:
        raise RuntimeError(error_message)

    logging.critical(error_message)
    return result


def run_batch_commands(
    cmds: List[str],
    max_workers: Optional[int] = None,
    max_retry_counter: int = 3,
    is_raise: bool = True,
) -> List[subprocess.CompletedProcess]:
    """
    This function runs a batch of commands in parallel.

    Parameters:
    - cmds (List[str]): List of shell commands to run.
    - max_workers (Optional[int]): Maximum number of concurrent workers. \
    None means the number of workers is the number of CPUs.
    - max_retry_counter (int): Maximum number of retries if a command fails.
    - is_raise (bool): Whether to raise an exception and exit the program if a command fails after all retries.

    Returns:
    - List[subprocess.CompletedProcess]: List of results of the command executions.
    """

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = executor.map(
            lambda cmd: run_command(cmd, max_retry_counter, is_raise), cmds
        )
    return list(results)


def parse_duration(duration):
    if pd.isnull(duration) or duration == "-":
        return 0
    if "day" in duration:
        days, time = duration.split(", ")
        days = int(days.split(" ")[0])
        hours, minutes, seconds = map(int, time.split(":"))
        total_seconds = days * 24 * 3600 + hours * 3600 + minutes * 60 + seconds
    else:
        hours, minutes, seconds = map(int, duration.split(":"))
        total_seconds = hours * 3600 + minutes * 60 + seconds
    return total_seconds / 3600
