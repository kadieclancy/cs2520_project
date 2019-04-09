import socket
import pickle
import sys
import time
from Packet import packet
from threading import Timer,Thread,Event
from dijkstras import dijkstras
from linkstate import *
from routingTable import *
import random as rand

class router:

    def __init__(self, id, ip, port):
        print('Initializing router ' + str(id) + '...')
        self.id = int(id)
        self.ip = ip 
        self.port = port
        #these params can be modified
        self.alive_interval = 5
        self.LSA_interval = 10
        self.timout = 2
        self.packetbuffer = ''
        # Link State DB is a matrix, init populated with known neighbors
        # once neighbors send their connections, matrix is updated
        self.LSDB = []
        # Keeps track of the mapping from internal naming of nodes to IP/ports
        self.countt = 0
        self.mapping = {self.countt : [sys.argv[2], int(sys.argv[3])]}
        # Routing Table structure
        self.RT = RoutingTable()
        # Local link state object to keep track of neighbors and weights to neighbors
        self.localLinkState = LinkState(self.ip, self.port)
        #self.localLinkState.printLinkState()
        self.msg_holder = {}
        self.running = False
        self.ports = []
        self.topology = self.get_topology()
        self.neighbor_ports = self.get_neighbor_ports()
        self.neighbors_statuses = {}
        self.packet_drop_rate = 100
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
        def join(self):
            self.thread.join()

    #subclass to create the LSA thread responsible for LSA messages to neighbors 
    class periodic_LSA_timer():
        def __init__(self, time, timer_event):
            self.time = time
            self.timer_event = timer_event
            self.thread = Timer(self.time, self.timer_event)
        def start(self):
            self.thread.start()
        def cancel(self):
            self.thread.cancel()
        def join(self):
            self.thread.join()

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
        def join(self):
            self.thread.join()

    #if the router specified by the argument is a neighbor to this router, return the port
    #   number of the neighbor router. otherwise, return -1 
    def is_neighbor(self, other_router_port):
        try:
            if str(other_router_port) == str(self.port):
                return -1
            i = self.ports.index(str(other_router_port))
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
                #self.countt = self.countt + 1
                #self.mapping[self.countt] = c
        return neighbor_info

    #call when router first starts up. contacts the central conn_router to get the
    #   network topology 
    def get_topology(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            #connect to conn_router, whos port is hard coded in 
            s.connect(('127.0.0.1', 12345))
            p = packet(12345, self.port, 0, ' ', str(self.id), False)
            encoded_packet = pickle.dumps(p)
            s.sendall(encoded_packet)
            data = s.recv(4096)
        connec = pickle.loads(data)
        #now, connect again and periodically poll whether all other routers are connected
        port_poll = Timer(5, self.port_poll_thread)
        port_poll.start()
        port_poll.join()
        return connec

    def port_poll_thread(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            #connect to conn_router, whos port is hard coded in 
            s.connect(('127.0.0.1', 12345))
            p = packet(12345, self.port, 1, ' ', 'request_ports', False)
            encoded_packet = pickle.dumps(p)
            s.sendall(encoded_packet)
            data = s.recv(4096)
        p = pickle.loads(data)
        if isinstance(p, packet):
            print('Not all routers ready. Trying again in 5 seconds.')
            port_poll = Timer(5, self.port_poll_thread)
            port_poll.start()
            port_poll.join()
        else:
            print('All routers ready.')
            self.ports = p


    #on startup, routers must confirm that their neighbors established in the 
    #   router topology are alive. It should hang up here before beginning its usual functions,
    #   until its confirmed that all of its neighbors are live. At which point self.running = True
    def establish_neighbor_connections(self):
        #print(self.neighbor_ports)
        for neighbor in self.neighbor_ports:
            init_timing_thread = self.init_neighbor_timer(5, self.establish_neighbor_thread, neighbor[1])
            init_timing_thread.start()
            #init_timing_thread.join()
        timing_thread = self.periodic_neighbor_timer(5, self.periodic_ping_neighbors)
        timing_thread.start()
        timing_thread_lsa = self.periodic_LSA_timer(6, self.periodic_LSA_neighbors)
        timing_thread_lsa.start()

    #event function for repeadedly pinging neighbors at startup. This needs to be its own
    #   function because it is the callback for a timer object. there will be different threads
    #   each running this function for each neighbor. once all neighbors are confirmed to be alive
    #   and all threads running this function cease, normal functioning of the router may begin
    def establish_neighbor_thread(self, other_router_port):
        print('Attempting to establish connection to router: ' + str(other_router_port))
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect(('127.0.0.1', int(other_router_port)))
                p = packet(other_router_port, self.port, 2, ' ', 'Neighbor_Request', False)
                encoded_packet = pickle.dumps(p)
                s.sendall(encoded_packet)
                data = s.recv(4096)
            c = pickle.loads(data)
            if str(c.contents) == 'Be_Neighbors_Confirm':
                print('Connection established')
                self.neighbors_statuses[str(other_router_port)] = True
                # Add neighbor to LSDB (init delay 1 for hop)
                self.localLinkState.addNeighbor('127.0.0.1', other_router_port)
                #self.localLinkState.printLinkState()
                # Init Routing Table
                #self.RT.createInitRT(self.localLinkState)
            else:
                print('Connection refused.')
                print(str(c.contents))
        except:
            print('Unable to connect to neighbor: ' + str(other_router_port))  
            timing_thread = self.init_neighbor_timer(5, self.establish_neighbor_thread, other_router_port)
            timing_thread.start()
        

    #callback function to a timer object (periodic_neighbor_timer). each alive_interval 
    #   seconds, it attemps to establish a connection with all of its neighbors. 
    def periodic_ping_neighbors(self):
        if self.running:
            #print('Pinging neighbors...')
            for neighbor in self.neighbor_ports:
                try:
                    cur_time = 0
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                        s.connect((neighbor[0], int(neighbor[1])))
                        cur_time = time.time()
                        p = packet(neighbor[0], self.port, 1, ' ', str(cur_time), False)
                        # can send LSA here
                        encoded_packet = pickle.dumps(p)
                        s.sendall(encoded_packet)
                        data = s.recv(1024)
                    c = pickle.loads(data) 
                    delay_time = int(c) - int(cur_time)
                    # Update weight in Link State
                    num = self.localLinkState.ip2MapNum(neighbor[0], neighbor[1])
                    self.localLinkState.updateNeighborDelay(num, delay_time)
                    self.RT.updateRT(num, delay_time)
                except Exception as e:
                    print(e)
                    print('Unable to connect to neighbor (Alive): ' + str(neighbor))
        else:
            if self.all_connections_established():
                self.running = True
                self.RT.createInitRT(self.localLinkState)
                print('Router startup complete. Please allow a few seconds for routing tables to be built.')
        timing_thread = self.periodic_neighbor_timer(self.alive_interval, self.periodic_ping_neighbors)
        timing_thread.start()
        return
        

    #callback function to a timer object (periodic_neighbor_timer). each alive_interval 
    #   seconds, it attemps to establish a connection with all of its neighbors. 
    def periodic_LSA_neighbors(self):
        if self.running:
            #print('Sending LSA to neighbors...')
            for neighbor in self.neighbor_ports:
                try:
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                        s.connect((neighbor[0], int(neighbor[1])))
                        #conetents of 'packet num' for LSA packets is the LIFETIME
                        p = packet(neighbor[0], self.port, 3, '3', self.localLinkState, False)
                        encoded_packet = pickle.dumps(p)
                        s.sendall(encoded_packet)
                except Exception as e:
                    print(e)
                    print('Unable to connect to neighbor (LSA): ' + str(neighbor))
        timing_thread_lsa = self.periodic_LSA_timer(self.LSA_interval, self.periodic_LSA_neighbors)
        timing_thread_lsa.start()
        return

    #simple function to check through connections_statuses to see if all neighbors are connected
    def all_connections_established(self):
        #print(str(self.neighbors_statuses))
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

    #callback function from a timer that should trigger a request for retransmission if 
    #   an ack is not received after the specified time 
    def timeout_callback(self):
        #print('Ack not received! Requesting retransmission')
        i = 10
    
    #most of the routers lifetime will be spent in this function, waiting for a connection
    def listen(self, HOST, PORT):
        print('Listening...')
        while True:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                #s.setblocking(0)
                s.bind((HOST, int(PORT)))
                s.listen()
                p_error = False
                conn, addr = s.accept()
                with conn:
                    #print('Connected by', addr)
                    while True:
                        data = conn.recv(4096)
                        if not data:
                            break
                        decoded_packet = pickle.loads(data)  
                        if not isinstance(decoded_packet.contents, LinkState) and decoded_packet.check_chksum() == False:
                            print('Packet error. Dropping...')
                            p_error = True
                            break
                        if rand.randint(0, self.packet_drop_rate) == 0:
                            print('Buffers full. Dropping...')
                            p_error = True
                            break
                        #ack_timeout = Timer(self.timout, self.timeout_callback)
                        msg_packets = []
                        #op 0 = no operations required, forward to dest ip
                        if(decoded_packet.op == 0 and self.running and p_error == False): 
                            # If its a message coming from the client to be sent
                            if decoded_packet.source_ip == int(PORT):
                                # break the message into packets
                                try:
                                    msg = decoded_packet.contents
                                    max = 10
                                    if len(decoded_packet.contents) > max:
                                        msg_packets = [msg[i:i+max] for i in range(0, len(msg), max)]
                                except:
                                    pass
                                #print(msg_packets)
                            #if the destination IP is this router
                            if(int(decoded_packet.dest_ip) == int(PORT) and p_error == False):
                                #print('Test procedure: forcibly dropping packet')
                                #break
                                if decoded_packet.packet_num == ' ':
                                    print('*Packet arrived at destination with contents: (Full Message)')
                                    print(str(decoded_packet.contents))
                                    print('Sending ack')
                                    #ack_timeout.cancel()
                                    ack_pack = packet(decoded_packet.source_ip, self.port, 0, ' ', 'ack', False)
                                    conn.sendall(pickle.dumps(ack_pack))
                                    # Record Msg
                                    self.msg_holder[decoded_packet.source_ip] = decoded_packet.contents
                                    break
                                else:
                                    print('*Packet arrived at destination with contents:')
                                    print(str(decoded_packet.contents))
                                    self.packetbuffer += decoded_packet.contents
                                    if decoded_packet.packet_num == 'L':
                                        print('*Full Message:')
                                        print(self.packetbuffer)
                                        self.msg_holder[decoded_packet.source_ip] = self.packetbuffer
                                        self.packetbuffer = ' '
                                        break
                                    else:
                                        print('Sending ack')
                                        #ack_timeout.cancel()
                                        ack_pack = packet(decoded_packet.source_ip, self.port, 0, ' ', 'ack', False)
                                        conn.sendall(pickle.dumps(ack_pack))
                                        break
                            #else, forward the packet to the next hop 
                            if msg_packets == []:
                                forward_port = self.RT.routingTableLookup('127.0.0.1', str(decoded_packet.dest_ip))              
                                forward_port = self.is_neighbor(int(forward_port[1]))
                                print('Forwarding the packet to ' + str(forward_port))
                                #if the destination cannot be reached, the forward port will be -1
                                if(forward_port != -1):
                                    new_p = packet(decoded_packet.dest_ip, HOST + str(PORT), 0, decoded_packet.packet_num, decoded_packet.contents)
                                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as send_s:
                                        send_s.connect(('127.0.0.1', int(forward_port)))
                                        send_s.sendall(pickle.dumps(new_p))
                                        print('Waiting for Ack')
                                        #ack_timeout.start()
                                        try:
                                            data = pickle.loads(send_s.recv(4096))
                                            if(data.contents == 'ack'):
                                                #ack_timeout.cancel()
                                                print('Received acknowledgment. Ready to forward more packets')
                                                if str(decoded_packet.source_ip) != str(self.port):
                                                    print('Sending ack to: ' + str(decoded_packet.source_ip))
                                                    ack_pack = packet(decoded_packet.source_ip, self.port, 0, ' ', 'ack', False)
                                                    conn.sendall(pickle.dumps(ack_pack))
                                                break
                                            else:   #noack
                                                if str(decoded_packet.source_ip) != self.port: 
                                                    print('Received noack. Forwarding to: ' + str(decoded_packet.source_ip))
                                                    ack_pack = packet(decoded_packet.source_ip, self.port, 0, ' ', 'noack', False)
                                                    conn.sendall(pickle.dumps(ack_pack))
                                                    break
                                                else:
                                                    print('Packet dropped. Retransmitting packet.')
                                                    while True:
                                                        #send_s.connect(('127.0.0.1', int(forward_port)))
                                                        time.sleep(2)
                                                        send_s.sendall(pickle.dumps(new_p))
                                                        try:
                                                            data = pickle.loads(send_s.recv(4096))
                                                            if(data.contents == 'ack'):
                                                                print('Received acknowledgment. Ready to forward more packets')
                                                                ack_pack = packet(decoded_packet.source_ip, self.port, 0, ' ', 'ack', False)
                                                                conn.sendall(pickle.dumps(ack_pack))
                                                                break
                                                        except:
                                                            print('Packet dropped. Retransmitting packet.')
                                                    

                                        except Exception as e:
                                            if str(decoded_packet.source_ip) == str(self.port):
                                                print('Packet dropped. Retransmitting packet.')
                                                #send_s.connect(('127.0.0.1', int(forward_port)))
                                                while True:
                                                    time.sleep(2)
                                                    send_s.close()
                                                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as new_send_s:
                                                        new_send_s.connect(('127.0.0.1', int(forward_port)))
                                                        new_p = packet(decoded_packet.dest_ip, HOST + str(PORT), 0, decoded_packet.packet_num, decoded_packet.contents)
                                                        new_send_s.sendall(pickle.dumps(new_p))
                                                        try:
                                                            data = pickle.loads(new_send_s.recv(4096))
                                                            if(data.contents == 'ack'):
                                                                print('Received acknowledgment. Ready to forward more packets')
                                                                ack_pack = packet(decoded_packet.source_ip, self.port, 0, ' ', 'ack', False)
                                                                conn.sendall(pickle.dumps(ack_pack))
                                                                break
                                                        except:
                                                            print('Packet dropped. Retransmitting packet.')
                                            else:
                                                print('Packet dropped. Sending NoAck to: ' + str(decoded_packet.source_ip))
                                                ack_pack = packet(decoded_packet.source_ip, self.port, 0, ' ', 'noack', False)
                                                conn.sendall(pickle.dumps(ack_pack))
                                else:
                                    print('Error forwarding packet')
                                    break
                            #else if there are packets to be sent
                            else:
                                print('OKAY WE ARE PACKETIZING')
                                forward_port = self.RT.routingTableLookup('127.0.0.1', str(decoded_packet.dest_ip))              
                                forward_port = self.is_neighbor(int(forward_port[1]))
                                counter = 0
                                final = len(msg_packets) - 1
                                for pkt in msg_packets:
                                    print('Forwarding the packet to ' + str(forward_port))
                                    print(pkt)
                                    #if the destination cannot be reached, the forward port will be -1
                                    if(forward_port != -1):
                                        if counter != final:
                                            new_p = packet(decoded_packet.dest_ip, HOST + str(PORT), 0, str(counter), pkt, False)
                                        else:
                                            new_p = packet(decoded_packet.dest_ip, HOST + str(PORT), 0, 'L', pkt, False)
                                        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as send_s:
                                            send_s.connect(('127.0.0.1', int(forward_port)))
                                            send_s.sendall(pickle.dumps(new_p))
                                            if counter != final:
                                                print('Waiting for Ack')
                                                #ack_timeout.start()
                                                try:
                                                    data = pickle.loads(send_s.recv(4096))
                                                    if(data.contents == 'ack'):
                                                        #ack_timeout.cancel()
                                                        print('Received acknowledgment. Ready to forward more packets')
                                                        print('Sending ack to: ' + str(decoded_packet.source_ip))
                                                        ack_pack = packet(decoded_packet.source_ip, self.port, 0, ' ', 'ack', False)
                                                        conn.sendall(pickle.dumps(ack_pack))
                                                        counter = counter + 1
                                                        time.sleep(1)
                                                except:
                                                    print('Connection broken')
                                    else:
                                        print('Error forwarding packet')
                                        break
                        #op code of 1 means its a periodic alive message
                        elif(decoded_packet.op == 1 and self.running):
                            #respond with the current time to get delay
                            conn.sendall(pickle.dumps(time.time()))
                            break

                        #op code of 2 means its a neighbor acquisition message
                        elif(decoded_packet.op == 2):
                            #if self.is_neighbor(decoded_packet.source_ip) != -1:
                            #    resp_packet = packet(decoded_packet.source_ip, self.port, 2, 'Be_Neighbors_Confirm')
                            #    conn.sendall(pickle.dumps(resp_packet))
                            #else:
                            #    resp_packet = packet(decoded_packet.source_ip, self.port, 2, 'Be_Neighbors_Refuse')
                            #    conn.sendall(pickle.dumps(resp_packet))
                            resp_packet = packet(decoded_packet.source_ip, self.port, 2, ' ', 'Be_Neighbors_Confirm', False)
                            conn.sendall(pickle.dumps(resp_packet))
                            break

                        #op code of 3 means link state advertisement
                        elif(decoded_packet.op == 3 and self.running):
                            lt = int(decoded_packet.packet_num)
                            if(lt <= 0):
                                #print('LSA lifetime over, discarding...')
                                pass
                            else:    
                                lsa = decoded_packet.contents
                                port = decoded_packet.source_ip
                                # add to LSDB & recompute routing table     
                                self.RT.addOtherRouterLSA(lsa)
                                # send to all neighbors except the one that sent it
                                for neighbor in self.neighbor_ports:
                                    if str(neighbor[1]) != str(port):
                                        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s2:
                                            s2.connect((neighbor[0], int(neighbor[1])))
                                            p = packet(neighbor[0], self.port, 3, str(lt-1), lsa, False)
                                            encoded_packet = pickle.dumps(p)
                                            s2.sendall(encoded_packet)
                               
                        #op code of 4 send shortest path to client
                        elif(decoded_packet.op == 4 and self.running):
                            print('Client Request For - Shortest Paths')
                            shortest_paths = pickle.dumps(self.RT.RT)
                            reply_pack = packet(decoded_packet.source_ip, self.port, 4, ' ', shortest_paths, False)
                            conn.sendall(pickle.dumps(reply_pack))
                        #op code of 5 send RT to client
                        elif(decoded_packet.op == 5 and self.running):
                            print('Client Request For - Routing Table')
                            route_tbl = pickle.dumps(self.RT)
                            reply_pack = packet(decoded_packet.source_ip, self.port, 5, ' ', route_tbl, False)
                            conn.sendall(pickle.dumps(reply_pack))
                        #op code of 5 send RT to client
                        elif(decoded_packet.op == 6 and self.running):
                            print('Client Request For - Control Info')
                            control = pickle.dumps(self.alive_interval)
                            reply_pack = packet(decoded_packet.source_ip, self.port, 6, ' ', control, False)
                            conn.sendall(pickle.dumps(reply_pack))
                        #op code of 7 to send saved msg info
                        elif(decoded_packet.op == 7 and self.running):
                            print('Client Request For - Incoming Messages')
                            msg = pickle.dumps(self.msg_holder)
                            reply_pack = packet(decoded_packet.source_ip, self.port, 7, ' ', msg, False)
                            conn.sendall(pickle.dumps(reply_pack))
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
    print('Syntax should be \'python3 router.py ID IP PORT\'')
