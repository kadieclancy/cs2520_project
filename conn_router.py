#this router is responsible for storing all the physical topology of the network 
import socket
import pickle
from Packet import packet
import numpy as np
from threading import Timer


class conn_router:

    def __init__(self):
        # Load the config file that gives info about network
        self.connec = np.loadtxt("config_file2.txt", dtype='i', delimiter=',')
        self.ports = []
        for i in range(len(self.connec[0])):
            self.ports.append(0)
        self.num_connections = 0
        self.HOST = '127.0.0.1'
        self.PORT = 12345 

    #the sole function of this router is to provide the connectivity information to other routers
    # this enables the routers to know what other routers are in the network, the connectivity
    # of those routers, as well as their ips/ports 
    def run(self):
        while True:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                s.bind((self.HOST, self.PORT))
                s.listen()
                conn, addr = s.accept()
                with conn:
                    #print('Connected by', addr)
                    while True:
                        data = conn.recv(1024)
                        if not data:
                            break
                        p = pickle.loads(data)
                        #op code of 0 means its the routers first time connecting
                        if p.op == 0:
                            self.ports[int(p.contents)] = p.source_ip
                            print(self.ports)
                            self.num_connections = self.num_connections + 1
                            print('Num_connections: ' + str(self.num_connections))
                            #d = [self.connec, self.ports]
                            data_pickle = pickle.dumps(self.connec)
                            conn.sendall(data_pickle)

                            #send_connec_thread = Timer(5, self.send_topology_thread, [conn])
                            #send_connec_thread.start()
                        #op code of 1 means the router is trying to get the other port nums
                        elif p.op == 1:
                            if self.num_connections < len(self.connec[0]):
                                p = packet(p.source_ip, '12345', 0, ' ', 'not_all_routers_ready', False)
                                data_pickle = pickle.dumps(p)
                                conn.sendall(data_pickle)
                            else:
                                data_pickle = pickle.dumps(self.ports)
                                conn.sendall(data_pickle)



    def send_topology_thread(self, soc):
        if self.num_connections < len(self.connec[0]):
            print(str(self.num_connections) + ' routers connected of ' + str(len(self.connec[0])))
            send_connec_thread = Timer(5, self.send_topology_thread, [soc])
            send_connec_thread.start()
        else:
            d = [self.connec, self.ports]
            data_pickle = pickle.dumps(d)
            soc.sendall(data_pickle)


c = conn_router()
c.run()