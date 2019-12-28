


class IO(object):
	def __init__(self,filepath):
		pass

	def load(self):
		"""
		Load IO table
		"""
		file = open(self.filepath,"r")
		raw = file.read()
		file.close()

		self.io_matrix = [[]] # input output intermediate matrix
		self.gross_output = 10000
		self.gross_input = 10000
		pass
		return self


io = IO(path).load()
io.io_matrix
io.gross_input