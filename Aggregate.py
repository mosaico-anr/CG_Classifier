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

import multiprocessing
import netaddr
import numpy as np
import time

class Aggregate:
    TAB_PIP=[] # Pipes nodes -> Aggregator
    DIC_GLB={} # Dictionary to aggregate
    TIMS=[] # Time to classify (Nodes)
    LASTS=0 # Experiment
    LOG="" # Log File


    def __init__(self,PIPsIN,OUT):
        self.TAB_PIP=PIPsIN
        self.LOG=open(OUT,"w")


    def Close_Connections(self):
        for pip in self.TAB_PIP:
            pip.close()


    def Launch(self):
        start=time.time()
        List_OK=multiprocessing.connection.wait(self.TAB_PIP,timeout=10)
        while List_OK:
            for pip in List_OK:
                # Retrieve DATA
                dat=pip.recv()
                IP1=dat[0]
                IP2=dat[1]
                Lab=dat[2]
                self.TIMS.append(dat[3])

                # Compute HASH & then INDEX
                Hash1=netaddr.IPAddress(IP1).value
                Hash2=netaddr.IPAddress(IP2).value
                Hash=Hash1*10**10+Hash2 # Concatenate HASHES

                # Update Dico
                if Hash not in self.DIC_GLB.keys():
                    self.DIC_GLB[Hash]=(0,0)
                Cpl=self.DIC_GLB[Hash]
                if Lab:
                    self.DIC_GLB[Hash]=(Cpl[0]+1,Cpl[1])
                else:
                    self.DIC_GLB[Hash]=(Cpl[0],Cpl[1]+1)
            List_OK=multiprocessing.connection.wait(self.TAB_PIP,timeout=10)
        end=time.time()-10 # Remove timeout
        self.LASTS=end-start
        print("[!] AGG : TIMEOUT")
        print("[!] AGG : Lasts ~ %f seconds"%(self.LASTS))
        self.Close_Connections()


    def Display(self):
        #print("\n[!] Classification Results:")
        nbCpl=0
        nbRpt=0
        for k,v in self.DIC_GLB.items():
            print("\t> %d : %d CG vs %d -> %f CG"%(k,v[0],v[1],float(v[0])/(v[0]+v[1])))
            IP1=str(k)[:10]
            # Remove first Zeros
            IP2=str(k)[10:]
            nbCpl+=1
            nbRpt+=(v[0]+v[1])
            i=0
            end=False
            while i<len(IP2) and not end:
                if IP2[i]!='0':
                    end=True
                else: i+=1
            IP2=str(k)[10+i:]
            # Print results
            print("\t> %s <-> %s \n"%(netaddr.IPAddress(IP1),netaddr.IPAddress(IP2)))
            if v[0]+v[1]>0:
                self.LOG.write("%s,%s,%d,%d,%f\n"%(netaddr.IPAddress(IP1),netaddr.IPAddress(IP2),v[0],v[1],float(v[0])/(v[0]+v[1])))
        self.LOG.close()

        if nbCpl>0:
            print("\n[!] AGG: Mean Time by classifier : %f "%np.mean(self.TIMS))
            print("[!] AGG: Nb conversations : %d, ~ %f reports per conversation"%(nbCpl,float(nbRpt)/nbCpl))
        if self.LASTS>0:
            print("[!] AGG: received %d classifs"%nbRpt)
            print("[!] AGG: ~%d classifs per second"%(float(nbRpt)/self.LASTS))
