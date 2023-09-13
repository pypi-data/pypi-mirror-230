import warnings

import pkg_resources
import requests


def check_version(package_name):
    # Get the installed version of the package
    installed_version = pkg_resources.get_distribution(package_name).version

    # Fetch the latest version from PyPI
    response = requests.get(f"https://pypi.org/pypi/{package_name}/json", timeout=10)
    latest_version = response.json()["info"]["version"]

    # Compare the versions and raise a warning if the installed version is out-of-date
    if pkg_resources.parse_version(installed_version) < pkg_resources.parse_version(
        latest_version
    ):
        print("--------------------------------------------------")
        print(f"Installed {package_name} version: {installed_version}")
        print(f"Latest {package_name} version: {latest_version}")
        warnings.warn(
            "Out-of-date version! Please consider upgrading to the latest version."
        )
        print("--------------------------------------------------")


check_version("ngcpp")
