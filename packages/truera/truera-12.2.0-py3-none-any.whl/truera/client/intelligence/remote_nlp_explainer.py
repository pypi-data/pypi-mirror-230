from __future__ import annotations

import logging
from typing import Dict, Optional, TYPE_CHECKING, Union

import pandas as pd

from truera.client.client_utils import get_qoi_from_string
from truera.client.client_utils import get_string_from_qoi_string
from truera.client.errors import NotFoundError
from truera.client.intelligence.explainer import NonTabularExplainer
from truera.client.intelligence.remote_explainer import RemoteSplitMetadata
from truera.client.services.artifact_interaction_client import Model
from truera.client.services.artifact_interaction_client import Project

if TYPE_CHECKING:
    from ipywidgets import widgets

    from truera.client.remote_truera_workspace import RemoteTrueraWorkspace


class RemoteNLPExplainer(NonTabularExplainer):

    def __init__(
        self, workspace: RemoteTrueraWorkspace, project: Project, model: Model,
        data_collection_name: str, data_split_name: str
    ) -> None:
        self._logger = logging.getLogger(__name__)
        self._workspace = workspace
        self._project = project
        self._model = model
        model_meta = self._workspace.artifact_interaction_client.get_model_metadata(
            self._project.name, self._model.model_name
        )
        self._data_collection_id = model_meta["data_collection_id"]
        self._data_collection_name = data_collection_name
        self._base_data_split = None
        self.set_base_data_split(data_split_name)
        self._segment = None

    @property
    def logger(self):
        return self._logger

    @property
    def _project_id(self) -> str:
        return self._project.id

    @property
    def _project_name(self) -> str:
        return self._project.name

    @property
    def _model_id(self) -> str:
        return self._model.model_id

    def _get_score_type(self) -> str:
        project_metadata = self._workspace.artifact_interaction_client.get_project_metadata(
            self._project_id
        )
        return get_string_from_qoi_string(
            project_metadata["settings"]["score_type"]
        )

    def _get_split_metadata(self, split_name: str) -> RemoteSplitMetadata:
        split_id = self._workspace.artifact_interaction_client.get_split_metadata(
            self._project.name, self._data_collection_name, split_name
        )["id"]
        return RemoteSplitMetadata(split_id=split_id, split_name=split_name)

    def set_base_data_split(self, data_split_name: str):
        if not data_split_name:
            self._base_data_split = None
            return
        self._base_data_split = self._get_split_metadata(data_split_name)

    def _ensure_base_data_split(self):
        if not self._base_data_split:
            raise ValueError(
                "Set the current data_split using `set_base_data_split`"
            )

    def get_base_data_split(self) -> str:
        self._ensure_base_data_split()
        return self._base_data_split.split_name

    def get_data_collection(self) -> str:
        return self._data_collection_name

    def get_xs(
        self,
        start: Optional[int] = 0,
        stop: Optional[int] = None,
        extra_data: bool = False,
        system_data: bool = False
    ) -> pd.DataFrame:
        self._ensure_base_data_split()
        return self._workspace.aiq_client.get_xs(
            self._project_id,
            self._base_data_split.split_id,
            self._data_collection_id,
            start,
            stop,
            extra_data=extra_data,
            system_data=system_data,
            segment=self._segment,
            model_id=self._model_id
        ).response

    def get_ys(
        self,
        start: Optional[int] = 0,
        stop: Optional[int] = None,
        system_data: bool = False
    ) -> pd.DataFrame:
        self._ensure_base_data_split()
        return self._workspace.aiq_client.get_ys(
            self._project_id,
            self._base_data_split.split_id,
            self._data_collection_id,
            start,
            stop,
            system_data=system_data,
            segment=self._segment,
            model_id=self._model_id
        ).response

    def get_ys_pred(
        self,
        start: Optional[int] = 0,
        stop: Optional[int] = None,
        *,
        system_data: bool = False,
        include_all_points: bool = False,
        score_type: Optional[str] = None,
        wait: bool = True
    ) -> pd.DataFrame:
        self._ensure_base_data_split()
        score_type_qoi = get_qoi_from_string(score_type) if score_type else None
        return self._workspace.aiq_client.get_ys_pred(
            self._project_id,
            self._model_id,
            self._base_data_split.split_id,
            start,
            stop,
            segment=self._segment,
            include_system_data=system_data,
            include_all_points=include_all_points,
            score_type=score_type_qoi,
            wait=wait
        ).response

    def compute_feature_influences(
        self,
        start: Optional[int] = 0,
        stop: Optional[int] = None,
        score_type: Optional[str] = None,
        system_data: bool = False,
        wait: bool = True
    ) -> pd.DataFrame:
        self._ensure_base_data_split()
        self._validate_feature_influence_score_type(score_type)
        return self._workspace.aiq_client.get_feature_influences(
            self._project_id,
            self._model_id,
            self._base_data_split.split_id,
            start,
            stop,
            score_type=score_type,
            segment=self._segment,
            include_system_data=system_data,
            wait=wait,
            dont_compute=False
        ).response

    def get_feature_influences(
        self,
        start: Optional[int] = 0,
        stop: Optional[int] = None,
        score_type: Optional[str] = None,
        system_data: bool = False,
    ) -> pd.DataFrame:
        self._ensure_base_data_split()
        self._validate_feature_influence_score_type(score_type)
        try:
            return self._workspace.aiq_client.get_feature_influences(
                self._project_id,
                self._model_id,
                self._base_data_split.split_id,
                start,
                stop,
                score_type=score_type,
                segment=self._segment,
                include_system_data=system_data,
                wait=False,
                dont_compute=True
            ).response
        except NotFoundError:
            raise NotFoundError(
                "Feature influences not found. Compute feature influences with `compute_feature_influences`"
            )

    def compute_performance(
        self,
        metric_type: Optional[str] = None,
        threshold: float = 0.5,
        plot_roc: bool = False
    ) -> Dict[str, Union[float, Dict[int, float]]]:
        ys = self.get_ys()
        ys_preds = self.get_ys_pred().to_numpy()
        return self._compute_performance(
            ys, ys_preds, metric_type, threshold, plot_roc
        )

    def global_token_summary(
        self,
        num_records: int = None,
        max_words_to_track: int = 500,
        offset: int = 0
    ) -> widgets.Widget:
        """
        Summary and exploration of the most important tokens in the split.
        Args:
            - num_records: The number of records to use.
            - max_words_to_track: The maximum number of words to show. Defaults
              to 500.
            - offset: An index offset for the records to use. Defaults to 0.
        Returns:
            An interactive widget.
        """

        from truera.nlp.general.aiq.utils import NLPSplitData
        from truera.nlp.general.aiq.visualizations import Figures
        from truera.nlp.general.utils.configs import TokenType

        viz = Figures(None)

        split_data = NLPSplitData.from_remote_workspace(self._workspace)

        obj = viz.GlobalTokenSummary(
            self,
            split_data=split_data,
            num_records=num_records,
            max_words_to_track=max_words_to_track,
            offset=offset,
            token_type=TokenType.
            TOKEN  # TODO: Spans not currently supported in remote workspace
        )

        return obj.render()

    def record_explanations_attribution_tab(
        self, num_records: int = None
    ) -> widgets.Widget:
        """ Display the influence profile plot and feature interactions of each sentence in the split.
        Args:
            num_records: The number of records to use.
        Returns:
            An interactive widget.
        """

        from truera.nlp.general.aiq.utils import NLPSplitData
        from truera.nlp.general.aiq.visualizations import Figures
        from truera.nlp.general.utils.configs import TokenType

        viz = Figures(None)

        split_data = NLPSplitData.from_remote_workspace(self._workspace)

        return viz.record_explanations_attribution_tab(
            split_data,
            num_records=num_records,
            enable_feature_interactions=
            False  # TODO: enable feature interactions by ingesting gradient paths
        )
