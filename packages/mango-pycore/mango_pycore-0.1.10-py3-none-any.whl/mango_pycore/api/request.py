import base64
import datetime
import traceback

from .exceptions import BadRequest

class BaseRequest:
    def __init__(self):
        pass


class RestApiRequest(BaseRequest):
    def __init__(self, event: dict, debug=False):
        super().__init__()
        self.raw_event = event
        self.debug = debug
        self._process_api_gateway_request_v1(event)

    def _process_api_gateway_request_v1(self, event):
        try:
            # Required Data
            self.headers = event['headers']
            self.method = event['requestContext']['httpMethod']
            self.path = event['path']
            self.timestamp = event['requestContext']['requestTimeEpoch']
            self.date = datetime.datetime.utcfromtimestamp(self.timestamp/1000)
            self.route_key = f"{self.method} {event['requestContext']['resourcePath']}"
            self.stage = event['requestContext']['stage']

            # Conditional Data
            self.api_id = event['requestContext'].get('apiId')
            self.request_id = event['requestContext'].get('requestId')
            self.cookies = event.get('cookies')
            self.body = event.get('body', {}) if event.get('body', {}) else '{}'
            self.is_base_64_encoded = event.get('isBase64Encoded')
            self.path_parameters = event.get('pathParameters', {})
            self.query_string = event.get('queryStringParameters', {}) if event.get('queryStringParameters') else {}
            self.protocol = event['requestContext'].get('protocol')
            self.source_ip = event['requestContext']['identity'].get('sourceIp')
            self.host = event['requestContext'].get('domainName')
        except KeyError:
            e = "Bad request from api gateway v1"
            if self.debug:
                e = traceback.format_exc()
            raise BadRequest(e)


class HttpApiRequest(BaseRequest):
    def __init__(self, event: dict, debug=False):
        super().__init__()
        self.raw_event = event
        self.debug = debug
        self._process_api_gateway_request_v2(event)

    def _process_api_gateway_request_v2(self, event):
        try:
            # Required data
            self.headers = event['headers']
            self.method = event['requestContext']['http']['method']
            self.path = event['requestContext']['http']['path']
            self.timestamp = event['requestContext']['timeEpoch']
            self.date = datetime.datetime.utcfromtimestamp(self.timestamp / 1000)
            self.route_key = event['routeKey']
            self.stage = event['requestContext']['stage']

            # Conditional data
            self.api_id = event['requestContext'].get('apiId')
            self.request_id = event['requestContext'].get('requestId')
            self.body = event.get('body', {}) if event.get('body', {}) else '{}'
            self.cookies = event.get('cookies')
            self.is_base_64_encoded = event.get('isBase64Encoded')
            self.path_parameters = event.get('pathParameters', {})
            self.query_string = event.get('queryStringParameters', {}) if event.get('queryStringParameters') else {}
            self.protocol = event['requestContext']['http'].get('protocol')
            self.source_ip = event['requestContext']['http'].get('sourceIp')
            self.host = event['requestContext'].get('domainName')
        except KeyError:
            e = "Bad request from api gateway v2"
            if self.debug:
                e = traceback.format_exc()
            raise BadRequest(e)


class WebsocketApiRequest:
    def __init__(self, event: dict, debug=False):
        self.raw_event = event
        self.debug = debug
        self._process_api_websocket_request(event)

    def _process_api_websocket_request(self, event):
        try:
            # Required Data
            self.route_key = event["requestContext"]["routeKey"]
            self.source_ip = event["requestContext"]["identity"]["sourceIp"]
            self.stage = event["requestContext"]["stage"]
            self.message_direction = event["requestContext"]["messageDirection"]
            self.event_type = event["requestContext"]["eventType"]
            self.request_id = event["requestContext"]["requestId"]
            self.connection_id = event["requestContext"]["connectionId"]
            self.domain_name = event["requestContext"]["domainName"]
            self.is_encoded = event["isBase64Encoded"]
            self.body = self._extract_body(self.is_encoded, event["body"]) if "body" in event.keys() else {}
            self.query_params = event.get("queryStringParameters", {})

        except KeyError:
            e = "Bad request from api gateway websocket"
            if self.debug:
                e = traceback.format_exc()
            raise BadRequest(e)

    def _extract_body(self, encoded, body):
        if encoded:
            data = base64.b64decode(body)
            return data
        return body
