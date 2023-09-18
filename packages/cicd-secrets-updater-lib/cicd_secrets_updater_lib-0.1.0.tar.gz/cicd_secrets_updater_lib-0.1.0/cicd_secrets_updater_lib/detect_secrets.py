import contextlib
import os
import subprocess

from .utilities import execute_command


def get_detect_secrets_version():
    """
    Obtain the version of detect-secrets
    :return: The version of detect-secrets
    """

    with contextlib.suppress(subprocess.CalledProcessError):
        version = subprocess.check_output(
            ["detect-secrets", "--version"],
            stderr=subprocess.STDOUT,
            universal_newlines=True
        )

    # If version is empty, return None
    if not version:
        return None

    # If version contains
    # WARNING: You are running an outdated version of detect-secrets.
    #  Your version: 0.13.1+ibm.58.dss
    #  Latest version: 0.13.1+ibm.61.dss
    #  See upgrade guide at https://ibm.biz/detect-secrets-how-to-upgrade
    # 0.13.1+ibm.58.dss
    # obtain only '0.13.1+ibm.58.dss'
    if "WARNING: You are running an outdated version of detect-secrets" in version:
        version = version.split("\n")[5]

    return version.strip()


def delete_secrets_baseline(repositories_path, repo):
    """
    Delete the secrets baseline file
    :param repositories_path: The path to the where the repositories are cloned
    :param repo: The repository
    :return: The path to the secrets baseline file
    """

    secrets_baseline_path = f'{repositories_path}/{repo.name}/.secrets.baseline'

    if os.path.isfile(secrets_baseline_path):
        os.remove(secrets_baseline_path)

    return secrets_baseline_path


def update_secrets_scan(repository_path):
    """
    Update the .secrets.baseline file
    :param repository_path: The path to the repository
    """

    execute_command(f"cd {repository_path} && detect-secrets scan --update .secrets.baseline")


def audit_secrets(repository_path):
    """
    Audit the .secrets.baseline file
    :param repository_path: The path to the repository
    """

    execute_command(f"cd {repository_path} && yes 'n' | detect-secrets audit .secrets.baseline")
