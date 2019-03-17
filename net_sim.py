from router import router
import threading 
#from multiprocessing.dummy import Pool as ThreadPool 

def create_router(id, ip, port):
	router(id, ip, port)


num_routers = 2
for i in range(0, num_routers):
	#start port numbers at 50000
	#t = threading.Thread(target=create_router, args=(i, '127.0.0.1', i+20000))
	#t.daemon = True
	#t.start()
	create_router(i, '127.0.0.1', i+20000)


