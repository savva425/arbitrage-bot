# Class to represent a graph 
class Graph: 
	def __init__(self, vertices): 
		self.V = vertices # No. of vertices 
		self.graph = [] # default dictionary to store graph 

	# function to add an edge to graph 
	def addEdge(self, u, v, w): 
		self.graph.append([u, v, w]) 

	# utility function used to print the solution 
	def getDist(self, dist): 
		print("Vertex Distance from Source") 
		for i in range(self.V): 
			print("% d \t\t % d" % (i, dist[i])) 
	def getPred(self, to):
		return self.pred[to]

	# The main function that finds shortest distances from src to 
	# all other vertices using Bellman-Ford algorithm. The function 
	# also detects negative weight cycle 
	def BellmanFord(self, src): 
		# Step 1: Initialize distances from src to all other vertices 
		# as INFINITE 
		pred = [src] * self.V
		dist = [float("Inf")] * self.V
		dist[src] = 0


		# Step 2: Relax all edges |V| - 1 times. A simple shortest 
		# path from src to any other vertex can have at-most |V| - 1 
		# edges 
		# тут убрал для проверки
			# Update dist value and parent index of the adjacent vertices of 
			# the picked vertex. Consider only those vertices which are still in 
			# queue
		for i in range(self.V - 1): 
			for u, v, w in self.graph: 
				if dist[u] != float("Inf") and dist[u] + w < dist[v]: 
						dist[v] = dist[u] + w
		# Step 3: check for negative-weight cycles. The above step 
		# guarantees shortest distances if graph doesn't contain 
		# negative weight cycle. If we get a shorter path, then there 
		# is a cycle.

		#self.getDist(dist)

		for u, v, w in self.graph: 
			if dist[u] != float("Inf") and dist[u] + w < dist[v]: 
				dist[v] = dist[u] + w
				pred[v] = u
		self.pred = pred