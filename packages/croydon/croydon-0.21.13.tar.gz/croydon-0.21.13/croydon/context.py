import logging
import logging.handlers
import os
import sys
import importlib
from logging import Logger, getLogger
from typing import Generic, TypeVar, Type, Optional
from .types import CacheType
from .config import BaseConfig
from .types import TConfigType
from .taskq.types import TBaseQueue
from .cache import TCache, NoCache, SimpleCache, MemcachedCache, RequestLocalCache
from .db import DB
from .errors import ConfigurationError

_LOG_LEVELS = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warning": logging.WARNING,
    "error": logging.ERROR,
    "critical": logging.CRITICAL,
}

C = TypeVar("C", bound=BaseConfig)
CT = Type[C]


def _get_config_class() -> TConfigType:
    try:
        module = importlib.import_module("app.config")
        config_class = module.__dict__["Config"]
    except (ModuleNotFoundError, KeyError):
        raise RuntimeError("module app.config must be defined and contain a Config class")

    return config_class


def _get_project_dir() -> str:
    try:
        module = importlib.import_module("app.config")
    except ModuleNotFoundError:
        raise RuntimeError("module app.config must be defined and contain a Config class")

    file_dir = os.path.dirname(module.__file__)
    project_dir = os.path.abspath(os.path.join(file_dir, ".."))
    return project_dir


# To avoid initialization issues Context must be fully synchronous
# i.e. no properties requiring async initialization are allowed.
class Context(Generic[C]):
    _cfg: Optional[C] = None
    _log: Optional[Logger] = None
    _queue: Optional[TBaseQueue] = None
    _cache_l1: Optional[TCache] = None
    _cache_l2: Optional[TCache] = None
    _db: DB = None
    _project_dir: Optional[str] = None

    @property
    def initialised(self) -> bool:
        return self._project_dir is not None

    @property
    def project_dir(self) -> str:
        if self._project_dir is None:
            self.autosetup()
        return self._project_dir

    @property
    def cfg(self) -> C:
        if self._cfg is None:
            self.autosetup()
        return self._cfg

    @property
    def log(self) -> Logger:
        if self._log is None:
            self.autosetup()
        return self._log

    @property
    def queue(self) -> TBaseQueue:
        if self._queue is None:
            self.autosetup()
        return self._queue

    @property
    def cache_l1(self) -> TCache:
        if self._cache_l1 is None:
            self.autosetup()
        return self._cache_l1

    @property
    def cache_l2(self) -> TCache:
        if self._cache_l2 is None:
            self.autosetup()
        return self._cache_l2

    @property
    def db(self) -> DB:
        if self._db is None:
            self.autosetup()
        return self._db

    def from_config(self, config: C, project_dir: Optional[str] = None):
        self._project_dir = project_dir if project_dir else _get_project_dir()
        self._cfg = config
        self.setup()

    def autosetup(self):
        self._project_dir = _get_project_dir()
        cfgcls = _get_config_class()
        config_filename = os.getenv("CROYDON_CONFIG", "application.toml")
        if not os.path.isfile(config_filename):
            config_filename = os.path.join(self._project_dir, config_filename)
        self._cfg = cfgcls.parse(config_filename)
        self.setup()

    def set_project_dir(self, project_dir: str):
        self._project_dir = project_dir

    def setup(self) -> None:
        self._setup_logging()
        self._setup_cache()
        self._setup_db()  # needs logging and cache
        self._setup_queue()  # needs db

    def _setup_db(self):
        self._db = DB(
            config=self._cfg.database,
            mock=False,
        )

    def _setup_cache(self):
        for prop in ["level1", "level2"]:
            cache_type: CacheType = getattr(self._cfg.cache, prop)

            if cache_type == "none":
                cache = NoCache()
            elif cache_type == "simple":
                cache = SimpleCache()
            elif cache_type == "memcached":
                backends = self._cfg.memcached.backends
                cache = MemcachedCache(backends)
            elif cache_type == "request_local":
                cache = RequestLocalCache()
            else:
                raise ConfigurationError(f"invalid cache type {cache_type}")

            if prop == "level1":
                self._cache_l1 = cache
            else:
                self._cache_l2 = cache

    def _setup_queue(self):
        if self._cfg.queue.type == "mongo":
            from .taskq.mongo_queue import MongoQueue
            self._queue = MongoQueue(self._cfg.mongo_queue)
        else:
            raise TypeError(f"queue type {self._cfg.queue.type} is invalid")

    def _setup_logging(self):
        logger = getLogger(__name__)
        logger.propagate = False

        lvl = _LOG_LEVELS.get(
            self._cfg.logging.level.lower(),
            logging.DEBUG
        )
        logger.setLevel(lvl)

        for handler in logger.handlers:
            logger.removeHandler(handler)

        log_format = logging.Formatter(
            "[%(asctime)s] %(levelname)s %(filename)s:%(lineno)d %(message)s"
        )

        if self._cfg.logging.stdout:
            handler = logging.StreamHandler(stream=sys.stdout)
            handler.setLevel(lvl)
            handler.setFormatter(log_format)
            logger.addHandler(handler)

        if self._cfg.logging.filename is not None:
            handler = logging.handlers.WatchedFileHandler(self.cfg.logging.filename)
            handler.setLevel(lvl)
            handler.setFormatter(log_format)
            logger.addHandler(handler)

        self._log = logger


ctx = Context()
