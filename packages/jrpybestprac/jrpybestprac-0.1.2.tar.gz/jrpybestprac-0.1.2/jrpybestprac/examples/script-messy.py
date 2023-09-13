# script-dirty.py
from pandas import *
def YourFunc(x):
  '''
  some function
  '''
  return DataFrame(x).agg(["mean", "std"])
YourFunc({"a":range(5),"b":range(5,10)})
