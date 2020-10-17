# CSMA/CA simulator

## What is this?

This is event-driven continuous-time simulator of CSMA/CA protocol

## What does it do?

This simulator allows to estimate performance of the MAC layer in a radio network that uses CSMA/CA protocol with RTS/CTS session initiation procedure.

## What is simulation setup?

:white_check_mark: Access Point - Gateway that receives data

:white_check_mark: N nodes that transmitts data and compete for the channel

## What are performance metrics?
* Probability of successfull data transmission
* Probability of failed data transmission
* Collision  probability of RTS message at the Gateway
* Mean tranmission cycle time
* Ration between data transmission and transmission cycle time

## How it works?

<Protocol description should be here>
  
## What do I need to run the simulator?

1. install python 3.6.2+
2. install numpy
3. download source code
4. execute __unibo_rudn/simulation/sample_run.py__ or __unibo_rudn/simulation/collect_statistics_run.py__

## How to change input parameters

Input parameters could be found in __unibo_rudn/input/reslistic_input1.py__

| Parameter | Description |
|----------------|:---------:|
| is_debug_cycle_info | Output information about node cycle states and timings |
| sensing | Allows a node to sense the channel. In __true__ the node will detect CTS message in the channel and wait till the end of detected transmission | 
| mode | CYCLIC - after successful data transmission the node tries to send new data packet|
| simulation_time | requirested simulation time |
| Nretx | Number of allowed RTS retransmissions in case of collision |
| NN | Nodes number |
| p_a | Probability that node has a data packet to transmit|
| B | Channel bandwith |
| eta | Spectral efficiency |
| rb | Bit rate |
| sphere_radius | Sphere radius within which ode are distributed uniformly |
| c | light speed constant|
| Ldata | Data packet size (bytes) |
| Ldatapay | Data packet payload (bytes)|
| Lack | ACK message size (bytes) |
| Lrts | RTS message size (bytes) |
| Lcts | CTS message size (bytes) |
| Lbeacon | BEACON message size (bytes) |
| Tdata | data transmission time |
| Tack | ACK transmission time |
| Trts | RTS transmission time |
| Tcts | CTS transmission time |
| Tbeacon | BEACON transmission time |
| Tbo | Backoff duration |
| Tdatacts | Channel busy time due to transmission |
| Tout | CTS resposne waiting timeout |
| Tidle | IDLE timeout before checkg if there is a new message data for transmission |
| Twait | Waiting timeout due to detected transmissio|
| Tmax | Backoff right boundary multiplier |



