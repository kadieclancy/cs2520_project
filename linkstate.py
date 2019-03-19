# linkstate.py
# contains the Link State info for a local link state

class LinkState:
	def _init_(self, IP):
		self.IP = IP
		self.mapping = {0: self.IP}
		self.LSDB = {0: 0}

	def addNeighbor(self, neigh_IP):
		self.mapping[len(self.mapping)+1] = neigh_IP
	
	def updateNeighborDelay(self, neigh_index, delay)
		self.mapping[neigh_index] = delay