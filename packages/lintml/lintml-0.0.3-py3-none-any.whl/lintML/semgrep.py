from lintML.observation import Observation
import json
from tempfile import TemporaryDirectory
from lintML.ipynb_convert import get_ipynb_code
from pathlib import Path
import docker
from typing import List, Dict


def create_semgrep_observation(finding: Dict) -> Observation:
    """
    Create an observation object based on a Semgrep finding.

    Args:
        finding (Dict): A dictionary containing information about the finding.

    Returns:
        Observation: An observation object containing details about the finding.

    Note:
        - The `finding` dictionary is expected to have specific keys and values as shown in the example.
    """
    return Observation(
        category=finding["extra"]["metadata"]["vulnerability_class"][0],
        source_file=finding["path"],
        source_code=finding["extra"]["lines"],
        finder="Semgrep",
        finder_rule=finding["check_id"],
    )


async def semgrep_prep(dir: Path) -> TemporaryDirectory:
    """
    Convert .ipynb files to .py in a temporary directory for semgrep analysis

    Args:
        dir (Path): The directory containing the code to be analyzed.

    Returns:
        TemporaryDirectory: A temporary directory containing the code converted to Python.

    Raises:
        Any exceptions raised during the preparation process.
    """
    tmpdir = TemporaryDirectory(dir=dir, ignore_cleanup_errors=True)
    ipynb_files = dir.rglob("*.ipynb")
    await get_ipynb_code(ipynb_files, tmpdir)
    return tmpdir


async def run_semgrep(client: docker.DockerClient, dir: Path) -> List[Observation]:
    """
    Run Semgrep analysis on a directory using a Docker container.

    Args:
        client (docker.DockerClient): Docker client for interacting with Docker.
        dir (Path): Path to the directory containing the code to be analyzed.

    Returns:
        List[Observation]: A list of observations generated by Semgrep analysis.

    Raises:
        Any exceptions raised by Docker operations, JSON decoding, or Observation creation.
    """
    tmpdir = await semgrep_prep(dir)
    rule_root = "https://raw.githubusercontent.com/JosephTLucas/lintML/main/lintML/semgrep_rules/ready/"
    rules = ["",
             "huggingface-remote-code.yaml",
             'pickles.yaml',
             "sg_shelve.yaml",
             "tob_pickles-in-numpy.yaml",
             "tob_pickles-in-pandas.yaml",
             "tob_pickles-in-pytorch.yaml",
             "tob_scikit-joblib-load.yaml"]
    config = f" --config {rule_root}".join(rules)
    try:
        container_bytes = client.containers.run(
            "returntocorp/semgrep:latest",
            command=f"semgrep{config} --json /pwd --metrics=off -q",
            stdout=True,
            stderr=True,
            volumes={
                dir: {"bind": "/pwd", "mode": "ro"},
            },
        )
        container_str = container_bytes.decode("utf8")
        container_json = json.loads(container_str)
        observations = [
            create_semgrep_observation(f) for f in container_json["results"]
        ]
    finally:
        tmpdir.cleanup()
    return observations
