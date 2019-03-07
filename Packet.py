class packet:
	dest_ip = 0
	source_ip = 0
	op = -1
	def __init__(self, dest_ip, source_ip, op, contents):
		self.dest_ip = dest_ip
		self.source_ip = source_ip
		self.op = op
		self.contents = contents

