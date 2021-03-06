import time, threading 
import socket
from Packet import packet
import pickle 
import sys
from routingTable import *


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
		try:
			data = pickle.loads(s.recv(4096))
			if data.op == 0:
				print('Ack received. File transmitted successfully')
				return
			if data.op == 5:
				rt_obj = pickle.loads(data.contents)
				print(rt_obj.myMapping)
				print(rt_obj.RT)
				return
			else:
				rt = pickle.loads(data.contents)
				print(rt)
				print()
		except:
			print('Error connecting to router. Please try again.')

if len(sys.argv) >= 1:
	my_router_port = int(sys.argv[1])
	message_holder = {}
	
	#ignore this function for now. something like this will need to be implemented on the routers
	#	for periodic alive messages/LSA flooding
	while True:
		print('- - - - - Welcome to the Client Interface - - - - - ')
		print('Please refer to the numbered commands below')
		print()
		print('Enter 1 for control information')
		print('Enter 2 to send a file')
		print('Enter 3 to view messages')
		print('Enter 4 to view routing table information')
		print('Enter 5 to display shortest paths')
		print('Enter 6 to exit the client')
		print('Enter 7 for help')

		print()
		inp = input('>')
		if(int(inp) == 1):
			print('1: CONTROL INFO')
			print('Alive interval:')
			p = packet(my_router_port, my_router_port, 6, ' ', ' ')
			send_file(p)
		elif(int(inp) == 2):
			#dest = input('Enter dest port (33333): ')
			print('2: SEND FILE')
			print('Enter the message you wish to send:')
			msg = input('')
			print('Enter the port number of the reciever: (ex: 33333)')
			port_num = input('')
			p = packet(int(port_num), my_router_port, 0, ' ', msg)
			#Force an error into the packet
			#p.packet_error()
			send_file(p)
		elif(int(inp) == 4):
			print('4: VIEW ROUTING TABLE')
			p = packet(my_router_port, my_router_port, 5, ' ', ' ')
			send_file(p)
		elif (int(inp) == 5):
			print('5: VIEW SHORTEST PATHS')
			p = packet(my_router_port, my_router_port, 4, ' ', ' ')
			send_file(p)
		elif(int(inp) == 6):
			print('6: EXIT')
			break
		elif (int(inp) == 7):
			print('7: HELP')
			print('Please refer to the numbered commands below')
			print()
			print('Enter 1 to view control information, i.e. the alive interval used by the router')
			print('Enter 2 to send a message to a router in the network')
			print('Enter 3 to view messages that have been sent to the corresponding router')
			print('Enter 4 to view the routing table information of the corresponding router')
			print('Enter 5 to display shortest paths of the corresponding router')
			print('Enter 6 to exit the client')
			print('Enter 7 for help')
		elif (int(inp) == 3):
			print('3: VIEW MESSAGES')
			p = packet(my_router_port, my_router_port, 7, ' ', ' ')
			send_file(p)
		else:
			print('Invalid Command. Enter 6 for help.')
else:
	print('Syntax should be \'python3 client.py PORT\'')
