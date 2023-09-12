from typing import Mapping, Optional, Sequence, Tuple, TYPE_CHECKING, Union
import uuid

import pandas as pd
import pyarrow as pa

from truera.client.column_info import CreateCacheInfo
from truera.client.ingestion.constants import DEFAULT_APPROX_MAX_ROWS
from truera.client.ingestion.constants import DEFAULT_SAMPLE_STRATEGY
from truera.client.ingestion.constants import DEFAULT_SPLIT_MODE
from truera.client.ingestion.constants import DEFAULT_SPLIT_TYPE
from truera.client.ingestion.constants import NLP_INFLUENCE_COL_NAME
from truera.client.ingestion.constants import PROD_DATA_SPLIT_TYPE
from truera.client.ingestion.ingestion_validation_util import \
    validate_column_spec_and_model_output_context
from truera.client.ingestion.ingestion_validation_util import \
    validate_dataframe
from truera.client.ingestion.temporary_file import TemporaryFile
from truera.client.ingestion.util import BaseColumnSpec
from truera.client.ingestion.util import column_spec_from_kwargs
from truera.client.ingestion.util import ModelOutputContext
from truera.client.ingestion.util import NLPColumnSpec
from truera.client.ingestion_client import Table
from truera.client.services.artifactrepo_client import ArtifactType
from truera.client.util.workspace_validation_utils import \
    is_gradient_influence_type
# pylint: disable=no-name-in-module,no-member
from truera.protobuf.public.common.data_kind_pb2 import DATA_KIND_ALL
from truera.protobuf.public.data_service import \
    data_service_messages_pb2 as ds_messages_pb
from truera.protobuf.public.data_service import data_service_pb2 as ds_pb

# pylint: enable=no-name-in-module

if TYPE_CHECKING:
    from truera.client.remote_truera_workspace import RemoteTrueraWorkspace


def add_data(
    remote_workspace: 'RemoteTrueraWorkspace',
    data: Union[pd.DataFrame, 'Table'],
    *,
    split_name: str,
    column_spec: Union[BaseColumnSpec, Mapping[str, Union[str, Sequence[str]]]],
    model_output_context: Optional[Union[ModelOutputContext, dict]] = None,
    is_production_data: Optional[bool] = False,
    sample_count: Optional[int] = None
):
    if column_spec and not isinstance(column_spec, BaseColumnSpec):
        column_spec = column_spec_from_kwargs(**column_spec)
    if model_output_context and not isinstance(
        model_output_context, ModelOutputContext
    ):
        model_output_context = ModelOutputContext(**model_output_context)

    # Validation
    remote_workspace._ensure_project()
    remote_workspace._ensure_data_collection()

    project_id = remote_workspace.project.id
    project_influence_type = remote_workspace.cs_client.get_influence_algorithm_type(
        project_id
    )
    project_input_type = remote_workspace._get_input_type()
    existing_splits = remote_workspace.artifact_interaction_client.get_all_datasplits_in_data_collection(
        remote_workspace.project.name,
        remote_workspace.data_collection.name,
        exclude_prod=False
    )
    existing_models = remote_workspace.get_models()

    if split_name not in existing_splits:
        target_split_metadata = None
    else:
        target_split_metadata = remote_workspace.ar_client.get_datasplit_metadata(
            project_id=project_id,
            datasplit_name=split_name,
            data_collection_name=remote_workspace.data_collection.name
        )

    validate_column_spec_and_model_output_context(
        column_spec,
        model_output_context,
        split_name=split_name,
        existing_models=existing_models,
        existing_splits=existing_splits,
        project_influence_type=project_influence_type,
        target_split_metadata=target_split_metadata
    )

    rowset_id = None
    load_data_request = None
    sample_count = sample_count if sample_count is not None else DEFAULT_APPROX_MAX_ROWS
    if isinstance(data, Table):
        rowset_id = data._rowset_id
    elif isinstance(data, pd.DataFrame):
        validate_dataframe(
            data=data,
            column_spec=column_spec,
            input_type=project_input_type,
            logger=remote_workspace.logger
        )

        data, column_spec = format_dataframe(data, column_spec=column_spec)
        if data.shape[0] < sample_count:
            sample_count = data.shape[0]

        # Upload DataFrame as parquet
        with TemporaryFile(mode="w+", suffix=".parquet") as file:
            to_parquet(data, path=file.name, column_spec=column_spec)
            uri = remote_workspace.artifact_interaction_client.ar_client.upload_artifact(
                src=file.name,
                project_id=project_id,
                artifact_type=ArtifactType.data_source,
                artifact_id=str(uuid.uuid4()),
                intra_artifact_path="",
                scoping_artifact_ids=[],
                stream=False
            )

        # Build load request
        load_data_request = ds_pb.LoadDataRequest(
            data_source_info=ds_messages_pb.LoadDataInfo(
                project_id=project_id,
                describes_file_kind=DATA_KIND_ALL,
                creation_reason=ds_messages_pb.DS_CR_SYSTEM_REQUESTED,
                type=ds_messages_pb.DS_LOCAL,
                uri=uri,
                format=ds_messages_pb.Format(
                    file_type=ds_messages_pb.FT_PARQUET
                )
            )
        )
    else:
        raise ValueError(
            f"`data` must be either a pd.DataFrame or Table, instead received '{type(data)}'"
        )

    # Build materialize request
    split_type = PROD_DATA_SPLIT_TYPE if is_production_data else DEFAULT_SPLIT_TYPE
    materialize_request = _build_materialize_request(
        remote_workspace,
        split_name,
        column_spec,
        model_output_context,
        row_count=sample_count,
        split_already_exists=split_name in existing_splits,
        rowset_id=rowset_id,
        split_type=split_type
    )

    # Submit request(s)
    materialize_operation_id = _submit_data_service_requests(
        remote_workspace, materialize_request, load_data_request
    )

    # Wait for materialize to succeed
    remote_workspace.logger.info("Waiting for data split to materialize...")
    status = remote_workspace.get_ingestion_client(
    )._wait_for_materialize_operation(materialize_operation_id)
    remote_workspace.logger.info(
        f"Materialize operation id: {materialize_operation_id} finished with status: {status}."
    )
    remote_workspace.data_service_client.get_materialize_data_status(
        project_id=project_id,
        materialize_operation_id=materialize_operation_id,
        throw_on_error=True
    )

    # Set datasplit in current context
    remote_workspace.data_split_name = split_name


