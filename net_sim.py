from test_router import router
from _thread import *
import threading 
#from multiprocessing.dummy import Pool as ThreadPool 

def create_router(id, port):
	router(id, port)


num_routers = 2
for i in range(0, num_routers):
	#start port numbers at 50000
	t = threading.Thread(target=create_router, args=(i, i+50000))
	t.daemon = True
	t.start()
