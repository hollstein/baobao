from typing import Dict
from asciitree.drawing import BoxStyle, BOX_DOUBLE
from asciitree import LeftAligned
from collections import OrderedDict as OD

from baobao import Pipeline, Step
from baobao.pipeline import str_


def print_pipeline(pipeline: Pipeline) -> None:
    def tree_pipeline(pipeline: pipeline) -> Dict:
        return {
            f"pipeline << {pipeline.root_node.__name__}": OD([
                (f"Step {ii}:{step.func.__name__}", tree_step(step))
                for ii, step in enumerate(pipeline.pipeline)
            ])}

    def tree_step(step: Step) -> Dict:
        return {
            f"{kk}{'' if isinstance(vv, Pipeline) else ' = ' + str_(vv)}":
                tree_pipeline(vv) if isinstance(vv, Pipeline) else {}
            for kk, vv in {
                **{str(ii): arg for ii, arg in enumerate(step.args)},
                **step.kwargs
            }.items()
        }

    print(LeftAligned(
        draw=BoxStyle(gfx=BOX_DOUBLE, horiz_len=2)
    )(tree_pipeline(pipeline)))
