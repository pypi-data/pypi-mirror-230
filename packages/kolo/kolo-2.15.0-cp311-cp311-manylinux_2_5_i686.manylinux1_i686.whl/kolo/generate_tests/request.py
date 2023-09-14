from itertools import cycle
from urllib.parse import parse_qsl

from more_itertools import before_and_after, grouper


def _format_header(header: str) -> str:
    header = header.upper().replace("-", "_")
    if header in ("CONTENT_LENGTH", "CONTENT_TYPE"):
        return header
    return f"HTTP_{header}"


def get_request_headers(request):
    if not request:
        return {}
    request_headers = {
        _format_header(header): value for header, value in request["headers"].items()
    }
    if "HTTP_COOKIE" in request_headers and request_headers["HTTP_COOKIE"] == "":
        del request_headers["HTTP_COOKIE"]

    request_headers_to_delete = [
        "CONTENT_LENGTH",
        "HTTP_HOST",
        "HTTP_X_FORWARDED_FOR",
        "HTTP_X_FORWARDED_PROTO",
        "HTTP_CONNECTION",
        "HTTP_CACHE_CONTROL",
        "HTTP_DNT",
        "HTTP_SEC_CH_UA",
        "HTTP_USER_AGENT",
        "HTTP_ACCEPT",
        "HTTP_SEC_FETCH_DEST",
        "HTTP_SEC_CH_UA_MOBILE",
        "HTTP_REFERER",
        "HTTP_ACCEPT_ENCODING",
        "HTTP_ACCEPT_LANGUAGE",
        "HTTP_SEC_FETCH_SITE",
        "HTTP_SEC_FETCH_MODE",
        "HTTP_SEC_FETCH_USER",
        "HTTP_SEC_FETCH_DEST",
        "HTTP_SEC_CH_UA_PLATFORM",
        "HTTP_ORIGIN",
        "HTTP_UPGRADE_INSECURE_REQUESTS",
    ]

    for request_header in request_headers_to_delete:
        if request_header in request_headers:
            del request_headers[request_header]

    if "CONTENT_TYPE" in request_headers:
        # This is a special header, which ends up influencing
        # how the django test client formats different parts of the
        # request. It's provided to the test client as a lowercased
        # argument
        request_headers["content_type"] = request_headers["CONTENT_TYPE"]
        del request_headers["CONTENT_TYPE"]
    return request_headers


def get_request_body(request, request_headers):
    if not request:
        return ""
    request_body = request["body"]
    content_type = request_headers.get("content_type", "")
    if content_type == "application/x-www-form-urlencoded":
        # So: How can we now format the body so that it becomes more readable
        # We can totally cater to just this urlencoded version first...

        # TODO: Eventually need to be able to support multivaluedicts / query params
        # with multiple values per key
        # I couldn't quite get that to work.
        # Custom request body formatting is clearly useful also here again..
        urldecoded_body = dict(parse_qsl(request_body))
        return f"urlencode({urldecoded_body})"
    elif "multipart/form-data" in content_type:
        request_headers.pop("content_type")
        if request["method"] == "POST":
            return str(request["post_data"])
        return ""
    else:
        return repr(request_body)


def get_query_params(request):
    if not request:
        return ""
    query_params = request["query_params"]
    if query_params:
        return f"{query_params},"
    return ""


def group_request_frames(frames):
    types = cycle(("django_request", "django_template_start", "django_response"))
    for frame_type in types:  # pragma: no branch
        before, after = before_and_after(lambda f: f["type"] == frame_type, frames)
        yield tuple(before)
        frames = tuple(after)
        if not frames:
            break


def parse_request_frames(frames):
    frames = (
        frame
        for frame in frames
        if frame["type"]
        in ("django_request", "django_response", "django_template_start")
    )
    grouped_frames = group_request_frames(frames)
    served_request_frames = []
    for _request, templates, _response in grouper(grouped_frames, 3):
        if not _request or not _response:
            continue  # pramga: no cover

        # If we get multiple requests grouped, assume only the last one is valid
        request = _request[-1]

        # If we get multiple responses grouped, assume only the first one is valid
        response = _response[0]

        served_request_frames.append(
            {
                "request": request,
                "response": response,
                "templates": [frame["template"] for frame in templates],
            }
        )
    return served_request_frames


def build_test_client_call(
    request, query_params, prettified_request_body, request_headers, *, pytest
):
    if not request:
        return ""
    client = "client" if pytest else "self.client"
    headers = "\n".join(
        f"{header}={repr(value)}," for header, value in request_headers.items()
    )
    method = request["method"].lower()
    path_info = request["path_info"]
    return f"""{client}.{method}(
            "{path_info}",
            {query_params}
            {prettified_request_body},
            {headers}
        )
    """
