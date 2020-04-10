# CSMA/CA simulator

This is simple CSMA/CA imitation model.

This program simulates Thrz radio network consisting of 1 access point (namely Gateway) and N sensor tags (namely Nodes).

Simulation starts with beacon message transmission by Gateway. During simulation RTS messages sent by Nodes could collide, in such case only allowed 3 RTS retries.

In order to run simulation you need

Prerequesites:
1. install python 3.6.2+
2. install numpy
3. download source code

How to run simulation:
* python sample_run.py 
