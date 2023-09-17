# module1.py
def function1():
    return "Hello from function1"



"""
Test: Manager sends messages to workers which print they have received.

Run on at least two processors:
eg. For 4 processors:
mpiexec -np 2 module_mpi4py_1.py
"""

if __name__ == "__main__":
  function1()