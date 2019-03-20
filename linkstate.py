# linkstate.py
# contains the Link State info for a local link state
import numpy as np

class LinkState:
	def __init__(self, IP, port):
		self.IP = IP
		self.port = port
		self.mapping = {self.IP + str(self.port): 0}
		self.LSDB = {0: 0}

	def addNeighbor(self, neigh_IP, port):
		map_num = len(self.mapping)
		self.mapping[neigh_IP + str(port)] = map_num
		self.LSDB[map_num] = 1
		print('neighbor added to link state')
	
	def updateNeighborDelay(self, neigh_index, delay):
		self.LSDB[neigh_index] = delay + 1 # for now bc no delay
	
	def mapping2Matrix(self, map):
		print(map)
		mappingMatrix = np.array([])
		for key, elem in map:
			newrow = np.array([elem, key])
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
		map_num = self.mapping[IP + str(port)]
		return map_num
	
	def printLinkState(self):
		print(self.IP)
		print(self.port)
		print(self.mapping)
		print(self.LSDB)

#ls = LinkState('127.0.0.1', str(33333))
#ls.addNeighbor('127.0.0.1', str(22222))
#ls.addNeighbor('127.0.0.1', str(44444))
#ls.addNeighbor('127.0.0.1', str(55555))
#ls.printLinkState()
#num = ls.ip2MapNum('127.0.0.1', 55555)
#print(num)
#ls.updateNeighborDelay(num, 3)
#ls.printLinkState()

