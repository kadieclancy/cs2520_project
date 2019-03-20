# linkstate.py
# contains the Link State info for a local link state
import numpy as np

class LinkState:
	def _init_(self, IP, port):
		self.IP = IP
		self.port = port
		self.mapping = {0: self.IP}
		self.LSDB = {0: 0}

	def addNeighbor(self, neigh_IP, port):
		map_num = len(self.mapping) + 1
		self.mapping[neigh_IP + port] = map_num
		self.LSDB[map_num] = [1]
		print('neighbor added to link state')
	
	def updateNeighborDelay(self, neigh_index, delay):
		self.mapping[neigh_index] = delay + 1 # for now bc no delay
	
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
		
	def ip2MapNum(self, IP, port):
		map_num = self.mapping[IP + port]
		return map_num