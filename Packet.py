import random
from linkstate import *

error_rate = 10

class packet:
	#introduce a packet error every error_rate packets
	def __init__(self, dest_ip, source_ip, op, contents):
		self.dest_ip = dest_ip
		self.source_ip = source_ip
		self.op = op
		self.contents = contents
		#compute checksum before potentially introducing an error
		self.checksum = self.compute_chksum(self.contents)
		#force a packet error if the random number generated is 0 
		error = random.randint(0, error_rate)
		if error == -1:
			self.packet_error()


	def compute_chksum(self, msg):
	  msg = str(msg)
	  s = 0       # Binary Sum
	  # loop taking 2 characters at a time
	  for i in range(0, len(msg)-1, 2):
	    if (i+1) < len(msg):
	      a = ord(msg[i]) 
	      b = ord(msg[i+1])
	      s = s + (a+(b << 8))
	    elif (i+1)==len(msg):
	      s += ord(msg[i])
	    else:
	      raise "Something Wrong here"
	  # One's Complement
	  s = s + (s >> 16)
	  s = ~s & 0xffff
	  return s

	def check_chksum(self):
		return (self.checksum == self.compute_chksum(self.contents))

	#call if an error occurred when packet was created. randomly change one of
	#	the characters in contents 
	def packet_error(self):
		error_index = int(random.randint(0, len(self.contents)-1))
		#self.contents[error_index] = chr(ord(self.contents[error_index]) + 1)
		tmp = list(self.contents)
		tmp[error_index] = chr(ord(tmp[error_index]) + 1)
		self.contents = str(tmp)

# i = 1
# while True:
# 	print('making packet number: ' + str(i))
# 	p1 = packet(33333, 22222, 0, 'a packet')
# 	if not p1.check_chksum():
# 		print(p1.contents)
# 		break

#ls = LinkState('127.0.0.1', str(33333))
#lls =  pickle.dumps(ls)
# UNCOMMENT LSA
#p = packet('127.0.0.1', 33333, 3, lls)
# 	i+=1

