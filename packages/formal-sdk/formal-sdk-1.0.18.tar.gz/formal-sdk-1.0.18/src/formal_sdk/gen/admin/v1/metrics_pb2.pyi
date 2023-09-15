from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GetMetricsRequest(_message.Message):
    __slots__ = ["datastore_id", "interval", "user_id"]
    DATASTORE_ID_FIELD_NUMBER: _ClassVar[int]
    INTERVAL_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    datastore_id: _containers.RepeatedScalarFieldContainer[str]
    interval: str
    user_id: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, datastore_id: _Optional[_Iterable[str]] = ..., interval: _Optional[str] = ..., user_id: _Optional[_Iterable[str]] = ...) -> None: ...

class Metric(_message.Message):
    __slots__ = ["name", "path", "column_name", "column_path", "table_name", "table_path", "schema_name", "schema_path", "db_name", "user_id", "db_user", "end_user_id", "end_user_db_username", "app_type", "datastore_id", "datastore_name", "ts", "counter", "returned_rows", "ip_address", "data_label", "data_labels", "datastore_technology", "bucket"]
    NAME_FIELD_NUMBER: _ClassVar[int]
    PATH_FIELD_NUMBER: _ClassVar[int]
    COLUMN_NAME_FIELD_NUMBER: _ClassVar[int]
    COLUMN_PATH_FIELD_NUMBER: _ClassVar[int]
    TABLE_NAME_FIELD_NUMBER: _ClassVar[int]
    TABLE_PATH_FIELD_NUMBER: _ClassVar[int]
    SCHEMA_NAME_FIELD_NUMBER: _ClassVar[int]
    SCHEMA_PATH_FIELD_NUMBER: _ClassVar[int]
    DB_NAME_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    DB_USER_FIELD_NUMBER: _ClassVar[int]
    END_USER_ID_FIELD_NUMBER: _ClassVar[int]
    END_USER_DB_USERNAME_FIELD_NUMBER: _ClassVar[int]
    APP_TYPE_FIELD_NUMBER: _ClassVar[int]
    DATASTORE_ID_FIELD_NUMBER: _ClassVar[int]
    DATASTORE_NAME_FIELD_NUMBER: _ClassVar[int]
    TS_FIELD_NUMBER: _ClassVar[int]
    COUNTER_FIELD_NUMBER: _ClassVar[int]
    RETURNED_ROWS_FIELD_NUMBER: _ClassVar[int]
    IP_ADDRESS_FIELD_NUMBER: _ClassVar[int]
    DATA_LABEL_FIELD_NUMBER: _ClassVar[int]
    DATA_LABELS_FIELD_NUMBER: _ClassVar[int]
    DATASTORE_TECHNOLOGY_FIELD_NUMBER: _ClassVar[int]
    BUCKET_FIELD_NUMBER: _ClassVar[int]
    name: str
    path: str
    column_name: str
    column_path: str
    table_name: str
    table_path: str
    schema_name: str
    schema_path: str
    db_name: str
    user_id: str
    db_user: str
    end_user_id: str
    end_user_db_username: str
    app_type: str
    datastore_id: str
    datastore_name: str
    ts: _timestamp_pb2.Timestamp
    counter: int
    returned_rows: int
    ip_address: str
    data_label: str
    data_labels: _containers.RepeatedScalarFieldContainer[str]
    datastore_technology: str
    bucket: _timestamp_pb2.Timestamp
    def __init__(self, name: _Optional[str] = ..., path: _Optional[str] = ..., column_name: _Optional[str] = ..., column_path: _Optional[str] = ..., table_name: _Optional[str] = ..., table_path: _Optional[str] = ..., schema_name: _Optional[str] = ..., schema_path: _Optional[str] = ..., db_name: _Optional[str] = ..., user_id: _Optional[str] = ..., db_user: _Optional[str] = ..., end_user_id: _Optional[str] = ..., end_user_db_username: _Optional[str] = ..., app_type: _Optional[str] = ..., datastore_id: _Optional[str] = ..., datastore_name: _Optional[str] = ..., ts: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., counter: _Optional[int] = ..., returned_rows: _Optional[int] = ..., ip_address: _Optional[str] = ..., data_label: _Optional[str] = ..., data_labels: _Optional[_Iterable[str]] = ..., datastore_technology: _Optional[str] = ..., bucket: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class Node(_message.Message):
    __slots__ = ["id", "type", "shape", "color", "label"]
    ID_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    SHAPE_FIELD_NUMBER: _ClassVar[int]
    COLOR_FIELD_NUMBER: _ClassVar[int]
    LABEL_FIELD_NUMBER: _ClassVar[int]
    id: str
    type: str
    shape: str
    color: str
    label: str
    def __init__(self, id: _Optional[str] = ..., type: _Optional[str] = ..., shape: _Optional[str] = ..., color: _Optional[str] = ..., label: _Optional[str] = ...) -> None: ...

class Link(_message.Message):
    __slots__ = ["source", "target"]
    SOURCE_FIELD_NUMBER: _ClassVar[int]
    TARGET_FIELD_NUMBER: _ClassVar[int]
    source: str
    target: str
    def __init__(self, source: _Optional[str] = ..., target: _Optional[str] = ...) -> None: ...

class GetMetricsResponse(_message.Message):
    __slots__ = ["metrics", "nodes", "links"]
    METRICS_FIELD_NUMBER: _ClassVar[int]
    NODES_FIELD_NUMBER: _ClassVar[int]
    LINKS_FIELD_NUMBER: _ClassVar[int]
    metrics: _containers.RepeatedCompositeFieldContainer[Metric]
    nodes: _containers.RepeatedCompositeFieldContainer[Node]
    links: _containers.RepeatedCompositeFieldContainer[Link]
    def __init__(self, metrics: _Optional[_Iterable[_Union[Metric, _Mapping]]] = ..., nodes: _Optional[_Iterable[_Union[Node, _Mapping]]] = ..., links: _Optional[_Iterable[_Union[Link, _Mapping]]] = ...) -> None: ...
