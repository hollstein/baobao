![image.png](https://github.com/hollstein/baobao/raw/dev/notebooks/baobao_logo.png)

Baobao is a small library that attempts writing and maintaining data pipelines easier. It was written with Pandas in mind, but is not limited to it or even depends on it. It's AIP closely models Pandas pipe functionality.

Design principles are:
- Simple in the core
- Minimal dependencies
- Additional functionality is optional

Pipelines can be build like this:


```python
import pandas as pd
from baobao import Pipeline  # To define pipelines
from baobao import Step  # Pipelines are build from Steps which may contain Pipelines

# some functions that return pd.Dataframes to play with
from baobao.utils.examples import load_1, load_2, load_3

Pipeline(
    root_node=load_1,  # We have to start somewhere, could be any object or callable
    pipeline=(  # Pipelines are build from Steps
        Step(
            # Each Step is build from a function that takes 
            # the output of the previous Step as input in 
            # the first argument
            func=pd.merge,
            # Any argoments to [func] can be given
            left_index=True, right_index=True,
            right=Pipeline(load_2),  # including additional Pipelines
        ),
        Step(func=pd.merge, right=Pipeline(load_3), left_index=True, right_index=True),
    )
).run()  # Call the run method to actually run the pipeline, enjoy some logging out of the box
```
    INFO:root:Pipeline(root_node=load_1(),memory=None)
    INFO:root:    Step(func=merge,args=(),left_index=True,right_index=True,right=Pipeline(root_node=l[...])
    INFO:root:Pipeline(root_node=load_2(),memory=None)
    Load 1
    INFO:root:Complete pipeline after 3.02s
    INFO:root:    Step(func=merge,args=(),right=Pipeline(root_node=l[...],left_index=True,right_index=True)
    INFO:root:Pipeline(root_node=load_3(),memory=None)
    Load 2
    INFO:root:Complete pipeline after 3.02s
    INFO:root:Complete pipeline after 9.06s
    Load 3



A neat way of speeding this up is caching results to disk:


```python
# Baobao doesn't depend on any caching but respects Joblibs 
# API in case you want to chose some other caching strategy  
from joblib import Memory

# Baobao options are separated into a dedicated object in
# order to make it simple to push options down to Pipelines
# included in Steps of the root Pipeline
from baobao import PipelineOpts

# Define the pipeline:
pipeline = Pipeline(
    root_node=load_1,
    opts=PipelineOpts(
        memory=Memory("./cache", verbose=0),
        push_options=True  # Pushing options down to included Pipelines
    ),
    pipeline=(
        Step(func=pd.merge, right=Pipeline(load_2), left_index=True, right_index=True),
        Step(func=pd.merge, right=Pipeline(load_3), left_index=True, right_index=True),
    )
)
# Run the pipeline:
pipeline.run()
```

    INFO:root:Pipeline(root_node=load_1(),memory=Memory(location=./cache/joblib))
    INFO:root:    Step(func=merge,args=(),right=Pipeline(root_node=l[...],left_index=True,right_index=True)
    INFO:root:    Pipeline(root_node=load_2(),memory=Memory(location=./cache/joblib))
    INFO:root:    Complete pipeline after 0.00s
    INFO:root:    Step(func=merge,args=(),right=Pipeline(root_node=l[...],left_index=True,right_index=True)
    INFO:root:    Pipeline(root_node=load_3(),memory=Memory(location=./cache/joblib))
    INFO:root:    Complete pipeline after 0.01s
    INFO:root:Complete pipeline after 0.04s

Reasoning over pipelines might be simpler with this printing utility:


```python
from baobao.utils import print_pipeline
print_pipeline(pipeline)
```

    pipeline << load_1
     ╠══ Step 0:merge
     ║   ╠══ right = DataFrame shape:(10, 1), columns:['c2']
     ║   ╠══ left_index = True
     ║   ╚══ right_index = True
     ╚══ Step 1:merge
         ╠══ right = DataFrame shape:(10, 1), columns:['c3']
         ╠══ left_index = True
         ╚══ right_index = True


Printing can be adjusted using the multiple dispatch pattern:


```python
from baobao.pipeline import str_
@str_.register
def _(inp: pd.DataFrame):
    return f"DataFrame(shape:{inp.shape})"
@str_.register
def _(inp: bool):
    return f"Bool:{inp}"

print_pipeline(pipeline)
```

    pipeline << load_1
     ╠══ Step 0:merge
     ║   ╠══ right = DataFrame(shape:(10, 1))
     ║   ╠══ left_index = Bool:True
     ║   ╚══ right_index = Bool:True
     ╚══ Step 1:merge
         ╠══ right = DataFrame(shape:(10, 1))
         ╠══ left_index = Bool:True
         ╚══ right_index = Bool:True


A little more depth added:


```python
from baobao.utils.examples import *  # Import more load_X functions

def mk_pipeline():  # get fresh pipeline each time we call this function
    return Pipeline(
        root_node=load_1,
        opts=PipelineOpts(
            memory=None,#Memory("./cache", verbose=0),
            push_options=True
        ),
        pipeline=(
            Step(func=pd.merge, left_index=True, right_index=True, right=Pipeline(load_2)),
            Step(func=pd.merge, left_index=True, right_index=True, right=Pipeline(
                root_node=load_3,
                pipeline=(
                    Step(func=pd.merge, left_index=True, right_index=True, right=Pipeline(load_4)),
                    Step(func=pd.merge, left_index=True, right_index=True, right=Pipeline(
                        root_node=load_2,
                        pipeline=(
                            Step(func=pd.merge, left_index=True, right_index=True, right=Pipeline(load_5)),
                            Step(func=pd.merge, left_index=True, right_index=True, right=Pipeline(load_6)),
                        )
                    )),
                ))
                ),
            Step(func=pd.merge, left_index=True, right_index=True, right=Pipeline(load_5)),
        )
    )
```

Lets print this one again:


```python
print_pipeline(mk_pipeline())
```

    pipeline << load_1
     ╠══ Step 0:merge
     ║   ╠══ left_index = Bool:True
     ║   ╠══ right_index = Bool:True
     ║   ╚══ right
     ║       ╚══ pipeline << load_2
     ╠══ Step 1:merge
     ║   ╠══ left_index = Bool:True
     ║   ╠══ right_index = Bool:True
     ║   ╚══ right
     ║       ╚══ pipeline << load_3
     ║           ╠══ Step 0:merge
     ║           ║   ╠══ left_index = Bool:True
     ║           ║   ╠══ right_index = Bool:True
     ║           ║   ╚══ right
     ║           ║       ╚══ pipeline << load_4
     ║           ╚══ Step 1:merge
     ║               ╠══ left_index = Bool:True
     ║               ╠══ right_index = Bool:True
     ║               ╚══ right
     ║                   ╚══ pipeline << load_2
     ║                       ╠══ Step 0:merge
     ║                       ║   ╠══ left_index = Bool:True
     ║                       ║   ╠══ right_index = Bool:True
     ║                       ║   ╚══ right
     ║                       ║       ╚══ pipeline << load_5
     ║                       ╚══ Step 1:merge
     ║                           ╠══ left_index = Bool:True
     ║                           ╠══ right_index = Bool:True
     ║                           ╚══ right
     ║                               ╚══ pipeline << load_6
     ╚══ Step 2:merge
         ╠══ left_index = Bool:True
         ╠══ right_index = Bool:True
         ╚══ right
             ╚══ pipeline << load_5


and run it in a sequential manner:


```python
mk_pipeline().run()
```
    INFO:root:Pipeline(root_node=load_1(),memory=None)
    INFO:root:    Step(func=merge,args=(),left_index=Bool:True,right_index=Bool:True,right=Pipeline(root_node=l[...])
    INFO:root:    Pipeline(root_node=load_2(),memory=None)
    Load 1
    INFO:root:    Complete pipeline after 3.01s
    INFO:root:    Step(func=merge,args=(),left_index=Bool:True,right_index=Bool:True,right=Pipeline(root_node=l[...])
    INFO:root:    Pipeline(root_node=load_3(),memory=None)
    Load 2
    INFO:root:        Step(func=merge,args=(),left_index=Bool:True,right_index=Bool:True,right=Pipeline(root_node=l[...])
    INFO:root:        Pipeline(root_node=load_4(),memory=None)
    Load 3
    INFO:root:        Complete pipeline after 3.02s
    INFO:root:        Step(func=merge,args=(),left_index=Bool:True,right_index=Bool:True,right=Pipeline(root_node=l[...])
    INFO:root:        Pipeline(root_node=load_2(),memory=None)
    Load 4
    INFO:root:            Step(func=merge,args=(),left_index=Bool:True,right_index=Bool:True,right=Pipeline(root_node=l[...])
    INFO:root:            Pipeline(root_node=load_5(),memory=None)
    Load 2
    INFO:root:            Complete pipeline after 3.01s
    INFO:root:            Step(func=merge,args=(),left_index=Bool:True,right_index=Bool:True,right=Pipeline(root_node=l[...])
    INFO:root:            Pipeline(root_node=load_6(),memory=None)
    Load 5
    INFO:root:            Complete pipeline after 3.01s
    INFO:root:        Complete pipeline after 9.05s
    INFO:root:    Complete pipeline after 15.10s
    INFO:root:    Step(func=merge,args=(),left_index=Bool:True,right_index=Bool:True,right=Pipeline(root_node=l[...])
    INFO:root:    Pipeline(root_node=load_5(),memory=None)
    Load 6
    INFO:root:    Complete pipeline after 3.01s
    INFO:root:Complete pipeline after 24.15s
    Load 5

We can speed things up by submitting those pipelines that do not contain further pipelines to a multiprocess Pool and enjoy some nice speedups:


```python
from baobao.utils import run_parallel

run_parallel(mk_pipeline(), n_jobs=4)
```

    INFO:root:Submit: Pipeline(root_node=load_2(),memory=None) to: <multiprocessing.pool.Pool state=RUN pool_size=4>
    INFO:root:Submit: Pipeline(root_node=load_4(),memory=None) to: <multiprocessing.pool.Pool state=RUN pool_size=4>
    INFO:root:Submit: Pipeline(root_node=load_5(),memory=None) to: <multiprocessing.pool.Pool state=RUN pool_size=4>
    INFO:root:Pipeline(root_node=load_2(),memory=None)
    INFO:root:Submit: Pipeline(root_node=load_6(),memory=None) to: <multiprocessing.pool.Pool state=RUN pool_size=4>
    INFO:root:Pipeline(root_node=load_4(),memory=None)
    INFO:root:Submit: Pipeline(root_node=load_5(),memory=None) to: <multiprocessing.pool.Pool state=RUN pool_size=4>
    INFO:root:Pipeline(root_node=load_1(),memory=None)
    INFO:root:Pipeline(root_node=load_5(),memory=None)
    INFO:root:Pipeline(root_node=load_6(),memory=None)
    Load 4
    Load 2
    INFO:root:    Step(func=merge,args=(),left_index=Bool:True,right_index=Bool:True,right=<multiprocessing.poo[...])
    Load 6
    INFO:root:Complete pipeline after 3.04s
    Load 5
    INFO:root:Pipeline(root_node=load_5(),memory=None)
    INFO:root:Complete pipeline after 3.04s
    INFO:root:Complete pipeline after 3.06s
    INFO:root:Complete pipeline after 3.06s
    INFO:root:    Step(func=merge,args=(),left_index=Bool:True,right_index=Bool:True,right=Pipeline(root_node=l[...])
    INFO:root:    Pipeline(root_node=load_3(),memory=None)
    Load 1
    Load 5
    INFO:root:Complete pipeline after 3.02s
    INFO:root:        Step(func=merge,args=(),left_index=Bool:True,right_index=Bool:True,right=<multiprocessing.poo[...])
    INFO:root:        Step(func=merge,args=(),left_index=Bool:True,right_index=Bool:True,right=Pipeline(root_node=l[...])
    INFO:root:        Pipeline(root_node=load_2(),memory=None)
    Load 3
    INFO:root:            Step(func=merge,args=(),left_index=Bool:True,right_index=Bool:True,right=<multiprocessing.poo[...])
    INFO:root:            Step(func=merge,args=(),left_index=Bool:True,right_index=Bool:True,right=<multiprocessing.poo[...])
    INFO:root:        Complete pipeline after 3.02s
    INFO:root:    Complete pipeline after 6.04s
    INFO:root:    Step(func=merge,args=(),left_index=Bool:True,right_index=Bool:True,right=<multiprocessing.poo[...])
    INFO:root:Complete pipeline after 9.15s
    Load 2
