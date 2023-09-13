# datatool-python

A python library that contains a number of useful functions and approaches
for a data scientist. It includes time measurement tool, map-reduce,
clasterization on CUDA,
[LCS](https://en.wikipedia.org/wiki/Longest_common_subsequence_problem)
and so on. Look through the source code for details.

## Install

```
pip install datatool-python
```

## Use example

```python
from time import sleep
from datatool.time import Meter

with Meter() as tm:
    sleep(1.5)

print(tm.duration())  # Prints the measured duration of the body in with-statement (around 1.5)
```
