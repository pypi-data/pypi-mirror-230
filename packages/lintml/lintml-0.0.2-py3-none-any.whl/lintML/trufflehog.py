from lintML.observation import Observation
import json
import docker
from pathlib import Path
from typing import List


def create_trufflehog_observation(finding):
    """
    Create an observation object based on a TruffleHog finding.

    Args:
        finding (Dict): A dictionary containing information about the finding.

    Returns:
        Observation: An observation object containing details about the finding.
    """
    return Observation(
        category="Verified Credential",
        source_file=finding["SourceMetadata"]["Data"]["Filesystem"]["file"],
        source_code=finding["Raw"],
        finder="TruffleHog",
        finder_rule=finding["DetectorName"],
    )


async def run_trufflehog(client: docker.DockerClient, dir: Path) -> List[Observation]:
    """
    Run Trufflehog analysis on a directory using a Docker container.

    Args:
        client (docker.DockerClient): Docker client for interacting with Docker.
        dir (Path): Path to the directory containing the code to be analyzed.

    Returns:
        List[Observation]: A list of observations generated by TruffleHog.

    Raises:
        Any exceptions raised by Docker operations, JSON decoding, or Observation creation.
    """
    container_bytes = client.containers.run(
        "trufflesecurity/trufflehog:latest",
        command="filesystem /pwd --json --only-verified",
        stdout=True,
        stderr=True,
        volumes={dir: {"bind": "/pwd", "mode": "ro"}},
    )
    container_str = container_bytes.decode("utf8")
    findings = container_str.split("\n")
    observations = [
        create_trufflehog_observation(json.loads(f))
        for f in findings
        if "SourceMetadata" in f
    ]
    return observations
