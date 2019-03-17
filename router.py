import socket
import pickle
import sys
import time
from Packet import packet
from threading import Timer,Thread,Event

#todo:
#   1. implement RT as a dict, index by destination IP, data is the IP of the next hop to
#         reach the destination 
#   2. implement periodic alive messages 
#   3. implement init, where it contacts the conn_router and figures its local topology 
#   4. implement computation of the RT through the LSA's
#   5. implement LSA flooding 

class router:
    def __init__(self, id, ip, port):
        print('Initializing router ' + str(id) + '...')
        self.id = int(id)
        self.ip = ip 
        self.port = port
        self.alive_interval = 5
        conn_and_port_info = self.get_connections()
        self.connections = conn_and_port_info[0]
        self.ports = conn_and_port_info[1]
        self.neighbor_ports = self.get_neighbor_ports()
        self.listen(str(self.ip), self.port)

    #subclass to create the timing thread responsible for alive messages to neighbors 
    class neighbor_timer():
        def __init__(self, time, timer_event):
            self.time = time
            self.timer_event = timer_event
            self.thread = Timer(self.time, self.timer_event)
        def start(self):
            self.thread.start()
        def cancel(self):
            self.thread.cancel()

    #if the router specified by the argument is a neighbor to this router, return the port
    #   number of the neighbor router. otherwise, return -1 
    def is_neighbor(self, other_router_port):
        try:
            i = self.ports.index(int(other_router_port))
            return other_router_port
        except ValueError:
            return -1

    #optain the ips and port numbers of all neighbors and return them as a list of tuples
    def get_neighbor_ports(self):
        neighbor_info = []
        for i in range(len(self.ports)):
            if self.connections[self.id][i] == 1  and str(self.ports[i]) != str(self.port):
                c = ['127.0.0.1', self.ports[i]]
                neighbor_info.append(c)
        return neighbor_info

    #call when router first starts up, to get its neighbors 
    def get_connections(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            #connect to conn_router, whos port is hard coded in 
            s.connect(('127.0.0.1', 12345))
            p = packet(12345, self.ip, 0, 'get_connectivity')
            encoded_packet = pickle.dumps(p)
            s.sendall(encoded_packet)
            data = s.recv(1024)
        c = pickle.loads(data)
        timing_thread = self.neighbor_timer(self.alive_interval, self.periodic_ping_neighbors)
        timing_thread.start()
        print('Initial setup complete.')
        return c


    def periodic_ping_neighbors(self):
        print('Pinging neighbors:')
        for neighbor in self.neighbor_ports:
            cur_time = 0
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((neighbor[0], neighbor[1]))
                cur_time = time.time()
                p = packet(neighbor[0], self.ip, 1, str(cur_time))
                encoded_packet = pickle.dumps(p)
                s.sendall(encoded_packet)
                data = s.recv(1024)
            c = pickle.loads(data) 
            delay_time = int(c) - int(cur_time)
            #print('Delay to neighbor ' + str(neighbor[1]) + ' : ' + str(delay_time))
        timing_thread = self.neighbor_timer(self.alive_interval, self.periodic_ping_neighbors)
        timing_thread.start()
        return

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
                        data = conn.recv(1024)
                        if not data:
                            break
                        decoded_packet = pickle.loads(data)  
                        #op 0 = no operations required, forward to dest ip
                        if(decoded_packet.op == 0): 
                            #if the destination IP is this router
                            if(int(decoded_packet.dest_ip) == int(PORT)):
                                print('Packet arrived at destination with contents:')
                                print(decoded_packet.contents)
                                print('Sending ack')
                                conn.sendall(str.encode('ack'))
                                break
                            #else, forward the packet to the next hop 
                            forward_port = self.is_neighbor(decoded_packet.dest_ip)
                            print('PORT TO FORWARD PACKET TO: ' + str(forward_port))
                            #if the destination cannot be reached, the forward port will be -1
                            if(forward_port != -1):
                                print('Forwarding the packet to ' + str(forward_port))
                                new_p = packet(decoded_packet.dest_ip, HOST + str(PORT), 0, decoded_packet.contents)
                                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as send_s:
                                    send_s.connect(('127.0.0.1', int(forward_port)))
                                    send_s.sendall(pickle.dumps(new_p))
                                    data = send_s.recv(1024)
                                    if(data.decode() == 'ack'):
                                        print('Received acknowledgment. Ready to forward more packets')
                                        print('Sending ack')
                                        conn.sendall(str.encode('ack'))
                                        break
                            else:
                                print('Error forwarding packet.')
                                break
                        #op code of 1 means its a periodic alive message
                        elif(decoded_packet.op == 1):
                            #respond with the current time to get delay
                            conn.sendall(pickle.dumps(time.time()))
                            break

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
