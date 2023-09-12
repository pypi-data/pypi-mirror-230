from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass
import logging
from typing import List, Optional, Sequence

import pandas as pd

from truera.client.public.auth_details import AuthDetails
from truera.client.public.communicator.query_service_http_communicator import \
    HttpQueryServiceCommunicator
from truera.client.util.data.row_major_value_table_util import \
    RowMajorValueTableUtil
from truera.protobuf.public.aiq.accuracy_pb2 import \
    AccuracyType  # pylint: disable=no-name-in-module
from truera.protobuf.public.aiq.intelligence_service_pb2 import \
    BiasType  # pylint: disable=no-name-in-module
import truera.protobuf.public.common_pb2 as common_pb
from truera.protobuf.public.qoi_pb2 import \
    QuantityOfInterest  # pylint: disable=no-name-in-module
from truera.protobuf.queryservice import query_service_pb2 as qs_pb
from truera.utils.data_constants import NORMALIZED_EMBEDDINGS_COLUMN_NAME
from truera.utils.data_constants import NORMALIZED_ID_COLUMN_NAME
from truera.utils.data_constants import NORMALIZED_LABEL_COLUMN_NAME
from truera.utils.data_constants import NORMALIZED_PREDICTION_COLUMN_NAME
from truera.utils.data_constants import NORMALIZED_RANKING_GROUP_ID_COLUMN_NAME
from truera.utils.data_constants import NORMALIZED_RANKING_ITEM_ID_COLUMN_NAME
from truera.utils.data_constants import NORMALIZED_TIMESTAMP_COLUMN_NAME
from truera.utils.data_constants import NORMALIZED_TOKENS_COLUMN_NAME
from truera.utils.data_constants import SYSTEM_COLUMNS
from truera.utils.truera_status import TruEraInternalError
from truera.utils.truera_status import TruEraNotFoundError

TRUERA_SPLIT_ID_COL = "__truera_split_id__"


@dataclass
class BatchDataSummaryResults:

    @dataclass
    class BatchDataSummaryResult:
        df: pd.DataFrame
        error: qs_pb.QueryItemResult.QueryError

    entries: List[BatchDataSummaryResult]


