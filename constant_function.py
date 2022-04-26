# graph.py constant function example

from graph import *

def constant_function(arr):
	if not arr:
		return None
	return arr[0]

graph(constant_function)
