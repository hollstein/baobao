![image.png](notebooks/baobao_logo.png)

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





<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>c1</th>
      <th>c2</th>
      <th>c3</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>0</td>
      <td>0</td>
      <td>0.0</td>
    </tr>
    <tr>
      <th>1</th>
      <td>1</td>
      <td>1</td>
      <td>0.5</td>
    </tr>
    <tr>
      <th>2</th>
      <td>2</td>
      <td>4</td>
      <td>2.0</td>
    </tr>
    <tr>
      <th>3</th>
      <td>3</td>
      <td>9</td>
      <td>4.5</td>
    </tr>
    <tr>
      <th>4</th>
      <td>4</td>
      <td>16</td>
      <td>8.0</td>
    </tr>
    <tr>
      <th>5</th>
      <td>5</td>
      <td>25</td>
      <td>12.5</td>
    </tr>
    <tr>
      <th>6</th>
      <td>6</td>
      <td>36</td>
      <td>18.0</td>
    </tr>
    <tr>
      <th>7</th>
      <td>7</td>
      <td>49</td>
      <td>24.5</td>
    </tr>
    <tr>
      <th>8</th>
      <td>8</td>
      <td>64</td>
      <td>32.0</td>
    </tr>
    <tr>
      <th>9</th>
      <td>9</td>
      <td>81</td>
      <td>40.5</td>
    </tr>
  </tbody>
</table>
</div>



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





<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>c1</th>
      <th>c2</th>
      <th>c3</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>0</td>
      <td>0</td>
      <td>0.0</td>
    </tr>
    <tr>
      <th>1</th>
      <td>1</td>
      <td>1</td>
      <td>0.5</td>
    </tr>
    <tr>
      <th>2</th>
      <td>2</td>
      <td>4</td>
      <td>2.0</td>
    </tr>
    <tr>
      <th>3</th>
      <td>3</td>
      <td>9</td>
      <td>4.5</td>
    </tr>
    <tr>
      <th>4</th>
      <td>4</td>
      <td>16</td>
      <td>8.0</td>
    </tr>
    <tr>
      <th>5</th>
      <td>5</td>
      <td>25</td>
      <td>12.5</td>
    </tr>
    <tr>
      <th>6</th>
      <td>6</td>
      <td>36</td>
      <td>18.0</td>
    </tr>
    <tr>
      <th>7</th>
      <td>7</td>
      <td>49</td>
      <td>24.5</td>
    </tr>
    <tr>
      <th>8</th>
      <td>8</td>
      <td>64</td>
      <td>32.0</td>
    </tr>
    <tr>
      <th>9</th>
      <td>9</td>
      <td>81</td>
      <td>40.5</td>
    </tr>
  </tbody>
</table>
</div>



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





