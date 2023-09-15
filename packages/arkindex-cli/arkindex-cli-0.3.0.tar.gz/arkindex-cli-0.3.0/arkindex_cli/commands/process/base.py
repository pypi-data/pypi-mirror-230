# -*- coding: utf-8 -*-
from collections import Counter
from typing import Dict, Iterable, List, Optional, Union
from uuid import UUID

from apistar.exceptions import ErrorResponse
from arkindex import ArkindexClient
from rich.progress import Progress, track


def get_process(client: ArkindexClient, process_id: UUID) -> dict:
    try:
        return client.request("RetrieveProcess", id=process_id)
    except ErrorResponse as e:
        if e.status_code == 404:
            raise ValueError(f"Process {process_id} not found.") from e
        raise


def get_workflow(client: ArkindexClient, process: dict) -> dict:
    if not process["workflow"]:
        raise ValueError("This process does not have an associated workflow.")

    # Use the Requests session from the API client to have Arkindex authentication for arbitrary URLs
    resp = client.transport.session.get(process["workflow"])
    resp.raise_for_status()
    return resp.json()


def get_finished_tasks(workflow: dict, run: Optional[int] = None) -> Iterable[dict]:
    if run is None:
        run = max(task["run"] for task in workflow["tasks"])

    finished_tasks = [
        task
        for task in workflow["tasks"]
        if task["run"] == run and task["state"] in ("failed", "completed")
    ]

    if not finished_tasks:
        raise ValueError(
            f"This process' workflow does not have any finished tasks on run {run}"
        )

    return finished_tasks


def list_ml_report_urls(client: ArkindexClient, tasks: Iterable[dict]) -> List[str]:
    return [
        artifact["url"]
        for task in tasks
        for artifact in client.request("ListArtifacts", id=task["id"])
        if artifact["path"] == "ml_report.json"
    ]


def _ensure_transcriptions_int(transcriptions: Union[Dict[str, int], int]) -> int:
    """
    Ensures the older transcription count format that reported counts by type is converted to a single total count.
    {"transcriptions": {"word": 4, "paragraph": 2}} → {"transcriptions": 6}
    """
    if isinstance(transcriptions, dict):
        return sum(transcriptions.values())
    else:
        return transcriptions


class MLReport(dict):
    """
    A machine learning report (ml_report.json).

    Structure: {
      type: MLTool type,
      slug: MLTool slug,
      version: MLTool version,
      started: When the tool started,
      elements: {
        [Element ID]: {
          started: When processing started for this element,
          elements: Created element counts by element type slug (Dict[str, int]),
          transcriptions: Created transcriptions count,
          classifications: Created classification counts by class name,
          errors: [
            {
              class: Exception class name,
              message: Error message,
              status_code: HTTP status code (only for APIStar ErrorResponse),
              content: HTTP response content (only for APIStar ErrorResponse),
              traceback: Exception traceback as a string (optional)
            }
          ]
        }
      }
    }
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setdefault("elements", {})

    @classmethod
    def from_url(cls, client: ArkindexClient, url: str) -> "MLReport":
        # Use the Requests session from the API client to have Arkindex authentication for arbitrary URLs
        resp = client.transport.session.get(url)
        resp.raise_for_status()
        return cls(resp.json())

    @property
    def failed_elements(self) -> Dict[str, dict]:
        return {
            element_id: data
            for element_id, data in self["elements"].items()
            if data["errors"]
        }

    @property
    def errors_by_class(self) -> Dict[str, int]:
        return Counter(
            [
                error["class"]
                for element in self.failed_elements.values()
                for error in element["errors"]
            ]
        )

    def merge_elements(self, report: "MLReport") -> None:
        for element_id, data in report["elements"].items():
            if element_id not in self["elements"]:
                self["elements"][element_id] = data
                continue

            existing_data = self["elements"][element_id]
            merged_data = {"errors": existing_data["errors"] + data["errors"]}

            # Use the earliest start date; we can compare strings since they use ISO 8601
            if existing_data["started"] > data["started"]:
                merged_data["started"] = data["started"]
            else:
                merged_data["started"] = existing_data["started"]

            # Merge all counts
            merged_data["elements"] = Counter(existing_data["elements"])
            merged_data["elements"].update(data["elements"])
            merged_data["classifications"] = Counter(existing_data["classifications"])
            merged_data["classifications"].update(data["classifications"])
            merged_data["transcriptions"] = _ensure_transcriptions_int(
                existing_data["transcriptions"]
            ) + _ensure_transcriptions_int(data["transcriptions"])

            self["elements"][element_id] = merged_data


def get_global_report(
    client: ArkindexClient, process_id: UUID, run: Optional[int] = None
) -> List[MLReport]:
    """
    Retrieve all ML reports on a single run of a process with CLI progress bars
    """
    with Progress(transient=True) as progress:
        progress.add_task(start=False, description="Fetching process")

        process = get_process(client, process_id)
        workflow = get_workflow(client, process)

    # There are no artifacts on unfinished tasks; ignore them
    finished_tasks = get_finished_tasks(workflow, run)

    tasks_progress = track(
        finished_tasks, description="Listing artifacts", transient=True
    )
    try:
        artifact_urls = list_ml_report_urls(client, tasks_progress)
    finally:
        # When an error occurs in list_ml_report_urls, we need to make sure that the
        # generator returned by track() is closed.  Otherwise, the thread spawned to
        # give progress updates to the user will remain indefinitely running and the
        # program is stuck waiting for the thread to end after its main thread ends.
        tasks_progress.close()

    if not artifact_urls:
        raise ValueError(
            f"Run {run} on this process does not have ml_report.json artifacts"
        )

    ml_report = MLReport()
    for url in track(artifact_urls, description="Downloading reports", transient=True):
        ml_report.merge_elements(MLReport.from_url(client, url))
    return ml_report
