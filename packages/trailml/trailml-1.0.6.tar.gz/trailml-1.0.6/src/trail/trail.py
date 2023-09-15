import base64
import os.path
import signal
import sys
from collections import defaultdict
import time
from typing import Union

import mlflow
from gql import Client, gql
from gql.transport.aiohttp import AIOHTTPTransport
from gql.transport.exceptions import TransportQueryError
from mlflow.entities import Run
from mlflow.tracking import MlflowClient

from .libconfig import libconfig, is_development_environment
from .userconfig import userconfig
from .utils.auth import retrieve_jwt_token
from .utils.uploads import upload_folder


class Trail:
    ADD_EXPERIMENT_MUTATION = """
        mutation (
            $projectId: String!,
            $parentExperimentId: String!,
            $title: String!,
            $comments: String!,
            $instanceRunParameters: GenericScalar!,
            $instanceRunMetrics: GenericScalar!,
            $instanceRunComplete: Boolean!
            $hypothesis: String,
            $metricsHistoryEntries: [MetricsHistoryInput],
            $gitCommitHash: String
        ) {
            addExperiment(
                projectId: $projectId,
                parentExperimentId: $parentExperimentId,
                title: $title,
                comments: $comments,
                hypothesis: $hypothesis
                metricsHistory: $metricsHistoryEntries
                gitCommitHash: $gitCommitHash
                instanceRuns: {
                    comment: "",
                    parameters: $instanceRunParameters,
                    metrics: $instanceRunMetrics,
                    isComplete: $instanceRunComplete
                }
            ) {
                experiment {
                    id
                    title
                    comments
                    instanceRuns {
                        id
                        comment
                        parameters
                        metrics
                        isComplete
                    }
                }
            }
        }
    """

    PUT_ARTIFACT_MUTATION = """
        mutation (
            $experimentId: String!,
            $name: String!,
            $base64Data: String!,
            $tags: [String!]
        ) {
            putArtifact(
                experimentId: $experimentId,
                name: $name,
                base64Data: $base64Data,
                tags: $tags,
            ) {
                artifact {
                    id
                    name
                    contentType
                    size
                    tags
                }
            }
        }
    """

    SET_UPLOAD_INFORMATION = """
        mutation (
            $projectId: String!
        ) {
            updateProject(
                projectId: $projectId,
                uploadInformation: {
                isUploaded: true
            }) {
                id
                success
            }
        }
    """

    YDATA_PROFILING_TAG = "TRAIL_YDATA_DATASET_PROFILE"

    def __init__(
        self,
        experiment_title="Unnamed Run",
        parent_experiment_id=None,
        project_id=None,
        username=None,
        password=None,
    ):
        userconfig.merge(
            username=username,
            password=password,
            project_id=project_id,
            parent_experiment_id=parent_experiment_id,
        )

        self.project_config = userconfig.project()
        self.project_id = self.project_config.id
        self.parent_experiment_id = self.project_config.parent_experiment_id
        self.experiment_title = experiment_title
        self.artifacts = []
        self.default_handler = signal.getsignal(signal.SIGINT)
        self.is_complete = True
        self.hypothesis = ""

        self._client = None
        self._last_client_creation_time = 0

    def signal_handler(self, signum, frame):
        self.is_complete = False
        print("Latest run is logged.")
        raise KeyboardInterrupt()

    def __enter__(self):
        if mlflow.active_run() is None:
            raise Exception("No active mlflow run found!")
        signal.signal(signal.SIGINT, self.signal_handler)  # type: ignore
        return self

    def __exit__(self, exception_type, exception_value, exception_traceback):
        run = mlflow.active_run()
        if run is None:
            raise Exception("No active mlflow run found!")

        # we fetch the run like this because of
        # https://mlflow.org/docs/latest/python_api/mlflow.html#mlflow.active_run
        materialized_run = mlflow.get_run(run_id=run.info.run_id)

        if materialized_run:
            self._log_experiment(materialized_run)
            self._upload_artifacts(materialized_run)
        signal.signal(signal.SIGINT, self.default_handler)

    @property
    def client(self):
        current_time = time.time()
        if (
            not self._client or current_time - self._last_client_creation_time > 60 * 59
        ):  # firebase token experies after 1 hour
            token = retrieve_jwt_token(
                email=userconfig.username, password=userconfig.password
            )
            transport = AIOHTTPTransport(
                libconfig.GQL_ENDPOINT_URL, headers={"authorization": f"Bearer {token}"}
            )
            self._last_client_creation_time = current_time
            return Client(transport=transport)
        else:
            return self._client

    def put_dataset_analysis(self, src: str, name: str):
        """
        Wrapper function for put_artifact that sets specific tags to mark
        the artifact as dataset profiling analysis.
        """
        self.put_artifact(src, name, [self.YDATA_PROFILING_TAG])

    def put_artifact(
        self, src: Union[str, bytes], name: str, tags: Union[str, list, None]
    ):
        """Queues an artifact for upload to Trail.
        The artifact is uploaded when leaving the `with Trail` block.
        The `src` parameter can be either a string or a bytes object. In case
        of a string, it is assumed to be a path to a file. In case of a bytes
        object, it is assumed to be the raw data of the artifact.

        :param src: The artifact path or bytes to upload
        :param name: The name of the artifact
        :param tags: A single tag or a list of tags
        """

        if isinstance(src, str):
            with open(src, "rb") as f:
                data = f.read()
        elif isinstance(src, bytes):
            data = src
        else:
            raise ValueError("Artifact source must be of type string or bytes")

        if not tags:
            tags = []
        elif isinstance(tags, str):
            tags = [tags]

        self.artifacts.append(
            (
                data,
                name,
                tags,
            )
        )

    def _execute_client(
        self, document: str, variable_values: dict, error_message: str | None
    ):
        try:
            self.client.execute(
                document=gql(document),
                variable_values=variable_values,
            )
        except TransportQueryError as e:
            if is_development_environment():
                print(e)

            if error_message:
                print(error_message, file=sys.stderr)

    def _upload_artifact(self, data: bytes, name: str, tags: list):
        self._execute_client(
            document=self.PUT_ARTIFACT_MUTATION,
            variable_values={
                "experimentId": self.parent_experiment_id,
                "name": name,
                "base64Data": base64.b64encode(data).decode(),
                "tags": tags,
            },
            error_message="Error uploading experiment artifacts to Trail. Please contact"
            " us if the problem persists.",
        )

    def _set_upload_information(self) -> None:
        self._execute_client(
            document=self.SET_UPLOAD_INFORMATION,
            variable_values={
                "projectId": self.project_id,
            },
            error_message=None,
        )

    def upload_folder(self, local_folder: str, abs_path: str, expiration_seconds=300):
        success = upload_folder(local_folder, abs_path, expiration_seconds)
        if success:
            self._set_upload_information()

    def put_hypothesis(self, hypothesis: str):
        self.hypothesis = hypothesis

    def _log_experiment(self, run: Run):
        run_id = run.info.run_id
        tags = {k: v for k, v in run.data.tags.items() if not k.startswith("mlflow.")}
        mlflow_artifacts = [
            artifact.path for artifact in MlflowClient().list_artifacts(run_id, "model")
        ]
        d = {  # noqa: F841
            "run_id": run_id,
            "timestamp": run.info.start_time / 1000.0,
            "user": run.info.user_id,
            "artifacts": mlflow_artifacts,
            "tags": tags,
        }
        # Convert numeric parameter values to their respective types
        converted_params = run.data.params.copy()
        for key, value in converted_params.items():
            try:
                converted_params[key] = float(value)
            except ValueError:
                pass

        try:
            result = self.client.execute(
                document=gql(self.ADD_EXPERIMENT_MUTATION),
                variable_values={
                    "projectId": self.project_id,
                    "parentExperimentId": self.parent_experiment_id,
                    "title": self.experiment_title,
                    "comments": "",
                    "instanceRunParameters": converted_params,
                    "instanceRunMetrics": run.data.metrics,
                    "instanceRunComplete": self.is_complete,
                    "hypothesis": self.hypothesis,
                    "gitCommitHash": run.data.tags.get("mlflow.source.git.commit", ""),
                    "metricsHistoryEntries": self.get_metric_history_data(
                        run_id=run_id
                    ),
                },
            )

            experiment_id = result["addExperiment"]["experiment"]["id"]
            self.project_config.update_parent_experiment_id(experiment_id)
            self.parent_experiment_id = experiment_id
        except TransportQueryError as e:
            if is_development_environment():
                print(e)

            print(
                "Error uploading experiment data to Trail. Please contact us "
                "if the problem persists.",
                file=sys.stderr,
            )

    def _upload_artifacts(self, run: Run):
        run_id = run.info.run_id

        # upload cached artifacts
        mlflow_artifacts = MlflowClient().list_artifacts(run_id, "model")
        for artifact in mlflow_artifacts:
            path = artifact.path
            with open(path, "rb") as f:
                self._upload_artifact(
                    data=f.read(),
                    name=os.path.basename(path),
                    tags=["mlflow"],
                )

        for artifact in self.artifacts:
            data, name, tags = artifact
            self._upload_artifact(
                data=data,
                name=name,
                tags=tags,
            )

    def get_metric_history_data(self, run_id):
        client = mlflow.tracking.MlflowClient()
        run = mlflow.active_run()
        mlflowrun = mlflow.get_run(run_id=run.info.run_id)  # type: ignore
        metric_list = list(mlflowrun.data.metrics.keys())
        metrics = defaultdict(list)
        for metric in metric_list:
            metric_history = client.get_metric_history(run_id, metric)
            for entry in metric_history:
                metric_name = entry.key
                data_point = {
                    "value": entry.value,
                    "timeStamp": str(entry.timestamp),
                    "step": entry.step,
                }
                metrics[metric_name].append(data_point)

        metrics_history = []
        for metric in metrics:
            metrics_history.append({"metricName": metric, "history": metrics[metric]})

        return metrics_history
