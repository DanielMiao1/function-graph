# graph.py linear function example

from graph import *

def quadratic_function(arr):
	list_ = []
	for x in arr:
		for y in arr:
			list_.append(y)

graph(quadratic_function, samples=500)
