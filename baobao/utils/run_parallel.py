from multiprocessing import Pool
from multiprocessing.pool import ApplyResult
from typing import Union
import logging

from ..pipeline import Pipeline, Step


def run_parallel(pipeline: Pipeline, n_jobs: int = 2):
    def extraxt_pipelines_from_step(step: Step):
        return [extract_pipelines_from_pipeline(pp) for pp in (
                [arg for arg in step.args if isinstance(arg, Pipeline)] +
                [arg for _, arg in step.kwargs.items() if isinstance(arg, Pipeline)]
        )]

    def extract_pipelines_from_pipeline(pipeline: Pipeline):
        return [extraxt_pipelines_from_step(step) for step in pipeline.pipeline]

    def parse_pipeline(pipeline: Pipeline) -> Pipeline:
        pipeline.pipeline = [parse_step(step) for step in pipeline.pipeline]
        return pipeline

    def parse_arg(arg):
        return itter_or_submitt_pipeline(arg) if isinstance(arg, Pipeline) else arg

    def itter_or_submitt_pipeline(pipeline: Pipeline) -> Union[Pipeline, ApplyResult]:
        if len(extract_pipelines_from_pipeline(pipeline)) == 0:
            logging.info(f"Submit: {str(pipeline)} to: {str(pl)}")
            return pl.apply_async(pipeline)
        else:
            return parse_pipeline(pipeline)

    def parse_step(step):
        step.arg = [parse_arg(arg) for arg in step.args]
        step.kwargs = {k: parse_arg(v) for k, v in step.kwargs.items()}
        return step

    with Pool(n_jobs) as pl:
        return parse_pipeline(pipeline).run()