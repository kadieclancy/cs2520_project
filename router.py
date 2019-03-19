import socket
import pickle
import sys
import time
from Packet import packet
from threading import Timer,Thread,Event
from dijkstras import dijkstras

#todo:
#   1. implement RT as a dict, index by destination IP, data is the IP of the next hop to
#         reach the destination 
#   2. implement periodic alive messages 
#   3. implement init, where it contacts the conn_router and figures its local topology 
#   4. implement computation of the RT through the LSA's
#   5. implement LSA flooding 



class router:
	# Link State DB is a matrix, init populated with known neighbors
	# once neighbors send their connections, matrix is updated
	LSDB = []

	# Keeps track of the mapping from internal naming of nodes to IP/ports
	count = 0
	mapping	= {count : [sys.argv[2], int(sys.argv[3])]}
	
	# Routing Table structure indexed by destination and contains shortest path info
	RT	= {0 : [0]}

	def __init__(self, id, ip, port):
		print('Initializing router ' + str(id) + '...')
		self.id = int(id)
		self.ip = ip 
		self.port = port
		self.alive_interval = 5
		self.running = False
		conn_and_port_info = self.get_topology()
		self.topology = conn_and_port_info[0]
		self.ports = conn_and_port_info[1]
		self.neighbor_ports = self.get_neighbor_ports()
		self.neighbors_statuses = {}
		for neighbor in self.neighbor_ports:
			if str(neighbor) != str(self.port):
				self.neighbors_statuses[str(neighbor[1])] = False
		self.establish_neighbor_connections()
		self.listen(str(self.ip), self.port)

    #subclass to create the timing thread responsible for alive messages to neighbors 
	class periodic_neighbor_timer():
		def __init__(self, time, timer_event):
			self.time = time
			self.timer_event = timer_event
			self.thread = Timer(self.time, self.timer_event)
		def start(self):
			self.thread.start()
		def cancel(self):
			self.thread.cancel()

    #subclass to create the timing thread responsible for initial neighbor acquisition 
	class init_neighbor_timer():
		def __init__(self, time, timer_event, router_port):
			self.time = time
			self.timer_event = timer_event
			self.thread = Timer(self.time, self.timer_event, [router_port])
		def start(self):
			self.thread.start()
		def cancel(self):
			self.thread.cancel()

    #if the router specified by the argument is a neighbor to this router, return the port
    #   number of the neighbor router. otherwise, return -1 
	def is_neighbor(self, other_router_port):
		try:
			if str(other_router_port) == str(self.port):
				return -1
			i = self.ports.index(int(other_router_port))
			return other_router_port
		except ValueError:
			return -1

    #optain the ips and port numbers of all neighbors and return them as a list of tuples
	def get_neighbor_ports(self):
		neighbor_info = []
		for i in range(len(self.ports)):
			if self.topology[self.id][i] == 1  and str(self.ports[i]) != str(self.port):
				c = ['127.0.0.1', self.ports[i]]
				neighbor_info.append(c)
				self.count = self.count + 1
				self.mapping[self.count] = c
		return neighbor_info

    #call when router first starts up. contacts the central conn_router to get the
    #   network topology 
	def get_topology(self):
		with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            #connect to conn_router, whos port is hard coded in 
			s.connect(('127.0.0.1', 12345))
			p = packet(12345, self.ip, 0, 'get_connectivity')
			encoded_packet = pickle.dumps(p)
			s.sendall(encoded_packet)
			data = s.recv(4096)
		c = pickle.loads(data)
        #delay 10 seconds before pinging neighbors to allow them to startup 
		return c

    #on startup, routers must confirm that their neighbors established in the 
    #   router topology are alive. It should hang up here before beginning its usual functions,
    #   until its confirmed that all of its neighbors are live. At which point self.running = True
	def establish_neighbor_connections(self):
		for neighbor in self.neighbor_ports:
			init_timing_thread = self.init_neighbor_timer(5, self.establish_neighbor_thread, neighbor[1])
			init_timing_thread.start()
		timing_thread = self.periodic_neighbor_timer(self.alive_interval, self.periodic_ping_neighbors)
		timing_thread.start()

    #event function for repeadedly pinging neighbors at startup. This needs to be its own
    #   function because it is the callback for a timer object. there will be different threads
    #   each running this function for each neighbor. once all neighbors are confirmed to be alive
    #   and all threads running this function cease, normal functioning of the router may begin
	def establish_neighbor_thread(self, other_router_port):
		print('Attempting to establish connection to router: ' + str(other_router_port))
		try:
			with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
				s.connect(('127.0.0.1', other_router_port))
				p = packet(other_router_port, self.port, 2, 'Neighbor_Request')
				encoded_packet = pickle.dumps(p)
				s.sendall(encoded_packet)
				data = s.recv(4096)
			c = pickle.loads(data)
			if c.contents == 'Be_Neighbors_Confirm':
				print('Connection established')
				self.neighbors_statuses[str(other_router_port)] = True
			else:
				print('Connection refused.')
		except:
			print('Unable to connect to neighbor: ' + str(other_router_port))  
			timing_thread = self.init_neighbor_timer(5, self.establish_neighbor_thread, other_router_port)
			timing_thread.start()      

    #callback function to a timer object (periodic_neighbor_timer). each alive_interval 
    #   seconds, it attemps to establish a connection with all of its neighbors. 
	def periodic_ping_neighbors(self):
		if self.running:
			print('Pinging neighbors:')
			for neighbor in self.neighbor_ports:
				try:
					cur_time = 0
					with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
						s.connect((neighbor[0], neighbor[1]))
						cur_time = time.time()
						p = packet(neighbor[0], self.port, 1, str(cur_time))
						encoded_packet = pickle.dumps(p)
						s.sendall(encoded_packet)
						data = s.recv(1024)
					c = pickle.loads(data) 
					delay_time = int(c) - int(cur_time)
                    #print('Delay to neighbor ' + str(neighbor[1]) + ' : ' + str(delay_time))
				except:
					print('Unable to connect to neighbor: ' + str(neighbor))
		else:
			if self.all_connections_established():
				self.running = True
				print('Initial setup complete.')
		timing_thread = self.periodic_neighbor_timer(self.alive_interval, self.periodic_ping_neighbors)
		timing_thread.start()
		return

    #simple function to check through connections_statuses to see if all neighbors are connected
	def all_connections_established(self):
		for neighbor in self.neighbors_statuses:
			if not self.neighbors_statuses[neighbor]:
				return False
		return True
	
	def compute_RT(self, LSBD):
		# src is 0 since router always refers to itself as 0, returns dictionary
		SB = dijkstras(LSDB, 0)
		for key, elem in SB:
			# if not in RT, add it
			if key not in self.RT:
				self.RT[key] = elem
			# if in RT, update path
			else:
				self.RT[key] = elem
		return RT
	
    #most of the routers lifetime will be spent in this function, waiting for a connection
	def listen(self, HOST, PORT):
        #self.get_neighbor_ports()
		print('Listening...')
		while True:
			with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
				s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                #s.setblocking(0)
				s.bind((HOST, int(PORT)))
				s.listen()
				conn, addr = s.accept()
				with conn:
					print('Connected by', addr)
					while True:
						data = conn.recv(4096)
						if not data:
							break
						decoded_packet = pickle.loads(data)  
                        #op 0 = no operations required, forward to dest ip
						if(decoded_packet.op == 0): 
                        	# TODO add in buffer to hold packets
                            #if the destination IP is this router
							if(int(decoded_packet.dest_ip) == int(PORT)):
								print('Packet arrived at destination with contents:')
								print(decoded_packet.contents)
								print('Sending ack')
								ack_pack = packet(decoded_packet.source_ip, self.port, 0, 'ack')
								conn.sendall(pickle.dumps(ack_pack))
								break
                            #else, forward the packet to the next hop 
                            # RT lookup here
                            #forward_port = self.routing_table[str(decoded_packet.dest_ip)]
							forward_port = self.is_neighbor(decoded_packet.dest_ip)
                            #if the destination cannot be reached, the forward port will be -1
							if(forward_port != -1):
								print('Forwarding the packet to ' + str(forward_port))
								new_p = packet(decoded_packet.dest_ip, HOST + str(PORT), 0, decoded_packet.contents)
								with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as send_s:
									send_s.connect(('127.0.0.1', int(forward_port)))
									send_s.sendall(pickle.dumps(new_p))
									data = pickle.loads(send_s.recv(4096))
									if(data.contents == 'ack'):
										print('Received acknowledgment. Ready to forward more packets')
										print('Sending ack')
										ack_pack = packet(decoded_packet.source_ip, self.port, 0, 'ack')
										conn.sendall(pickle.dumps(ack_pack))
										break
							else:
								print('Error forwarding packet.')
								break
                        #op code of 1 means its a periodic alive message
						elif(decoded_packet.op == 1):
                            #respond with the current time to get delay
							conn.sendall(pickle.dumps(time.time()))
							break

                        #op code of 2 means its a neighbor acquisition message
						elif(decoded_packet.op == 2):
							if self.is_neighbor(decoded_packet.source_ip) != -1:
								resp_packet = packet(decoded_packet.source_ip, self.port, 2, 'Be_Neighbors_Confirm')
								conn.sendall(pickle.dumps(resp_packet))
							else:
								resp_packet = packet(decoded_packet.source_ip, self.port, 2, 'Be_Neighbors_Refuse')
								conn.sendall(pickle.dumps(resp_packet))
							break

						#op code of 3 means link state advertisement
						elif(decoded_packet.op == 3):
							# read contents
							lsa = decoded_packet.contents
							# TODO: add to LSDB
							# TODO: forward to neighbors
							# TODO: recompute RT
                        #op -1 = test packet                
						elif(decoded_packet.op == -1):
							print('Test packet from ' + str(s.getsockname[1]))


#syntax for creating a new router should be
# python3 test_router.py ID IP PORT 
if len(sys.argv) > 1:
    router(sys.argv[1], sys.argv[2], sys.argv[3])
    #init_router()
    #listen(sys.argv[1], int(sys.argv[2]))
else:
    print('Syntax should be \'python3 router.py IP PORT\'')
