"""
    Python Program To do the classification
"""
import joblib
import sklearn
import time




class Node:
    PIPE_in=""
    PIPE_out=""
    #ROOT="/home/philippe/Desktop/MOSAICO/Docs_These/Code/ML_Prod/"
    #ROOT="/home/madynes/Philippe/"
    MODEL_PTH="./DT_0.033.model"
    MODEL=""
    DICO={}
    IP_LAN=["192.168","2a01:e0a:3db:bcc0:","2a01:e0a:98a:6990:","152.81"]




    def __init__(self,pipin,pipout):
        self.PIPE_in=pipin
        self.PIPE_out=pipout
        self.MODEL=joblib.load(self.MODEL_PTH)


    def ipInLan(self,IP):
        end=False
        i=0
        lg=len(self.IP_LAN)
        while i<lg and not end:
            if self.IP_LAN[i] in IP:
                end=True
            i+=1
        return end


    def Work(self):
        while 1:
            # Read Pipe, Make classif
            pipe_data=self.PIPE_in.recv()
            strt=time.time()
            IPa=pipe_data[0]
            IPb=pipe_data[1]
            Fts=pipe_data[2]
            if self.ipInLan(IPa) and not self.ipInLan(IPb): # IPa the client / IPb the server
                lab=self.MODEL.predict([Fts])
                # Send Results
                self.PIPE_out.send( (IPa,IPb,lab,time.time()-strt) )
            elif not self.ipInLan(IPa) and self.ipInLan(IPb): # IPa the server / IPb the client
                IPa,IPb=IPb,IPa
                Fts=Fts[6:]+Fts[:6]
                lab=self.MODEL.predict([Fts])
                # Send Results
                self.PIPE_out.send( (IPa,IPb,lab,time.time()-strt) )

            # Temporary, just for iperf
            else:
                lab=self.MODEL.predict([Fts])
                # Send Results
                self.PIPE_out.send( (IPa,IPb,lab,time.time()-strt) )
