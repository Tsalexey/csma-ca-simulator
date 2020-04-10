# CSMA/CA simulator

This is simple CSMA/CA imitation model.

This simulation framework represents a Thrz radio network consisting of 1 access point (namely Gateway) and N sensor tags (namely Nodes).

Simulation starts with beacon message transmission by Gateway. During simulation RTS messages sent by Nodes could collide.

At the moment 2 scenarios are provided:
1) Simulation finishes when GW get 3 collisions **allow_n_retries_at_gw**
2) Simulation lasts until all the Node doesn't send user data **unlimited_time_for_all_tags_polling**

Prerequesites:
1. install python 3.6.2+
2. install numpy
3. download source code

How to run simulation:
* python sample_run.py 
