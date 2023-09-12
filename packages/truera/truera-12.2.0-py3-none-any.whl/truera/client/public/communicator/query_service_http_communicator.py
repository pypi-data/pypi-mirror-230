from truera.client.public.auth_details import AuthDetails
from truera.client.public.communicator.http_communicator import \
    HttpCommunicator
from truera.client.public.communicator.query_service_communicator import \
    AbstractQueryServiceCommunicator
from truera.protobuf.queryservice import query_service_pb2 as qs_pb


class HttpQueryServiceCommunicator(
    HttpCommunicator, AbstractQueryServiceCommunicator
):

    def __init__(
        self,
        connection_string: str,
        auth_details: AuthDetails = None,
        logger=None
    ):
        connection_string = connection_string.rstrip("/")
        self.connection_string = f"{connection_string}/api/query"
        self.http_communicator = HttpCommunicator(
            connection_string=connection_string,
            auth_details=auth_details,
            logger=logger
        )

    def echo(self, request: qs_pb.EchoRequest) -> qs_pb.EchoResponse:
        uri = f"{self.connection_string}/queryservice/echo/{request.request_id}/{request.message}"
        json_resp = self.http_communicator.get_request(uri, None)
        return self.http_communicator._json_to_proto(
            json_resp, qs_pb.EchoResponse()
        )

    def query(
        self,
        request: qs_pb.QueryRequest,
        request_context=None
    ) -> qs_pb.QueryResponse:
        uri = f"{self.connection_string}/queryservice/query"
        json_req = self.http_communicator._proto_to_json(request)
        json_resp_arr = []
        with self.http_communicator.post_request(
            uri, json_data_or_generator=json_req, stream=True
        ) as response:
            self.http_communicator._handle_response(response)
            response.encoding = "UTF-8"
            for body in response.iter_lines(decode_unicode=True):
                json_resp_arr.append(body)
        json_resp_arr = "".join(json_resp_arr)
        return self.http_communicator._json_to_proto(
            json_resp_arr, qs_pb.QueryResponse()
        )

    def accuracy(
        self,
        request: qs_pb.AccuracyRequest,
        request_context=None
    ) -> qs_pb.AccuracyResponse:
        uri = f"{self.connection_string}/queryservice/accuracy"
        json_req = self.http_communicator._proto_to_json(request)
        response = self.http_communicator.post_request(
            uri, json_data_or_generator=json_req
        )
        return self.http_communicator._json_to_proto(
            response, qs_pb.AccuracyResponse()
        )
