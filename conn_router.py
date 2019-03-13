#this router is responsible for storing all the physical topology of the network 
import socket
import pickle
import numpy as np

HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
PORT = 12345        # Port to listen on (non-privileged ports are > 1023)
					#	hard coded in, new routers will ping this port 

#conn will be nxn, for n routers, where conn[i, j] is 1 if router_i and router_j are 
#	neighbors, and 0 otherwise 
#connec = 	[[0, 0, 0, 0],	
#			[0, 0, 0, 0],
#			[0, 0, 0, 0],
#			[0, 0, 0, 0]]
#test_network0

# Load the config file that gives info about network
connec = np.loadtxt("config_file.txt", dtype='i', delimiter=',')
print(connec)

#connec = 	[[1, 1],
#			[1, 1]]

#ports[i] = port number for router i
ports = [22222, 33333]
#test_network1
#connec = 	[[1, 1, 0, 0],	
#			[1, 1, 1, 0],
#			[0, 1, 1, 1],
#			[0, 0, 1, 1]]

#the sole function of this router is to provide the connectivity information to other routers
# this enables the routers to know what other routers are in the network, the connectivity
# of those routers, as well as their ips/ports 
def run():
	while True:
		with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
			s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
			s.bind((HOST, PORT))
			s.listen()
			conn, addr = s.accept()
			with conn:
			    print('Connected by', addr)
			    while True:
			        data = conn.recv(1024)
			        if not data:
			            break
			        d = [connec, ports]
			        #connectivity_pickle = pickle.dumps(connec)
			        #ports_pickle = pickle.dumps(ports)
			        data_pickle = pickle.dumps(d)
			        conn.sendall(data_pickle)

run()