def _build_materialize_request(
    remote_workspace: 'RemoteTrueraWorkspace',
    split_name: str,
    column_spec: BaseColumnSpec,
    model_output_context: ModelOutputContext,
    row_count: int,
    split_already_exists: bool = False,
    rowset_id: str = None,
    split_type: str = DEFAULT_SPLIT_TYPE
) -> ds_pb.MaterializeDataRequest:
    # Create model cache info
    column_info = column_spec.to_column_info()
    if model_output_context is None:
        model_cache = None
    else:
        model_metadata = remote_workspace.artifact_interaction_client.ar_client.get_model_metadata(
            project_id=remote_workspace.project.id,
            model_name=model_output_context.model_name
        )
        background_split_id = None
        if column_info.feature_influences is not None and len(
            column_info.feature_influences
        ) > 0 and not is_gradient_influence_type(
            model_output_context.influence_type
        ):
            background_split_id = remote_workspace.ar_client.get_datasplit_metadata(
                project_id=remote_workspace.project.id,
                data_collection_name=remote_workspace.data_collection.name,
                datasplit_name=model_output_context.background_split_name
            ).id
        model_cache = CreateCacheInfo(
            model_id=model_metadata.id,
            score_type=model_output_context.score_type,
            background_split_id=background_split_id,
            explanation_algorithm_type=model_output_context.influence_type
        ).build_create_cache_info()

    # Create split info
    existing_split_id, create_split_info = None, None
    if split_already_exists:
        existing_split_id = remote_workspace.artifact_interaction_client.ar_client.get_datasplit_metadata(
            project_id=remote_workspace.project.id,
            data_collection_name=remote_workspace.data_collection.name,
            datasplit_name=split_name,
        ).id
    else:
        create_split_info = ds_messages_pb.CreateSplitInfo(
            output_split_name=split_name,
            output_split_type=split_type,
            # TODO: Check if DEFAULT_SPLIT_MODE is required for all scenarios or in some we might have to change
            output_split_mode=DEFAULT_SPLIT_MODE
        )

    # Create materialize request
    materialize_request = ds_pb.MaterializeDataRequest(
        rowset_id=rowset_id,
        data_info=ds_messages_pb.MaterializeDataInfo(
            project_id=remote_workspace.project.id,
            output_data_collection_id=remote_workspace.data_collection.id,
            cache_info=model_cache,
            existing_split_id=existing_split_id,
            create_split_info=create_split_info,
            projections=column_info.get_projections(),
            system_columns=column_info.get_system_column_details()
        ),
        sample_strategy=DEFAULT_SAMPLE_STRATEGY,
        approx_max_rows=row_count,
    )
    return materialize_request


def _submit_data_service_requests(
    remote_workspace: 'RemoteTrueraWorkspace',
    materialize_request: ds_pb.MaterializeDataRequest,
    load_data_request: ds_pb.LoadDataRequest = None
) -> str:
    if load_data_request:
        rowset_id, _ = remote_workspace.data_service_client.load_data_source_from_request(
            load_data_request
        )
        materialize_request.rowset_id = rowset_id

    response = remote_workspace.data_service_client.materialize_data_from_request(
        materialize_request=materialize_request
    )
    return response.materialize_operation_id


def format_dataframe(
    data: pd.DataFrame, column_spec: BaseColumnSpec
) -> Tuple[pd.DataFrame, BaseColumnSpec]:
    # Format id column
    data = data.copy()
    data[column_spec.id_col_name
        ] = data[column_spec.id_col_name].astype("string")

    if isinstance(
        column_spec, NLPColumnSpec
    ) and column_spec.token_influence_col_name:
        # Rename feature influence column name to NLP_INFLUENCE_COL_NAME ('__truera_influences__')
        data = data.rename(
            columns={
                column_spec.token_influence_col_name: NLP_INFLUENCE_COL_NAME
            }
        )
        column_spec = column_spec.copy(
            token_influence_col_name=NLP_INFLUENCE_COL_NAME
        )

    # Format tags column
    if column_spec.tags_col_name:
        data[column_spec.tags_col_name] = data[column_spec.tags_col_name].apply(
            lambda tags: [tags] if isinstance(tags, str) else tags
        )

    return data, column_spec


def to_parquet(data: pd.DataFrame, path: str, column_spec: 'BaseColumnSpec'):
    '''Write pandas.DataFrame to a file. 
    
    This function handles the special case of tags column, which is a list of strings.
    '''

    if not column_spec.tags_col_name:
        return data.to_parquet(path, index=False)

    schema_without_lists = pa.Schema.from_pandas(
        data.drop(column_spec.tags_col_name, axis="columns")
    )

    fields = [pa.field(column_spec.tags_col_name, pa.list_(pa.string()))]
    for col_name, col_type in zip(
        schema_without_lists.names, schema_without_lists.types
    ):
        fields.append(pa.field(col_name, col_type))

    data.to_parquet(
        path=path, index=False, engine="pyarrow", schema=pa.schema(fields)
    )