class QueryServiceClient(object):

    def __init__(
        self,
        connection_string: str,
        auth_details: AuthDetails = None,
        use_http: bool = False,
        logger=None
    ):
        if not use_http:
            from truera.client.private.communicator.query_service_grpc_communicator import \
                GrpcQueryServiceCommunicator
        self.communicator = HttpQueryServiceCommunicator(
            connection_string, auth_details, logger
        ) if use_http else GrpcQueryServiceCommunicator(
            connection_string, auth_details, logger
        )
        self.logger = logger or logging.getLogger(__name__)
        self._include_sys_cols = [
            NORMALIZED_ID_COLUMN_NAME, NORMALIZED_TIMESTAMP_COLUMN_NAME,
            NORMALIZED_RANKING_GROUP_ID_COLUMN_NAME,
            NORMALIZED_RANKING_ITEM_ID_COLUMN_NAME
        ]

    def echo(self, request_id: str, message: str) -> qs_pb.EchoResponse:
        self.logger.info(
            f"QueryServiceClient::echo request_id={request_id}, message={message}"
        )
        request = qs_pb.EchoRequest(request_id=request_id, message=message)
        response = self.communicator.echo(request)
        return response

    def getPreprocessedData(
        self,
        project_id: str,
        data_collection_id: str,
        query_spec: qs_pb.QuerySpec,
        include_system_data: bool,
        request_id: str,
        request_context=None
    ) -> Optional[pd.DataFrame]:
        return self._read_static_data(
            project_id=project_id,
            data_collection_id=data_collection_id,
            query_spec=query_spec,
            expected_data_kind="DATA_KIND_PRE",
            system_cols_to_keep=self._include_sys_cols
            if include_system_data else [],
            request_id=request_id,
            request_context=request_context
        )

    def getProcessedOrPreprocessedData(
        self,
        project_id: str,
        data_collection_id: str,
        query_spec: qs_pb.QuerySpec,
        include_system_data: bool,
        request_id: str,
        request_context=None
    ) -> Optional[pd.DataFrame]:
        try:
            return self._read_static_data(
                project_id=project_id,
                data_collection_id=data_collection_id,
                query_spec=query_spec,
                expected_data_kind="DATA_KIND_POST",
                system_cols_to_keep=self._include_sys_cols
                if include_system_data else [],
                request_id=request_id,
                request_context=request_context
            )
        except TruEraNotFoundError:
            return self._read_static_data(
                project_id=project_id,
                data_collection_id=data_collection_id,
                query_spec=query_spec,
                expected_data_kind="DATA_KIND_PRE",
                system_cols_to_keep=self._include_sys_cols
                if include_system_data else [],
                request_id=request_id,
                request_context=request_context
            )

    def getLabels(
        self,
        project_id: str,
        data_collection_id: str,
        query_spec: qs_pb.QuerySpec,
        include_system_data: bool,
        request_id: str,
        request_context=None
    ) -> Optional[pd.DataFrame]:
        try:
            return self._read_static_data(
                project_id=project_id,
                data_collection_id=data_collection_id,
                query_spec=query_spec,
                expected_data_kind="DATA_KIND_LABEL",
                system_cols_to_keep=[NORMALIZED_LABEL_COLUMN_NAME] +
                self._include_sys_cols
                if include_system_data else [NORMALIZED_LABEL_COLUMN_NAME],
                request_id=request_id,
                request_context=request_context
            )
        except TruEraNotFoundError as e:
            self.logger.info(
                f"GetLabels could not fetch labels. Returning 'None' instead. Exception raised is {e}."
            )
            return None
        except Exception as e:
            raise TruEraInternalError(
                f"GetLabels could not fetch labels for unknown reason. Exception raised is {e}."
            )

    def getExtraData(
        self,
        project_id: str,
        data_collection_id: str,
        query_spec: qs_pb.QuerySpec,
        include_system_data: bool,
        request_id: str,
        request_context=None,
    ) -> pd.DataFrame:
        return self._read_static_data(
            project_id=project_id,
            data_collection_id=data_collection_id,
            query_spec=query_spec,
            expected_data_kind="DATA_KIND_EXTRA",
            system_cols_to_keep=self._include_sys_cols
            if include_system_data else [],
            request_id=request_id,
            request_context=request_context
        )

    def getModelPredictions(
        self,
        project_id: str,
        model_id: str,
        query_spec: qs_pb.QuerySpec,
        quantity_of_interest: QuantityOfInterest,
        classification_threshold: float,
        include_system_data: bool,
        request_id: str,
        request_context=None
    ) -> Optional[pd.DataFrame]:
        request = qs_pb.QueryRequest(
            id=request_id,
            project_id=project_id,
            prediction_request=qs_pb.PredictionRequest(
                model_id=model_id,
                qoi=quantity_of_interest,
                query_spec=query_spec,
                classification_threshold=classification_threshold
            )
        )
        dataframe = RowMajorValueTableUtil.pb_stream_to_dataframe(
            self.communicator.query(request, request_context)
        )
        if dataframe is None:
            raise TruEraNotFoundError("Could not find any points.")
        dataframe = self._resolve_split_metadata(
            dataframe=dataframe,
            system_cols_to_keep=[NORMALIZED_PREDICTION_COLUMN_NAME] +
            self._include_sys_cols
            if include_system_data else [NORMALIZED_PREDICTION_COLUMN_NAME]
        )

        return dataframe

    @staticmethod
    def _guarentee_select_cols(
        query_spec: qs_pb.QuerySpec, ensure_select_cols: List[str]
    ):
        copied = False
        for col in ensure_select_cols:
            if col not in query_spec.select_columns:
                if not copied:
                    new_query_spec = qs_pb.QuerySpec()
                    new_query_spec.CopyFrom(query_spec)
                    query_spec = new_query_spec
                    copied = True
                query_spec.select_columns.append(col)
        return query_spec

    def getModelTokens(
        self,
        project_id: str,
        model_id: str,
        query_spec: qs_pb.QuerySpec,
        quantity_of_interest: QuantityOfInterest,
        include_system_data: bool,
        classification_threshold: float,
        request_id: str,
        request_context=None
    ) -> Optional[pd.DataFrame]:
        query_spec = self._guarentee_select_cols(
            query_spec,
            [NORMALIZED_ID_COLUMN_NAME, NORMALIZED_TOKENS_COLUMN_NAME]
        )
        request = qs_pb.QueryRequest(
            id=request_id,
            project_id=project_id,
            prediction_request=qs_pb.PredictionRequest(
                model_id=model_id,
                qoi=quantity_of_interest,
                query_spec=query_spec,
                classification_threshold=classification_threshold
            )
        )
        dataframe = RowMajorValueTableUtil.pb_stream_to_dataframe(
            self.communicator.query(request, request_context)
        )
        if dataframe is None:
            raise TruEraNotFoundError("Could not find any points.")

        dataframe = self._resolve_split_metadata(
            dataframe=dataframe,
            system_cols_to_keep=[NORMALIZED_TOKENS_COLUMN_NAME] +
            self._include_sys_cols
            if include_system_data else [NORMALIZED_TOKENS_COLUMN_NAME],
            cols_to_drop=[NORMALIZED_PREDICTION_COLUMN_NAME]
        )
        return dataframe

    def getModelEmbeddings(
        self,
        project_id: str,
        model_id: str,
        query_spec: qs_pb.QuerySpec,
        quantity_of_interest: QuantityOfInterest,
        include_system_data: bool,
        request_id: str,
        request_context=None
    ) -> Optional[pd.DataFrame]:
        query_spec = self._guarentee_select_cols(
            query_spec,
            [NORMALIZED_ID_COLUMN_NAME, NORMALIZED_EMBEDDINGS_COLUMN_NAME]
        )
        request = qs_pb.QueryRequest(
            id=request_id,
            project_id=project_id,
            prediction_request=qs_pb.PredictionRequest(
                model_id=model_id,
                qoi=quantity_of_interest,
                query_spec=query_spec
            )
        )
        dataframe = RowMajorValueTableUtil.pb_stream_to_dataframe(
            self.communicator.query(request, request_context)
        )
        if dataframe is None:
            raise TruEraNotFoundError("Could not find any points.")

        dataframe = self._resolve_split_metadata(
            dataframe=dataframe,
            system_cols_to_keep=[NORMALIZED_EMBEDDINGS_COLUMN_NAME] +
            self._include_sys_cols
            if include_system_data else [NORMALIZED_EMBEDDINGS_COLUMN_NAME],
            cols_to_drop=[NORMALIZED_PREDICTION_COLUMN_NAME]
        )
        return dataframe

    def getModelInfluences(
        self,
        project_id: str,
        request_id: str,
        query_spec: qs_pb.QuerySpec,
        options: common_pb.FeatureInfluenceOptions,
        model_id: Optional[str] = None,
        include_system_data: bool = False,
        request_context=None
    ) -> Optional[pd.DataFrame]:
        request = qs_pb.QueryRequest(
            id=request_id,
            project_id=project_id,
            feature_influence_request=qs_pb.FeatureInfluenceRequest(
                model_id=model_id, query_spec=query_spec, options=options
            )
        )
        response_stream = self.communicator.query(request, request_context)
        dataframe = RowMajorValueTableUtil.pb_stream_to_dataframe(
            response_stream
        )
        if dataframe is None:
            return None

        dataframe = self._resolve_split_metadata(
            dataframe=dataframe,
            system_cols_to_keep=self._include_sys_cols
            if include_system_data else []
        )
        return dataframe

    def getAccuracies(
        self,
        project_id: str,
        model_id: str,
        accuracy_types: Sequence[AccuracyType.Type],
        query_spec: qs_pb.QuerySpec,
        quantity_of_interest: QuantityOfInterest,
        classification_threshold: float,
        include_confusion_matrix: bool,
        include_record_count: bool,
        request_id: str,
        request_context=None
    ) -> qs_pb.AccuracyResponse:
        request = qs_pb.AccuracyRequest(
            request_id=request_id,
            project_id=project_id,
            model_id=model_id,
            accuracy_type=accuracy_types,
            query_spec=query_spec,
            qoi=quantity_of_interest,
            classification_threshold=classification_threshold,
            include_confusion_matrix=include_confusion_matrix,
            include_compute_record_count=include_record_count
        )
        response = self.communicator.accuracy(request, request_context)
        return response

    def getModelComparison(
        self,
        request_id: str,
        project_id: str,
        comparison_specs: list,
        request_context=None
    ):
        request = qs_pb.QueryRequest(
            id=request_id,
            project_id=project_id,
            model_comparison_request=qs_pb.ModelComparisonRequest(
                comparison_specs=comparison_specs
            )
        )
        response = self.communicator.query(request, request_context)
        return RowMajorValueTableUtil.pb_stream_to_dataframe(response)

    def getModelBias(
        self,
        request_id: str,
        project_id: str,
        bias_type: BiasType.Type,
        model_id: str,
        query_spec_1: qs_pb.QuerySpec,
        query_spec_2: qs_pb.QuerySpec,
        qoi: QuantityOfInterest,
        classification_threshold: float,
        positive_class_favored: bool,
        request_context=None
    ):
        request = qs_pb.QueryRequest(
            id=request_id,
            project_id=project_id,
            model_bias_request=qs_pb.ModelBiasRequest(
                bias_type=bias_type,
                model_id=model_id,
                query_spec_1=query_spec_1,
                query_spec_2=query_spec_2,
                qoi=qoi,
                classification_threshold=classification_threshold,
                positive_class_favored=positive_class_favored
            )
        )
        response = self.communicator.query(request, request_context)
        return RowMajorValueTableUtil.pb_stream_to_dataframe(response)

    def getFilterData(
        self,
        project_id: str,
        data_collection_id: str,
        query_spec: qs_pb.QuerySpec,
        request_id: str,
        request_context=None
    ) -> Optional[pd.DataFrame]:
        request = qs_pb.QueryRequest(
            id=request_id,
            project_id=project_id,
            filter_data_request=qs_pb.FilterDataRequest(
                data_collection_id=data_collection_id, query_spec=query_spec
            )
        )
        response_stream = self.communicator.query(request, request_context)
        dataframe = RowMajorValueTableUtil.pb_stream_to_dataframe(
            response_stream
        )
        if dataframe is None:
            return None

        dataframe = self._resolve_split_metadata(dataframe=dataframe)
        return dataframe

    def getBatchQueryResponse(
        self,
        request: qs_pb.BatchQueryRequest,
        request_context=None
    ) -> Iterator[qs_pb.BatchQueryResponse]:
        return self.communicator.batch_query(request, request_context)

    def _pb_stream_to_batch_results(
        self, response_stream: Iterator[qs_pb.BatchQueryResponse]
    ) -> BatchDataSummaryResults:
        # NOTE: response_stream only contains one response for batch data summary though the generic getBatchQueryResponse is designed to return a response stream
        for response in response_stream:
            results = BatchDataSummaryResults(entries=[])
            for query_item_result in response.results:
                if query_item_result.error_code != qs_pb.QueryItemResult.QueryError.NO_ERROR:
                    results.entries.append(
                        BatchDataSummaryResults.BatchDataSummaryResult(
                            df=pd.DataFrame(),
                            error=query_item_result.error_code
                        )
                    )
                    continue
                dataframe = RowMajorValueTableUtil.pb_stream_to_dataframe(
                    [query_item_result]
                )
                if dataframe is None or len(dataframe) == 0:
                    results.entries.append(
                        BatchDataSummaryResults.BatchDataSummaryResult(
                            df=pd.DataFrame(),
                            error=query_item_result.error_code
                        )
                    )
                    continue
                dataframe = self._resolve_split_metadata(
                    dataframe=dataframe,
                    system_cols_to_keep=self._include_sys_cols
                )
                if isinstance(dataframe, pd.Series):
                    dataframe = dataframe.to_frame()
                results.entries.append(
                    BatchDataSummaryResults.BatchDataSummaryResult(
                        df=dataframe, error=query_item_result.error_code
                    )
                )

            return results

    def getBatchDataSummary(
        self,
        request: qs_pb.BatchQueryRequest,
        request_context=None
    ) -> BatchDataSummaryResults:
        response_stream = self.getBatchQueryResponse(
            request_context=request_context, request=request
        )
        return self._pb_stream_to_batch_results(response_stream=response_stream)

    def _read_static_data(
        self,
        *,
        project_id: str,
        data_collection_id: str,
        query_spec: qs_pb.QuerySpec,
        expected_data_kind: str,
        system_cols_to_keep: Sequence[str],
        request_id: str,
        request_context=None,
    ) -> Optional[pd.DataFrame]:
        request = qs_pb.QueryRequest(
            id=request_id,
            project_id=project_id,
            raw_data_request=qs_pb.RawDataRequest(
                data_kind=expected_data_kind,
                data_collection_id=data_collection_id,
                query_spec=query_spec
            )
        )
        response_stream = self.communicator.query(request, request_context)
        dataframe = RowMajorValueTableUtil.pb_stream_to_dataframe(
            response_stream
        )
        if dataframe is None:
            return None

        dataframe = self._resolve_split_metadata(
            dataframe=dataframe,
            system_cols_to_keep=system_cols_to_keep,
        )
        return dataframe

    def _resolve_split_metadata(
        self,
        dataframe: pd.DataFrame,
        system_cols_to_keep: Optional[list[str]] = None,
        cols_to_drop: Optional[Sequence[str]] = None
    ) -> pd.DataFrame:
        system_cols_to_keep = system_cols_to_keep or []
        cols_to_drop = cols_to_drop or []
        for col in SYSTEM_COLUMNS:
            if col not in dataframe.columns:
                continue
            elif col in [
                NORMALIZED_ID_COLUMN_NAME,
                NORMALIZED_RANKING_GROUP_ID_COLUMN_NAME,
                NORMALIZED_RANKING_ITEM_ID_COLUMN_NAME
            ]:
                continue
            elif col not in system_cols_to_keep:
                cols_to_drop.append(col)
            elif col == NORMALIZED_TIMESTAMP_COLUMN_NAME:
                # get datetime from integer epoch, but cast to string for AIQ purposes
                dataframe[NORMALIZED_TIMESTAMP_COLUMN_NAME] = pd.to_datetime(
                    dataframe[NORMALIZED_TIMESTAMP_COLUMN_NAME], unit="s"
                ).astype(str)
        df_columns = set(dataframe.columns)
        cols_to_drop = [c for c in cols_to_drop if c in df_columns]
        dataframe.drop(cols_to_drop, axis="columns", inplace=True)
        if NORMALIZED_ID_COLUMN_NAME in dataframe.columns:
            dataframe.set_index(NORMALIZED_ID_COLUMN_NAME, inplace=True)
        return dataframe
