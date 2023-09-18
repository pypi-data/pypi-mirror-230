__all__ = (
    "make_run",
    "run_subprocesses",
)

import typing
from functools import wraps

if typing.TYPE_CHECKING:
    from . import context
    from .sub_processors import BaseSubprocessor


def run_subprocesses(
    processor: "BaseSubprocessor",
    context_instance: "context.BaseProcessorContext",
) -> typing.Any:  # noqa: ANN401
    processor.context = context_instance
    return processor()


def make_run(run_func):
    @wraps(run_func)
    def run_wrapper(self, *args, **kwargs):
        for pre_proc in self.pre_run:
            self.results.pre_run[pre_proc] = run_subprocesses(pre_proc, self.context)
        self.results.run = run_func(self, *args, **kwargs)
        for post_proc in self.post_run:
            self.results.post_run[post_proc] = run_subprocesses(post_proc, self.context)
        return self.results.run

    return run_wrapper
