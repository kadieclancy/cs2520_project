import time, threading 
import socket
from Packet import packet
import pickle 

#todo:
#	1. file to packet conversion 
#	2. printing / configuring of control information 
#	3. removal of periodic ping - this is something the router does

def control():
	print('Need to implement control')
	return

def send_file(packet):
	PORT = input('Enter first hop port (22222): ')
	with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
	    s.connect(('127.0.0.1', int(PORT)))
	    #tuple, sock_info[0] = ip, sock_info[1] = host
	    sock_info = s.getsockname()
	    #s.sendall(str.encode(mes))
	    #p = packet(HOST+str(PORT), sock_info[1], 0, 'file contents')
	    encoded_packet = pickle.dumps(packet)
	    s.sendall(encoded_packet)
	    data = s.recv(1024)
	    if data.decode() == 'ack':
	    	print('Ack received. File transmitted succesfully')

#ignore this function for now. something like this will need to be implemented on the routers
#	for periodic alive messages/LSA flooding

#def periodic_ping_server():
#	print('Pinging...')
#	HOST = input('Enter destination IP: ')
#	PORT = input('Enter destination port: ')
#	del_start = time.time()
#	with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
#	    s.connect((HOST, int(PORT)))
	    #tuple, sock_info[0] = ip, sock_info[1] = host
#	    sock_info = s.getsockname()
	    #s.sendall(str.encode(mes))
#	    p = packet(HOST+str(PORT), sock_info[1], 0, 'ping packet')
#	    encoded_packet = pickle.dumps(p)
#	    s.sendall(encoded_packet)
#	    data = s.recv(1024)
#	del_end = time.time()
#	print('Ping completed in ' + str(del_end - del_start) + ' sec.')
	#print(data.decode())
#	threading.Timer(15, periodic_ping_server).start()

print('Welcome to the Client Interface')
print('Please refer to the numbered commands below')
print()
print('Enter 1 for control information')
print('Enter 2 to send a file')
print('Enter 3 to view routing table information')
print('Enter 4 to display shortest paths')
print('Enter 5 to exit the client')
print('Enter 6 for help')
inp = input('')
if(int(inp) == 1):
	control()
elif(int(inp) == 2):
	p = packet(33333, 00000, 0, 'This is a packet')
	send_file(p)
elif(int(inp) == 3):
	# TODO
elif (int(inp) == 4):
	# TODO
elif(int(inp) == 5):
	# TODO implement exit
elif (int(inp) == 6):
	print('Welcome to the Client Interface')
	print('Please refer to the numbered commands below')
	print()
	print('Enter 1 for control information')
	print('Enter 2 to send a file')
	print('Enter 3 to view routing table information')
	print('Enter 4 to display shortest paths')
	print('Enter 5 to exit the client')
	print('Enter 6 for help')
else:
	print('Invalid Command. Enter 6 for help.')
