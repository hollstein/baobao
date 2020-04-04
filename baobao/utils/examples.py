from time import sleep
import pandas as pd

t_sleep = 3.0

def load_1():
    sleep(t_sleep)
    print("Load 1")
    return pd.DataFrame(data={"c1":list(range(10))})

def load_2():
    sleep(t_sleep)
    print("Load 2")
    return pd.DataFrame(data={"c2":[c**2 for c in range(10)]})

def load_3():
    sleep(t_sleep)
    print("Load 3")
    return pd.DataFrame(data={"c3":[c**2 / 2 for c in range(10)]})

def load_4():
    sleep(t_sleep)
    print("Load 4")
    return pd.DataFrame(data={"c4":[c-1 for c in range(10)]})

def load_5():
    sleep(t_sleep)
    print("Load 5")
    return pd.DataFrame(data={"c5":[c*2 for c in range(10)]})

def load_6():
    sleep(t_sleep)
    print("Load 6")
    return pd.DataFrame(data={"c6":[c*2/4 for c in range(10)]})