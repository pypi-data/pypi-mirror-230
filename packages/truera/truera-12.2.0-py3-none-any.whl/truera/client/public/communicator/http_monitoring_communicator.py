import logging
from typing import Union

from truera.client.public.auth_details import AuthDetails
from truera.client.public.communicator.http_communicator import \
    HttpCommunicator
from truera.client.public.communicator.monitoring_communicator import \
    MonitoringCommunicator
from truera.protobuf.monitoring import \
    monitoring_dashboard_pb2 as monitoring_dashboard_pb2


class HttpMonitoringCommunicator(MonitoringCommunicator):

    def __init__(
        self,
        connection_string: str,
        auth_details: AuthDetails,
        logger: logging.Logger,
        *,
        verify_cert: Union[bool, str] = True
    ):
        connection_string = connection_string.rstrip("/")
        self.connection_string = f"{connection_string}/api/monitoring"
        self.logger = logger
        self.http_communicator = HttpCommunicator(
            connection_string=self.connection_string,
            auth_details=auth_details,
            logger=logger,
            verify_cert=verify_cert
        )

    def query_data(
        self,
        req: monitoring_dashboard_pb2.QueryDataRequest,
        request_context=None
    ) -> monitoring_dashboard_pb2.QueryDataResponse:
        uri = f"{self.connection_string}/querydata"
        json_req = self.http_communicator._proto_to_json(req)
        json_resp = self.http_communicator.get_request(uri, {}, body=json_req)
        return self.http_communicator._json_to_proto(
            json_resp, monitoring_dashboard_pb2.QueryDataResponse()
        )
