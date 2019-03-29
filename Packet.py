import random
from linkstate import *

error_rate = 100

class packet:
	#introduce a packet error every error_rate packets
	def __init__(self, dest_ip, source_ip, op, packet_num, contents, error=True):
		self.dest_ip = dest_ip
		self.source_ip = source_ip
		self.op = op
		self.packet_num = packet_num
		self.contents = contents
		#compute checksum before potentially introducing an error
		self.checksum = self.compute_chksum(self.contents)
		#force a packet error if the random number generated is 0 
		error_val = random.randint(0, error_rate)
		if error_val == 0 and error==True:
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


