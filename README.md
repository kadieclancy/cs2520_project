# Wide Area Networks Project: User Manual

**Some notes about the code:**

1. The network relies on a central router that stores the physical topology of the whole network. This is called conn_router.py. New routers know the port/ip of conn_router and automatically connect to it when they become alive. 

2. Each router/client must be run in its own terminal window, including conn_router.py.

3. Since the whole thing is run locally, the IPs for all the routers is just loopback 127.0.0.1. The port numbers are used to differentiate different routers and different sockets within routers. 

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
2. python3 router.py 0 127.0.0.1 222222
```
```
3. python3 router.py 1 127.0.0.1 333333 
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
4. python3 client.py 22222
```
```
4. python3 client.py 4444
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
2. python3 router.py 2 127.0.0.1 44444
```
```
3. python3 router.py 3 127.0.0.1 34444
```
```
4. python3 client.py 22222
```
```
4. python3 client.py 34444
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
2. python3 router.py 2 127.0.0.1 44444
```
```
3. python3 router.py 3 127.0.0.1 34444
```
```
3. python3 router.py 4 127.0.0.1 34445
```
```
4. python3 client.py 22222
```
```
4. python3 client.py 44444
```
```
4. python3 client.py 34445
```