<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>c1</th>
      <th>c2_x</th>
      <th>c3</th>
      <th>c4</th>
      <th>c2_y</th>
      <th>c5_x</th>
      <th>c6</th>
      <th>c5_y</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>0</td>
      <td>0</td>
      <td>0.0</td>
      <td>-1</td>
      <td>0</td>
      <td>0</td>
      <td>0.0</td>
      <td>0</td>
    </tr>
    <tr>
      <th>1</th>
      <td>1</td>
      <td>1</td>
      <td>0.5</td>
      <td>0</td>
      <td>1</td>
      <td>2</td>
      <td>0.5</td>
      <td>2</td>
    </tr>
    <tr>
      <th>2</th>
      <td>2</td>
      <td>4</td>
      <td>2.0</td>
      <td>1</td>
      <td>4</td>
      <td>4</td>
      <td>1.0</td>
      <td>4</td>
    </tr>
    <tr>
      <th>3</th>
      <td>3</td>
      <td>9</td>
      <td>4.5</td>
      <td>2</td>
      <td>9</td>
      <td>6</td>
      <td>1.5</td>
      <td>6</td>
    </tr>
    <tr>
      <th>4</th>
      <td>4</td>
      <td>16</td>
      <td>8.0</td>
      <td>3</td>
      <td>16</td>
      <td>8</td>
      <td>2.0</td>
      <td>8</td>
    </tr>
    <tr>
      <th>5</th>
      <td>5</td>
      <td>25</td>
      <td>12.5</td>
      <td>4</td>
      <td>25</td>
      <td>10</td>
      <td>2.5</td>
      <td>10</td>
    </tr>
    <tr>
      <th>6</th>
      <td>6</td>
      <td>36</td>
      <td>18.0</td>
      <td>5</td>
      <td>36</td>
      <td>12</td>
      <td>3.0</td>
      <td>12</td>
    </tr>
    <tr>
      <th>7</th>
      <td>7</td>
      <td>49</td>
      <td>24.5</td>
      <td>6</td>
      <td>49</td>
      <td>14</td>
      <td>3.5</td>
      <td>14</td>
    </tr>
    <tr>
      <th>8</th>
      <td>8</td>
      <td>64</td>
      <td>32.0</td>
      <td>7</td>
      <td>64</td>
      <td>16</td>
      <td>4.0</td>
      <td>16</td>
    </tr>
    <tr>
      <th>9</th>
      <td>9</td>
      <td>81</td>
      <td>40.5</td>
      <td>8</td>
      <td>81</td>
      <td>18</td>
      <td>4.5</td>
      <td>18</td>
    </tr>
  </tbody>
</table>
</div>



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





<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>c1</th>
      <th>c2_x</th>
      <th>c3</th>
      <th>c4</th>
      <th>c2_y</th>
      <th>c5_x</th>
      <th>c6</th>
      <th>c5_y</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>0</td>
      <td>0</td>
      <td>0.0</td>
      <td>-1</td>
      <td>0</td>
      <td>0</td>
      <td>0.0</td>
      <td>0</td>
    </tr>
    <tr>
      <th>1</th>
      <td>1</td>
      <td>1</td>
      <td>0.5</td>
      <td>0</td>
      <td>1</td>
      <td>2</td>
      <td>0.5</td>
      <td>2</td>
    </tr>
    <tr>
      <th>2</th>
      <td>2</td>
      <td>4</td>
      <td>2.0</td>
      <td>1</td>
      <td>4</td>
      <td>4</td>
      <td>1.0</td>
      <td>4</td>
    </tr>
    <tr>
      <th>3</th>
      <td>3</td>
      <td>9</td>
      <td>4.5</td>
      <td>2</td>
      <td>9</td>
      <td>6</td>
      <td>1.5</td>
      <td>6</td>
    </tr>
    <tr>
      <th>4</th>
      <td>4</td>
      <td>16</td>
      <td>8.0</td>
      <td>3</td>
      <td>16</td>
      <td>8</td>
      <td>2.0</td>
      <td>8</td>
    </tr>
    <tr>
      <th>5</th>
      <td>5</td>
      <td>25</td>
      <td>12.5</td>
      <td>4</td>
      <td>25</td>
      <td>10</td>
      <td>2.5</td>
      <td>10</td>
    </tr>
    <tr>
      <th>6</th>
      <td>6</td>
      <td>36</td>
      <td>18.0</td>
      <td>5</td>
      <td>36</td>
      <td>12</td>
      <td>3.0</td>
      <td>12</td>
    </tr>
    <tr>
      <th>7</th>
      <td>7</td>
      <td>49</td>
      <td>24.5</td>
      <td>6</td>
      <td>49</td>
      <td>14</td>
      <td>3.5</td>
      <td>14</td>
    </tr>
    <tr>
      <th>8</th>
      <td>8</td>
      <td>64</td>
      <td>32.0</td>
      <td>7</td>
      <td>64</td>
      <td>16</td>
      <td>4.0</td>
      <td>16</td>
    </tr>
    <tr>
      <th>9</th>
      <td>9</td>
      <td>81</td>
      <td>40.5</td>
      <td>8</td>
      <td>81</td>
      <td>18</td>
      <td>4.5</td>
      <td>18</td>
    </tr>
  </tbody>
</table>
</div>


