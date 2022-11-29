# Copyright (c) 2022 Centre National de la Recherche Scientifique All Rights Reserved. 
#
# This file is part of MOSAICO PROJECT.
#
# MOSAICO PROJECT is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# MOSAICO PROJECT is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with MOSAICO PROJECT. See the file COPYING.  If not, see <http://www.gnu.org/licenses/>.

import time
import socket
import json


class UDP_SRV:
    # CONF
    SRV_ADDR=""
    SRV_PORT=0
    SRV_TIMO=0
    CLT_ADDR="" # Addr of the probe: filtering

    # FIELDS REPORT
    IP1=0
    IP2=2
    UP_STAT=4
    DW_STAT=5
    ####
    NB_PAK=0
    MEAN_S=1
    STD_S=2
    MEAN_I=3
    STD_I=4

    # Processes
    Tab_Proc=[]
    NB_Nods=0
    Idf_RR=0




    def __init__(self,srv_addr,srv_port,srv_timeout,clt_addr,PIPs):
        self.SRV_ADDR=srv_addr
        self.SRV_PORT=srv_port
        self.SRV_TIMO=srv_timeout
        self.CLT_ADDR=clt_addr
        self.Tab_Proc=PIPs
        self.NB_Nods=len(PIPs)


    def Handle_Report(self,UDP_pak):
        # Goal is to handle the report of Xavier
        Msg=UDP_pak.decode()
        JS=json.loads(Msg)
        # Check Nb Fields OK
        if (len(JS)==6):
            D=JS[self.DW_STAT]
            U=JS[self.UP_STAT]
            if(len(D)==5 and len(U)==5):
                # Give the work
                SumSZ_DW=JS[self.DW_STAT][self.MEAN_S] * JS[self.DW_STAT][self.NB_PAK]
                SumSZ_UP=JS[self.UP_STAT][self.MEAN_S] * JS[self.UP_STAT][self.NB_PAK]
                Fts=[ JS[self.DW_STAT][self.MEAN_S], JS[self.DW_STAT][self.STD_S], JS[self.DW_STAT][self.MEAN_I], JS[self.DW_STAT][self.STD_I], SumSZ_DW , JS[self.DW_STAT][self.NB_PAK],
                JS[self.UP_STAT][self.MEAN_S], JS[self.UP_STAT][self.STD_S], JS[self.UP_STAT][self.MEAN_I], JS[self.UP_STAT][self.STD_I], SumSZ_UP , JS[self.UP_STAT][self.NB_PAK] ]
                self.Tab_Proc[self.Idf_RR].send((JS[self.IP1],JS[self.IP2],Fts))

                # Round Robin
                self.Idf_RR=(self.Idf_RR+1)%self.NB_Nods


    def Close_Connections(self):
        for pip in self.Tab_Proc:
            pip.close()


    def Launch(self):
        # Launch UDP server
        serveur = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        serveur.bind((self.SRV_ADDR, self.SRV_PORT))
        serveur.settimeout(self.SRV_TIMO)

        zero_tim=time.time()
        start=time.time()
        Nb_Rep=0
        while True:
            try:
                data,addr=serveur.recvfrom(1024)
            except:
                # Reached the Timeout
                print("[!] UDP_SRV: TIMEOUT 1 : SRV")
                print("[!] UDP_SRV: received %d reports"%Nb_Rep)
                print("[!] UDP_SRV: Lasts ~ %f seconds"%(start-zero_tim))
                if start-zero_tim>0:
                    print("[!] UDP_SRV: ~%f reports per sec"%(float(Nb_Rep)/(start-zero_tim)))
                self.Close_Connections()
                exit(0)
            else:
                # IF IP sniffer (limit to the probe's traffic)
                if addr[0]==self.CLT_ADDR and addr[1]!=53:
                    start=time.time()
                    Nb_Rep+=1
                    self.Handle_Report(data)
                # There is traffic, but not good one
                elif time.time()-start>self.SRV_TIMO:
                    PRINT("[!] UDP_SRV: TIMEOUT 2 : SRV")
                    print("[!] UDP_SRV: received %d reports"%Nb_Rep)
                    print("[!] UDP_SRV : Lasts ~ %f seconds"%(start-zero_tim))
                    if start-zero_tim>0:
                        print("[!] UDP_SRV: ~%f reports per sec"%(float(Nb_Rep)/(start-zero_tim)))
                    self.Close_Connections()
                    exit(0)
