# routingTable.py
# contains the Link State info for a local link state
import numpy as np
from linkstate import *
from dijkstras import *

class RoutingTable:
	def __init__(self):
		self.RT = np.array([0])
		self.myMapping = {}
		self.RT_Dict = {}
	
	def createInitRT(self, localLinkState):
		self.myMapping = localLinkState.mapping
		
		# get a matrix mapping of dict
		mappingMatrix = np.array([])
		for key, elem in self.myMapping.items():
			newrow = np.array([elem, key])
			if mappingMatrix.size == 0:
				mappingMatrix = newrow
			else:
				mappingMatrix = np.vstack([mappingMatrix, newrow])
		
		lls = localLinkState.LSDB
		print(mappingMatrix)
		for row in mappingMatrix:
			# the mapping in the local link state will be the order of the adj mat
			ind = row[0]
			# create row and col to add to the RT adj mat
			if np.array_equal(self.RT, [0]) and int(ind) == 0:
				print(' ')
			else:
				s = self.RT.shape
				r = int(s[0])
				new_col = np.zeros([(r),1], dtype = int) #[:,[0]]
				new_row = np.zeros([1,(r+1)], dtype = int)[0,:]
				# add to RT
				self.RT = np.column_stack((self.RT, new_col))
				self.RT = np.vstack((self.RT, new_row))
				# change ind of neighbor to 1 init bc connected
				self.RT[0, r] = 1
				self.RT[r, 0] = 1
		print('ROUTING TABLE:')
		print(self.RT)
		self.computeRT(self.RT)

	def computeRT(self, adjMat):
		self.RT_Dict = dijkstras(adjMat, 0)
		print('ROUTING TABLE DICT:') 
		print(self.RT_Dict)

	def addLSA(self, linkstate):
		map = linkstate.mapping
		lsdb = linkstate.LSDB
		
	def updateRT(self, mappingNum, delay):
		self.RT[0, int(mappingNum)] = int(delay) + 1
		self.RT[int(mappingNum), 0] = int(delay) + 1
		print('NEW ROUTING TABLE:')
		print(self.RT)
		self.computeRT(self.RT)
	
	def routingTableLookup(self, IP, port):
		mapNum = self.myMapping[str(IP)+str(port)]
		vect = self.RT_Dict[mapNum]
		dist = vect[0]
		path = vect[1]
		
		for key, elem in self.myMapping.items():
			if path[0] == elem:
				addr = key
		
		forward_IP = addr[:9]
		forward_port = addr[9:]
		
		return forward_IP, forward_port
		
	
ls = LinkState('127.0.0.1', str(33333))
ls.addNeighbor('127.0.0.1', str(22222))
ls.addNeighbor('127.0.0.1', str(44444))
ls.addNeighbor('127.0.0.1', str(55555))
#ls.printLinkState()
#num = ls.ip2MapNum('127.0.0.1', 55555)
#print(num)
#ls.updateNeighborDelay(num, 3)
#ls.printLinkState()

print('Starting RT STuff')
route = RoutingTable()
route.createInitRT(ls)
route.updateRT(2, 10)
route.routingTableLookup('127.0.0.1', str(22222))