# Wide Area Networks Project

Some notes about the current state of the code:

1. The network relies on a central router that stores the physical topology of the whole network. this is called conn_router. New routers know the port/ip of conn_router and automatically connect to it when they become alive. 



2. Each router/client must be run in its own terminal window, including conn_router. This is temporary, until I figure out how to actually use threads properly. 

3. Since the whole thing is run locally, the IPs for all the routers is just loopback 127.0.0.1. The port numbers are used to differentiate different routers and different sockets within routers. 

Currently, the program runs a simulation with 1 client and 2 routers, where the client sends a packet to the first router, who sends it to the second, at which point an ack is propogated packwards. This topology and the ports of the routers are hard coded in. To run this simulation, run the commands (each in a seperate terminal): 
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
4. python3 client.py 
```
```
5. 'Welcome. Type 1 for control information, 2 to send a file.' 
```
```
6. 2 7. 'Enter first hop port (22222):' 22222 
```
Here, we hard code the port for the first hop. The client sends the packet to port 22222, which forwards it to 33333.

##TODOS
```
0. control interface for application/client layer 
```
```
1. Figure out client/router interface, so the client does not have to hard code first hop in (include clients in network topologoy?)
```
```
2. Dijkstras / path finding from a hard-coded LSDB / connectivity matrix 
```
```
3. periodic alive messages to compute local topology 
```
```
4. LSA flooding, and using other LSA messages to update own LSDB 
```
```
5. error generation/handling (packet drops/corruption)
```

    
