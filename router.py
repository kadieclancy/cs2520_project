import socket
import pickle
import sys
from Packet import packet

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
        conn_and_port_info = self.get_connections()
        self.connections = conn_and_port_info[0]
        self.ports = conn_and_port_info[1]
        self.listen('127.0.0.1', port)

    #if the router specified by the argument is a neighbor to this router, return the port
    #   number of the neighbor router. otherwise, return -1 
    def is_neighbor(self, other_router_port):
        try:
            i = self.ports.index(other_router_port)
            return other_router_port
        except ValueError:
            return -1

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
        print('Initial setup complete.')
        return c


    def periodic_ping_neighbors(self):
        return

    #most of the routers lifetime will be spent in this function, waiting for a connection
    def listen(self, HOST, PORT):
        #self.get_neighbor_ports()
        print('Listening...')
        while True:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
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
                            #if the destination cannot be reached, the forward port will be -1
                            if(forward_port != -1):
                                print('Forwarding the packet to ' + str(forward_port))
                                new_p = packet(decoded_packet.dest_ip, HOST + str(PORT), 0, decoded_packet.contents)
                                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as send_s:
                                    send_s.connect(('127.0.0.1', forward_port))
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
    print('Syntax should be \'python3 test_router.py IP PORT\'')
