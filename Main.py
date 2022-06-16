import multiprocessing
import os,signal
import time # Temporal
NB_NODS=5 # Nodes to classify




"""
    Functions to launch processes
"""
import UDP_SRV
SRV_ADDR="127.0.0.1"
SRV_PORT=5000
def Launch_SRV_UDP(PIP_out:list):
    # Launch Server : Loria
    SRV_TIMOUT=10
    CLT_ADDR="127.0.0.1"
    print("[!] Launching SRV_UDP...")
    U=UDP_SRV.UDP_SRV(SRV_ADDR,SRV_PORT,SRV_TIMOUT,CLT_ADDR,PIP_out)
    U.Launch()


def Launch_SRV_TCP(PIP_out:list):
    # Launch Server : Montimage
    print("[!] Launching SRV_TCP...")
    # Will be handled if necessary


import Node
def Launch_NOD(PIP_in:list,PIP_out:list):
    # Launch Nodes
    print("[!]\t > Launching NOD...")
    N=Node.Node(PIP_in,PIP_out)
    N.Work()


import Aggregate
OUT="./Out.log"
def Launch_RED(PIP_in:list):
    # Launch Reduce
    print("[!] Launching RED...")
    Agg=Aggregate.Aggregate(PIP_in,OUT)
    Agg.Launch()
    # Blocks while traffic...
    Agg.Display()




"""
    Creates connexions
"""
# Connexions between MAP & NODES
MAP=[]
NOD_in=[]
for i in range(NB_NODS):
    map,nodi=multiprocessing.Pipe()
    MAP.append(map)
    NOD_in.append(nodi)

# Connexions between NODES & Reduce
NOD_out=[]
RED=[]
for i in range(NB_NODS):
    nodi,red=multiprocessing.Pipe()
    NOD_out.append(nodi)
    RED.append(red)




"""
    Launches processes
"""
srv = multiprocessing.Process(target=Launch_SRV_UDP, args=(MAP,))
srv.start()
Curr_T=time.time()
Nod_PIDs=[]
for i in range(NB_NODS):
    nod=multiprocessing.Process(target=Launch_NOD, args=(NOD_in[i],NOD_out[i]))
    nod.start()
    Nod_PIDs.append(nod.pid)
red=multiprocessing.Process(target=Launch_RED, args=(RED,))
red.start()




"""
    Kill Proceses
"""
# Waits srv to stop
srv.join()
for pid in Nod_PIDs:
    os.kill(pid,signal.SIGTERM)
red.join()


# https://www.geeksforgeeks.org/multiprocessing-python-set-2/
