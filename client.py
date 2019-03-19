import time, threading 
import socket
from Packet import packet
import pickle 
import sys



def control():
	print('Need to implement control')
	return

def send_file(packet):
	with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
	    s.connect(('127.0.0.1', my_router_port))
	    #tuple, sock_info[0] = ip, sock_info[1] = host
	    sock_info = s.getsockname()
	    #s.sendall(str.encode(mes))
	    #p = packet(HOST+str(PORT), sock_info[1], 0, 'file contents')
	    encoded_packet = pickle.dumps(packet)
	    s.sendall(encoded_packet)
	    data = pickle.loads(s.recv(4096))
	    if data.contents == 'ack':
	    	print('Ack received. File transmitted succesfully')

if len(sys.argv) >= 1:
	my_router_port = int(sys.argv[1])
	
	#ignore this function for now. something like this will need to be implemented on the routers
	#	for periodic alive messages/LSA flooding
	while True:
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
			#dest = input('Enter dest port (33333): ')
			print('Enter the message you wish to send:')
			msg = input('')
			print('Enter the port number of the reciever: (33333)')
			port_num = input('')
			p = packet(int(port_num), my_router_port, 0, msg)
			send_file(p)
		#elif(int(inp) == 3):
			# TODO
		#elif (int(inp) == 4):
			# TODO
		elif(int(inp) == 5):
			break
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
else:
	print('Syntax should be \'python3 client.py PORT\'')
