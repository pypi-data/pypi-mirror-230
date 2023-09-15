from typing import TypedDict, Union, Dict
from typing_extensions import Required


class SpanEvent(TypedDict, total=False):
    """ span_event. """

    event_id: str
    organization_id: int
    project_id: Required[int]
    """ Required property """

    trace_id: Required[str]
    """
    The trace ID is a unique identifier for a trace. It is a 16 byte hexadecimal string.

    Required property
    """

    span_id: Required[str]
    """
    The span ID is a unique identifier for a span within a trace. It is an 8 byte hexadecimal string.

    Required property
    """

    parent_span_id: str
    """ The parent span ID is the ID of the span that caused this span. It is an 8 byte hexadecimal string. """

    segment_id: str
    """ The segment ID is a unique identifier for a segment within a trace. It is an 8 byte hexadecimal string. """

    group_raw: str
    """ The raw group ID has from the root transaction. It is an 8 byte hexadecimal string. """

    is_segment: Required[bool]
    """
    Whether this span is a segment or not.

    Required property
    """

    start_timestamp_ms: Required[int]
    """
    The start timestamp of the span in milliseconds since epoch.

    Required property
    """

    duration_ms: Required[int]
    """
    The duration of the span in milliseconds.

    Required property
    """

    exclusive_time_ms: Required[int]
    """
    The exclusive time of the span in milliseconds.

    Required property
    """

    retention_days: Required[Union[int, None]]
    """ Required property """

    description: Union[str]
    tags: Union[Dict[str, Union[str, Union[int, float], bool]], None]
    """  Manual key/value tag pairs. """

    sentry_tags: "_SentryExtractedTags"


_SentryExtractedTags = Union["_SentryExtractedTagsAnyof0"]
""" Tags extracted by sentry. These are kept separate from customer tags """



_SentryExtractedTagsAnyof0 = TypedDict('_SentryExtractedTagsAnyof0', {
    'http.method': Union[str, None],
    'action': Union[str, None],
    'domain': Union[str, None],
    'module': Union[str, None],
    # 8 byte hexadecimal string
    'group': Union[str, None],
    'system': Union[str, None],
    'status': Union[str, None],
    'status_code': Union[int, None],
    'transaction': Union[str, None],
    'transaction.op': Union[str, None],
    'op': Union[str, None],
    'transaction.method': Union[str, None],
}, total=False)
