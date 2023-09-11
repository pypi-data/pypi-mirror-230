from __future__ import annotations

import functools
from importlib import util
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
    List,
    Mapping,
    NamedTuple,
    Protocol,
    TypeVar,
    overload,
)

import toolz
from absl import app, flags, logging

from absl_extra.notifier import BaseNotifier, LoggingNotifier

T = TypeVar("T", bound=Callable)
FLAGS = flags.FLAGS

if util.find_spec("pymongo"):
    from pymongo import MongoClient  # noqa
    from pymongo.collection import Collection  # noqa
else:
    Collection = type(None)
    logging.warning("pymongo not installed.")

if TYPE_CHECKING:
    from absl_extra.callbacks import CallbackFn


class MongoConfig(NamedTuple):
    uri: str
    db_name: str
    collection: str


class _ExceptionHandlerImpl(app.ExceptionHandler):
    def __init__(self, name: str, notifier: BaseNotifier):
        self.name = name
        self.notifier = notifier

    def handle(self, exception: Exception) -> None:
        self.notifier.notify_task_failed(self.name, exception)


class _TaskFn(Protocol):
    def __call__(self, *, db: Collection = None, **kwargs) -> None:
        ...


_TASK_STORE: Dict[str, Callable[[...], None]] = dict()  # type: ignore


class NonExistentTaskError(RuntimeError):
    def __init__(self, task: str, task_flag: str):
        super().__init__(f"Unknown {task_flag} {task}, registered are {list(_TASK_STORE.keys())}")


@toolz.curry
def make_task_func(
    func: _TaskFn,
    *,
    name: str,
    notifier: BaseNotifier | Callable[[], BaseNotifier],
    init_callbacks: List[CallbackFn],
    post_callbacks: List[CallbackFn],
    db_factory=None,
) -> _TaskFn:
    _name = name

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        app.install_exception_handler(_ExceptionHandlerImpl(name, notifier))  # type: ignore
        kwargs = {}
        if db_factory is not None:
            db = db_factory()
            kwargs["db"] = db

        for hook in init_callbacks:
            hook(_name, notifier=notifier, **kwargs)

        func(*args, **kwargs)

        for hook in post_callbacks:
            hook(_name, notifier=notifier, **kwargs)

    return wrapper


@toolz.curry
@overload
def register_task(
    func: Callable[[Collection], None],
    *,
    notifier: BaseNotifier | Callable[[], BaseNotifier] | None = None,
    mongo_config: MongoConfig | Mapping[str, Any],
    init_callbacks: List[CallbackFn] | None = None,
    post_callbacks: List[CallbackFn] | None = None,
) -> Callable[[Callable[[Collection], None]], _TaskFn]:
    ...


@toolz.curry
@overload
def register_task(
    func: Callable[[], None],
    *,
    notifier: BaseNotifier | Callable[[], BaseNotifier] | None = None,
    mongo_config: None,
    init_callbacks: List[CallbackFn] | None = None,
    post_callbacks: List[CallbackFn] | None = None,
) -> Callable[[Callable[[], None]], _TaskFn]:
    ...


@toolz.curry
def register_task(
    func: Callable[[Collection], None] | Callable[[], None],
    *,
    name: str = "main",
    notifier: BaseNotifier | Callable[[], BaseNotifier] | None = None,
    mongo_config: MongoConfig | Mapping[str, Any] | None = None,
    init_callbacks: List[CallbackFn] | None = None,
    post_callbacks: List[CallbackFn] | None = None,
) -> Callable[[Callable[[Collection], None] | Callable[[], None]], _TaskFn]:
    """
    Parameters
    ----------

    func:
        Function to execute.
    name : str, optional
        The name of the task. Default is "main".
    notifier : BaseNotifier | Callable[[], BaseNotifier] | None, optional
        The notifier object or callable that returns a notifier object. Default is None.
    mongo_config : MongoConfig | Mapping[str, Any] | None, optional
        The configuration object for MongoDB or a mapping of configuration values. Default is None.
    init_callbacks : List[CallbackFn] | None, optional
        The list of callback functions to be executed during task initialization. Default is None.
    post_callbacks : List[CallbackFn] | None, optional
        The list of callback functions to be executed after the task completes. Default is None.

    Returns
    -------
    Callable[[_TaskFn], None]
        The decorator function that registers the task.
    """
    from absl_extra.callbacks import DEFAULT_INIT_CALLBACKS, DEFAULT_POST_CALLBACK

    if isinstance(notifier, Callable):  # type: ignore
        notifier = notifier()  # type: ignore
    if notifier is None:
        notifier = LoggingNotifier()

    kwargs = {}

    if util.find_spec("pymongo") and mongo_config is not None:
        if isinstance(mongo_config, Mapping):
            mongo_config = MongoConfig(**mongo_config)
        db_factory = lambda: (  # noqa
            MongoClient(mongo_config.uri).get_database(mongo_config.db_name).get_collection(mongo_config.collection)
        )
        kwargs["db_factory"] = db_factory

    if init_callbacks is None:
        init_callbacks = DEFAULT_INIT_CALLBACKS  # type: ignore

    if post_callbacks is None:
        post_callbacks = DEFAULT_POST_CALLBACK  # type: ignore

    _TASK_STORE[name] = make_task_func(
        name=name,
        notifier=notifier,
        init_callbacks=init_callbacks,
        post_callbacks=post_callbacks,
        **kwargs,
    )(func)

    return _TASK_STORE[name]


def run(argv: List[str] | None = None, task_flag: str = "task", **kwargs):
    """
    Parameters
    ----------
    argv:
        CLI args passed to absl.app.run
    task_flag:
        Name of the CLI flag used to identify which task to run.
    kwargs:
        Kwargs passed to entrypoint function.

    Returns
    -------

    """
    flags.DEFINE_string(task_flag, default="main", help="Name of the function to execute.")

    def select_main(_):
        task_name = getattr(FLAGS, task_flag)
        if task_name not in _TASK_STORE:
            raise NonExistentTaskError(task_name, task_flag)
        func = _TASK_STORE[task_name]
        func(**kwargs)

    app.run(select_main, argv=argv)
