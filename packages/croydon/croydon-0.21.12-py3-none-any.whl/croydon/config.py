import tomllib
from typing import Literal, Optional, Self, List, Any
from pydantic import BaseModel, Field
from datetime import timedelta
from .types import CacheType, LogLevel


_DEFAULT_TIMEOUT = timedelta(seconds=1, milliseconds=100)
_DEFAULT_COOKIE_TTL = timedelta(days=90)


class SessionConfig(BaseModel):
    cookie: str = "_croydon_session_id"
    ttl: timedelta = _DEFAULT_COOKIE_TTL


class DatabaseConfig(BaseModel):
    uri: str = "mongodb://localhost:27017/test"
    timeout: timedelta = _DEFAULT_TIMEOUT


class LogConfig(BaseModel):
    level: LogLevel = "debug"
    filename: Optional[str] = None
    stdout: bool = True


class QueueConfig(BaseModel):
    type: Literal["mongo"] = "mongo"


class MongoQueueConfig(BaseModel):
    tasks_collection: str = "croydon_tasks"
    keep_done_tasks_for: timedelta = timedelta(days=30)
    cleanup_interval: timedelta = timedelta(hours=1)


class CacheConfig(BaseModel):
    level1: CacheType = "request_local"
    level2: CacheType = "memcached"


class MemcachedConfig(BaseModel):
    backends: List[str] = ["127.0.0.1:11211"]


class OAuthConfig(BaseModel):
    id: str
    secret: str
    authorize_url: str


class GeneralConfig(BaseModel):
    documents_per_page: int = 20


class BaseConfig(BaseModel):
    session: SessionConfig = Field(default_factory=SessionConfig)
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    logging: LogConfig = Field(default_factory=LogConfig)
    oauth: Optional[OAuthConfig] = Field(None)
    general: GeneralConfig = Field(default_factory=GeneralConfig)
    queue: QueueConfig = Field(default_factory=QueueConfig)
    mongo_queue: MongoQueueConfig = Field(default_factory=MongoQueueConfig)
    cache: CacheConfig = Field(default_factory=CacheConfig)
    memcached: MemcachedConfig = Field(default_factory=MemcachedConfig)

    @classmethod
    def parse(cls, filename) -> Self:
        with open(filename, "rb") as f:
            config = tomllib.load(f)
        return cls(**config)

    def get(self, key: str) -> Any:
        tokens = key.split(".")
        node = self
        while tokens:
            token = tokens.pop(0)
            try:
                node = getattr(node, token)
            except AttributeError:
                raise KeyError(f"key {key} does not exist")
        return node
    