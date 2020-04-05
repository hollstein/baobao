from dataclasses import dataclass
from copy import copy
from typing import Iterable, Union, Callable, Optional
from functools import singledispatch
import logging
from time import time
from multiprocessing.pool import ApplyResult

#######################
# optional dependencies
#######################

try:
    from joblib import Memory
except ImportError:
    logging.info("baobao: Missing joblib optional dependency, Step memoization will not work.")

    class Memory:
        pass

try:
    import pandas as pd
except ImportError:
    class pd:
        DataFrame = None


@dataclass
class PipelineOpts:
    """
    :param memory: Instance of joblib.Memory or anything that implements its API\n
    :param inplyce: True / False, if true the input is transformed, if false a copy is produced\n
    :push_options: True / False, if true, options of root pipeline are applied to all contained pipelines\n
    :param step_prefix: String to prefix steps, is repeated depending on depth within the complete pipeline\n
    :param pipeline_prefix:  String to prefix pipelines, is repeated depending on depth within the complete pipeline\n
    """
    memory: Optional[Memory] = None
    in_place: bool = True
    push_options: bool = False
    step_prefix = 4 * " "
    pipeline_prefix = ""


def _run(func: Callable, df: pd.DataFrame, *args, **kwargs):
    return func(df, *args, **kwargs)


class Step:
    """
        :param func: A function or callable that takes the result of a previous pipeline stet as
        input and transforms it as output of this step\n
        :param args: Positional arguments passed to func when called by pipeline\n
        :param kwargs: Keyword arguments passed to func when called by pipeline\n

    """

    def __init__(self, func: Callable, *args, **kwargs):

        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.pipeline_opts = None

    def __str__(self):

        def str_reduce(inp: str, allowed_length: int = 5) -> str:
            if len(inp) < allowed_length:
                return inp
            else:
                return f"{inp[:allowed_length]}[...]"

        def kv2str(kv: Iterable) -> str:
            return '='.join(map(lambda k: str_reduce(str_(k), allowed_length=20), kv))

        return (
            f"Step(func={self.func.__name__}"
            f",args=({','.join([str_reduce(str_(a)) for a in self.args])})"
            f",{','.join([kv2str(kv) for kv in self.kwargs.items()])})"
        )

    def set_options(self, opts):
        self.pipeline_opts = opts
        return self

    def push_options(self):

        opts = copy(self.pipeline_opts)
        opts.step_prefix = f"    {opts.step_prefix}"
        opts.pipeline_prefix = f"    {opts.pipeline_prefix}"

        def _pp(inp):
            if isinstance(inp, Pipeline):
                inp.opts = opts
                return inp
            else:
                return inp

        self.args = [_pp(arg) for arg in self.args]
        self.kwargs = {k: _pp(v) for k, v in self.kwargs.items()}

    def _run_pipelines_for_args_kwargs(self):

        def _run_if_pipeline(inp):
            return inp.get() if any([isinstance(inp, cl) for cl in (Pipeline, ApplyResult)]) else inp

        self.args = [_run_if_pipeline(arg) for arg in self.args]
        self.kwargs = {k: _run_if_pipeline(v) for k, v in self.kwargs.items()}

    def run(self, df: pd.DataFrame) -> pd.DataFrame:

        self._run_pipelines_for_args_kwargs()
        return (self.pipeline_opts.memory.cache(_run) if self.pipeline_opts.memory is not None else _run)(
            self.func, df, *self.args, **self.kwargs)


class Pipeline:
    """
    :param root_node: Callable or initial input data to run the pipeline\n
    :param pipeline: Iterable composed of baobao.Step instances\n
    :param opts: Instance of baobao.PipelineOpts\n
    """

    def __init__(
            self, root_node: Union[pd.DataFrame, Callable], pipeline: Iterable[Step] = tuple(),
            opts: PipelineOpts = PipelineOpts()
    ):
        self.root_node = root_node
        self.opts = opts
        self.pipeline = pipeline
        self.__name__ = str(self)

    def __str__(self):
        return f"Pipeline(root_node={str_(self.root_node)},memory={str(self.opts.memory)})"

    def run(self):
        return self.__call__()

    def get(self):
        return self.__call__()

    def __call__(self):

        t0 = time()
        logging.info(f"{self.opts.pipeline_prefix}{str(self)}")

        self.pipeline = [step.set_options(self.opts) for step in self.pipeline]

        if self.opts.push_options:
            for step in self.pipeline:
                step.push_options()

        # if memory given and root_node is callable, replace by memorized version
        root_node = (
            self.opts.memory.cache(self.root_node)
            if callable(self.root_node) and self.opts.memory is not None else self.root_node
        )
        # materialize root_node
        root_node = root_node() if callable(root_node) else root_node
        df = root_node if self.opts.in_place is True else root_node.copy()
        for ii, step in enumerate(self.pipeline):
            logging.info(f"{self.opts.step_prefix}{str(step)}")
            df = step.run(df)
        logging.info(f"{self.opts.pipeline_prefix}Complete pipeline after {(time()-t0):.2f}s")

        return df


@singledispatch
def str_(inp):
    if callable(inp):
        return f"{inp.__name__}()"
    else:
        return str(inp)[:40]


@str_.register
def _(inp: pd.DataFrame):
    return f"DataFrame shape:{inp.shape}, columns:{str(list(inp.columns))[:50]}"


@str_.register
def _(inp: bool):
    return f"{inp}"
