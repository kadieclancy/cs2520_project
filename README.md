# Wide Area Networks Project
# User Manual

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
4. python3 client.py router_port [router_port that corresponds with the router you want the client to connect to]
```

**Test cases:**

Simulation with 1 client and 2 routers, where the client sends a packet to the first router, who sends it to the second, at which point an ack is propogated packwards. To run this simulation, run the commands (each in a seperate terminal): 
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
5. 'Welcome. Type 1 for control information, 2 to send a file.' 
```
```
6. 2 
```
```
7. 'Enter first hop port (33333):' 33333 
```
The client sends the packet to port 22222, which forwards it to 33333.

##TODOS
0. control interface for application/client layer 
```
```
1. Figure out client/router interface, so the client does not have to hard code first hop in (include clients in network topologoy?)
```
```
4. LSA flooding, and using other LSA messages to update own LSDB 
```
```
5. Max packet size for links
```
```
6. Breakdown of files into packets of max size, reassembly, and possible fragmentation
```
```

    
