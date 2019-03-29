# Wide Area Networks Project: User Manual

**Some notes about the code:**

1. The network relies on a central router that stores the physical topology of the whole network. This is called conn_router.py. New routers know the port/ip of conn_router and automatically connect to it when they become alive. 

2. Each router/client must be run in its own terminal window, including conn_router.py.

3. Since the whole thing is run locally, the IPs for all the routers is just loopback 127.0.0.1. The port numbers are used to differentiate different routers and different sockets within routers.

4. For larger networks, you need to give the system some time (approximately 30 sec) after neighbor acquisiton for all routers to correctly discover all routers in the network via LSAs and construct their routing tables before sending messages. You can check to see if the whole network is accounted for by connecting a router to a client then selecting option 4 - view routing table.

5. Error rates are coded in. The packet error is possibly incurred during the creation of the packet, and thus is found in the __init__ for the packet class. The packet dropping is done in the router whenever it receives a new packet. The packet drop rate is in the constructor for the router. 

**How to run the code:**

To run this simulation, run the commands (each in a seperate terminal): 
```
1. python3 conn_router.py  [first make config.txt your intended network topology]
```
```
2. python3 router.py router_ID router_IP router_port [do this for each router]
```
```
3. python3 client.py router_port [router_port that corresponds with the router you want the client to connect to]
```

**Test case examples:**

*config_file_simple.txt*

Simulation with 2 clients and 2 routers, where the client sends a packet to the its router, who sends it to the second, at which point an ack is propogated packwards. To run this simulation, run the commands (each in a seperate terminal): 
```
1. python3 conn_router.py  
```
```
2. python3 router.py 0 127.0.0.1 22222
```
```
3. python3 router.py 1 127.0.0.1 33333
```
```
4. python3 client.py 22222
```
```
5. '- - - - - Welcome to the Client Interface ...' 
```
```
6. 2 
```
The client sends the packet to its corresponding router, which forwards it to the destination 33333.



*config_file_line.txt*

Simulation with 2 clients and 3 routers. To run this simulation, run the commands (each in a seperate terminal): 
```
1. python3 conn_router.py  
```
```
2. python3 router.py 0 127.0.0.1 22222
```
```
3. python3 router.py 1 127.0.0.1 33333
```
```
4. python3 router.py 2 127.0.0.1 44444
```
```
5. python3 client.py 22222
```
```
6. python3 client.py 44444
```



*config_file_circle.txt*

Simulation with 2 clients and 4 routers. To run this simulation, run the commands (each in a seperate terminal): 
```
1. python3 conn_router.py  
```
```
2. python3 router.py 0 127.0.0.1 22222
```
```
3. python3 router.py 1 127.0.0.1 33333
```
```
4. python3 router.py 2 127.0.0.1 44444
```
```
5. python3 router.py 3 127.0.0.1 34444
```
```
6. python3 client.py 22222
```
```
7. python3 client.py 34444
```



*config_file_combo.txt*

Simulation with 3 clients and 5 routers. To run this simulation, run the commands (each in a seperate terminal): 
```
1. python3 conn_router.py  
```
```
2. python3 router.py 0 127.0.0.1 22222
```
```
3. python3 router.py 1 127.0.0.1 33333
```
```
4. python3 router.py 2 127.0.0.1 44444
```
```
5. python3 router.py 3 127.0.0.1 34444
```
```
6. python3 router.py 4 127.0.0.1 34445
```
```
7. python3 client.py 22222
```
```
8. python3 client.py 44444
```
```
9. python3 client.py 34445
```
