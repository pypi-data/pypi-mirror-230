from io import BytesIO
from typing import List, Optional

from rhino_health.lib.endpoints.aimodel.aimodel_dataclass import AIModelRunInferenceAsyncResponse
from rhino_health.lib.endpoints.endpoint import Endpoint
from rhino_health.lib.endpoints.model_result.model_result_dataclass import ModelResult
from rhino_health.lib.utils import rhino_error_wrapper


class ModelResultEndpoints(Endpoint):
    @property
    def model_result_data_class(self):
        """
        @autoapi False
        """
        return ModelResult

    @rhino_error_wrapper
    def halt_model_run(self, model_action_uid: str):
        """
        Send a halting request to a running aimodel.

        This triggers the halting process but does not wait for halting to complete.

        If triggering the halting process fails, a message specifying the error is returned.

        Parameters
        ----------
        model_action_uid: str
            UID of the ModelResult representing the aimodel run to halt.

        Returns
        -------
        json response in the format of:
          "status": the request's status code -
                - 200: valid request, halting innitiated.
                - 400: invalid request, the model can not be halted, or does not exist.
                - 500: error while initiating halting.
          "data":  message specifying if the halting was initiated or failed. In case the request failed,
           the error message is also displayed.

        Examples
        --------
        >>> session.model_result.halt_model_run(model_action_uid)

        """
        result = self.session.get(f"/federatedmodelactions/{model_action_uid}/halt")
        return result

    @rhino_error_wrapper
    def run_inference(
        self,
        model_action_uid: str,
        validation_cohort_uids: List[str],
        validation_cohorts_suffix: str,
        timeout_seconds: int,
    ):
        """
        Trigger running inference on one or more cohorts using a previously trained model.

        Parameters
        ----------
        model_action_uid: str
            UID for the model action
        validation_cohort_uids: List[str]
            List of cohort UIDs to run inference on
        validation_cohorts_suffix: str
            Suffix for the validation cohorts
        timeout_seconds: int
            Timeout in seconds


        Returns
        -------
        AIModelRunAsyncResponse()

        Examples
        --------
        >>> s = session.model_result.run_inference(model_action_uid, validation_cohort_uids, validation_cohorts_suffix, timeout_seconds)
        >>> s.model_result() # Get the asynchronous result
        >>> s.federated_model_action_uid # Get the model result UID
        See Also
        --------
        rhino_health.lib.endpoints.aimodel.aimodel_dataclass.AIModelTrainAsyncResponse : AIModelTrainAsyncResponse Dataclass
        """
        data = {
            "validation_cohort_uids": validation_cohort_uids,
            "validation_cohorts_inference_suffix": validation_cohorts_suffix,
            "timeout_seconds": timeout_seconds,
        }

        res = self.session.post(
            f"/federatedmodelactions/{model_action_uid}/run_inference",
            data=data,
            adapter_kwargs={"data_as_json": True},
        )
        print(res.raw_response.content)
        return res.to_dataclass(AIModelRunInferenceAsyncResponse)


class ModelResultFutureEndpoints(ModelResultEndpoints):
    @rhino_error_wrapper
    def get_model_result(self, model_result_uid: str):
        """
        Returns a ModelResult dataclass

        Parameters
        ----------
        model_result_uid: str
            UID for the ModelResult

        Returns
        -------
        model_result: ModelResult
            ModelResult dataclass

        Examples
        --------
        >>> session.aimodel.get_model_result(model_result_uid)
        ModelResult()
        """
        result = self.session.get(f"/federatedmodelactions/{model_result_uid}")
        return result.to_dataclass(self.model_result_data_class)

    @rhino_error_wrapper
    def get_model_params(
        self, model_result_uid: str, model_weights_files: Optional[List[str]] = None
    ) -> BytesIO:
        """
        Returns the contents of one or more model params file(s) associated with a model result.

        The return value is an open binary file-like object, which can be read or written to a file.

        The contents are for a single file. This is either the model params file if there was only one
        available or selected, or a Zip file containing multiple model params files.

        Parameters
        ----------
        model_result_uid: str
            UID for the ModelResult
        model_weights_files: List(str)
            List of paths within S3 of model weight files to download. If multiple files are supplied, download
            as zip. If the argument is not specified, download all model weight files found for the given model action.

        Returns
        -------
        model_params: BytesIO
            A Python BytesIO Buffer

        Examples
        --------
        >>> with open("my_output_file.out", "wb") as output_file:
        >>>     model_params_buffer = session.model_result.get_model_params(model_result_uid, model_weights_files)
        >>>     output_file.write(model_params_buffer.getbuffer())
        """
        result = self.session.get(
            f"/federatedmodelactions/{model_result_uid}/download_model_params",
            params={"model_weights_files": model_weights_files},
        )
        return BytesIO(result.raw_response.content)

    # @rhino_error_wrapper
    # def __logs(self, model_result_uid: str):
    #     """
    #     @autoapi False
    #
    #     .. warning:: This feature is under development and the interface may change
    #     """
    #     result = self.session.get(
    #         f"/federatedmodelactions/{model_result_uid}/logs"
    #     )
    #     return result["logs"]
