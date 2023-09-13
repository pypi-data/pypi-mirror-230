import itertools
import ujson
from promoted_python_delivery_client.model.request import Request
from promoted_python_delivery_client.model.response import Response
from promoted_python_delivery_client.model.log_request import LogRequest


delivery_request_schema = Request.schema()  # type: ignore this is from dataclass_json
log_request_schema = LogRequest.schema()  # type: ignore this is from dataclass_json


# DEPRECATED use delivery_request_to_json_3
def delivery_request_to_json(req: Request) -> str:
    return req.to_json()  # type: ignore this is from dataclass_json


# DEPRECATED use delivery_request_to_json_3
def delivery_request_to_json_2(req: Request) -> str:
    return ujson.dumps(req.to_dict(encode_json=False))  # type: ignore this is from dataclass_json


# This one profiles the fastest, the others are here for reference purposes.
def delivery_request_to_json_3(req: Request) -> str:
    kvs = delivery_request_schema.dump(req)  # type: ignore this is from dataclass_json
    return ujson.dumps(_clean_empty(kvs))


# DEPRECATED use log_request_to_json_3
def log_request_to_json(req: LogRequest) -> str:
    return req.to_json()  # type: ignore this is from dataclass_json


# DEPRECATED use log_request_to_json_3
def log_request_to_json_2(req: LogRequest) -> str:
    return ujson.dumps(req.to_dict(encode_json=False))  # type: ignore this is from dataclass_json


# This one profiles the fastest, the others are here for reference purposes.
def log_request_to_json_3(req: LogRequest) -> str:
    kvs = log_request_schema.dump(req)  # type: ignore this is from dataclass_json
    return ujson.dumps(_clean_empty(kvs))


def delivery_response_from_json(payload: bytes) -> Response:
    return Response.from_json(payload)  # type: ignore this is from dataclass_json


def delivery_reponse_from_json_2(payload: bytes) -> Response:
    kvs = ujson.loads(payload)
    return Response.from_dict(kvs)  # type: ignore this is from dataclass_json


def _clean_empty(d, keep_empty=False):
    if isinstance(d, dict):
        return {
            k: v
            for k, v in ((k, _clean_empty(v, keep_empty=(keep_empty or k == "struct" or k == "insertionMatrix"))) for k, v in d.items())
            if v or keep_empty
        }
    if isinstance(d, list):
        return [
            v
            for v in map(_clean_empty, d, itertools.repeat(keep_empty, len(d)))
            if v or keep_empty]
    return d
