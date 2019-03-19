# linkstate.py
# contains the Link State info for a local link state
import numpy as np

class LinkState:
	def _init_(self, IP):
		self.IP = IP
		self.mapping = {0: self.IP}
		self.LSDB = {0: 0}

	def addNeighbor(self, neigh_IP):
		self.mapping[len(self.mapping)+1] = neigh_IP
	
	def updateNeighborDelay(self, neigh_index, delay):
		self.mapping[neigh_index] = delay
	
	def mapping2Matrix(self):
		mappingMatrix = np.array([])
		for key, elem in self.mapping:
			newrow = np.array([key, elem])
			mappingMatrix = np.vstack([mappingMatrix, new_row])
		return mappingMatrix
		
	def lsdb2Matrix(self):
		lsdbMatrix = np.array([])
		for key, elem in self.LSDB:
			newrow = np.array([key, elem])
			lsdbMatrix = np.vstack([lsdbMatrix, new_row])
		return lsdbMatrix
	
	def getMapping(self):
		return self.mapping
	
	def getLSDB(self):
		return self.LSDB