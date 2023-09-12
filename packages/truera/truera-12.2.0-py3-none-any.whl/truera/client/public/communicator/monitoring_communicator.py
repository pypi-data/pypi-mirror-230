from abc import ABC
from abc import abstractmethod

from truera.protobuf.monitoring import \
    monitoring_dashboard_pb2 as monitoring_dashboard_pb2


class MonitoringCommunicator(ABC):

    @abstractmethod
    def query_data(
        self,
        req: monitoring_dashboard_pb2.QueryDataRequest,
        request_context=None
    ) -> monitoring_dashboard_pb2.QueryDataResponse:
        pass