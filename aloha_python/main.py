import csv
import random
import statistics
from enum import Enum

TotScenario = 100 # number of scenarios to be simulated
side        = 30  # side of the sqaure area where nodes are located (in meters) - not used
Tmax        = 11  # contention window size
NN          = 10  # number of nodes
Tdata       = 20  # Tdata packet duration in unit of time  //maggiore uguale 3
Tslot       = 2   # Slot duration in unit of time - Tidle - Tbeacon
Tack        = 2   # Slot duration in unit of time
Tout        = 2   # Slot duration in unit of time
Tbackoff    = 2   # backoff duration in unit of time
nRetx       = 3   # max number of retransmissions
pa          = 1   # probability of transmission of the NN - pa
Ttot        = 20000 * Tslot

class NodeState(Enum):
    IDLE = "idle"
    TRANSMISSION = "transmission"
    BACKOFF = "backoff"
    OUT = "out"

class Node:
    def __init__(self):
        self.id = None
        self.x = None
        self.y = None
        self.hasDataToTransmit = None
        self.attempt = None
        self.delay = None
        self.time = None
        self.tx = None
        self.hasCollision = None
        self.state = None
        self.cycletime = None
        self.rtstime = None


def main():
    filename = "Results_N[%d-%d].csv" % (1, NN)
    kwargs = {'newline': ''}
    mode = 'w'

    with open(filename, mode, **kwargs) as fp:
        writer = csv.writer(fp, delimiter=';')

        writer.writerow(["Nodes","Average pS","Average pC","Average Etc time","Average Tdata time","Average p{cycle success}","Average p{cycle failure}"])

        for currentNodesNumber in range(1, NN+1):
            averpS = 0.0
            averpC = 0.0
            avertc = 0.0
            averrts = 0.0
            averpcn = 0.0
            averpfn = 0.0

            for numScen in range(1, TotScenario + 1):
                nodes = []
                init(nodes, currentNodesNumber)
                runSimulation(nodes, currentNodesNumber)

                averpSnode = 0.0
                averpCnode = 0.0
                avertcnode = 0.0
                averrtsnode = 0.0
                averpcnnode = 0.0
                averpfnnode = 0.0

                for node in nodes:
                    # print("Node %d had %d collisions" % (node.id, node.pacchColl))
                    if node.pacchRX  != 0:
                        averpSnode = averpSnode + node.pacchRX / node.pacchTX

                    if node.pacchRX + node.pacchColl != 0:
                        averpCnode = averpCnode + node.pacchColl / (node.pacchRX + node.pacchColl)

                    if node.pacchCT:
                        avertcnode = avertcnode + statistics.mean(node.pacchCT)

                    if node.pacchRTST:
                        averrtsnode = averrtsnode + statistics.mean(node.pacchRTST)

                    if node.pacchNCYCLES != 0:
                        averpcnnode = averpcnnode + node.pacchNDATA / node.pacchNCYCLES

                    if node.pacchNCYCLES  != 0:
                        averpfnnode = averpfnnode + node.pacchNWODATA / node.pacchNCYCLES

                averpS = averpS + (averpSnode / currentNodesNumber)
                averpC = averpC + (averpCnode / currentNodesNumber)
                avertc = avertc + (avertcnode / currentNodesNumber)
                averrts = averrts + (averrtsnode / currentNodesNumber)
                averpcn = averpcn + (averpcnnode / currentNodesNumber)
                averpfn = averpfn + (averpfnnode / currentNodesNumber)

                print("Scenario %d for %d nodes" % (numScen, currentNodesNumber))

            averpS = averpS / TotScenario
            averpC = averpC / TotScenario
            avertc = avertc / TotScenario
            averrts = averrts / TotScenario
            averpcn = averpcn / TotScenario
            averpfn = averpfn / TotScenario

            writer.writerow([currentNodesNumber, averpS, averpC, avertc, averrts, averpcn, averpfn])

def init(nodes, currentNodesNumber):
    for i in range(0, currentNodesNumber):
        node = Node()
        node.id = i
        node.hasDataToTransmit = True
        node.x = uniform() * side
        node.y = uniform() * side
        node.tx = Tdata
        node.hasCollision = False
        node.attempt = 0
        node.delay = 0
        node.state = NodeState.IDLE
        node.time = Tslot
        node.cycletime = Tslot
        node.rtstime = 0
    
        node.pacchTX = 0
        node.pacchTXtot = 0
        node.pacchRX = 0
        node.pacchColl = 0
        node.pacchCT = []
        node.pacchRTST = []
        node.pacchNCYCLES = 0
        node.pacchNDATA = 0
        node.pacchNWODATA = 0
        
        nodes.append(node)

def runSimulation(nodes, currentNodesNumber):
    for timer in range(0, Ttot + 1):
        for node in nodes:
            if timer == node.time:
                if node.state == NodeState.IDLE:
                    if node.hasDataToTransmit == True and uniform() <= pa:
                        delay = random.randrange(0, Tmax)

                        node.attempt += 1
                        
                        if delay == 0:
                            node.state = NodeState.TRANSMISSION
                            node.hasCollision = False
                            node.hasDataToTransmit = False
                            node.time = node.time + node.tx
                            
                            node.rtstime = node.rtstime + node.tx
                            node.cycletime = node.cycletime + node.tx

                            node.pacchTX += 1
                        else:
                            node.state = NodeState.BACKOFF
                            node.time = node.time + delay * Tbackoff

                            node.cycletime = node.cycletime + delay * Tbackoff
                    else:
                        node.time = node.time + Tslot
                        node.cycletime = node.cycletime + Tslot
                elif node.state == NodeState.TRANSMISSION:
                    if node.hasCollision == False:
                        node.state = NodeState.IDLE
                        node.time = node.time + Tack + Tslot

                        node.cycletime = node.cycletime + Tack + Tslot
                        node.pacchCT.append(node.cycletime)
                        node.pacchRTST.append(node.rtstime)
                        node.rtstime = 0
                        node.cycletime = 0
                        node.pacchNDATA += 1
                        node.pacchNCYCLES += 1

                        node.pacchRX += 1
                        node.attempt = 0

                        node.hasDataToTransmit = True
                    else:
                        node.state = NodeState.OUT
                        node.time = node.time + Tout

                        node.cycletime = node.cycletime + Tout

                elif node.state == NodeState.BACKOFF:
                    node.state = NodeState.TRANSMISSION
                    node.hasCollision = False
                    node.hasDataToTransmit = False
                    node.time = node.time + node.tx

                    node.rtstime = node.rtstime + node.tx
                    node.cycletime = node.cycletime + node.tx

                    if node.attempt == 1:
                        node.pacchTX += 1

                elif node.state == NodeState.OUT:
                    node.attempt += 1
                    node.pacchColl += 1

                    if node.attempt <= nRetx + 1:
                        delay = random.randrange(0, Tmax * node.attempt)

                        if delay == 0:
                            node.state = NodeState.TRANSMISSION
                            node.hasCollision = False
                            node.hasDataToTransmit = False
                            node.time = node.time + node.tx

                            node.rtstime = node.rtstime + node.tx
                            node.cycletime = node.cycletime + node.tx
                        else:
                            node.state = NodeState.BACKOFF
                            node.time = node.time + delay * Tbackoff

                            node.cycletime = node.cycletime + delay * Tbackoff
                    else:
                        node.state = NodeState.IDLE
                        node.time = node.time + Tslot

                        node.cycletime = node.cycletime + Tslot
                        node.pacchCT.append(node.cycletime)
                        node.pacchRTST.append(node.rtstime)
                        node.rtstime = 0
                        node.cycletime = 0
                        node.pacchNCYCLES += 1
                        node.pacchNWODATA += 1

                        node.hasDataToTransmit = True
                        node.attempt = 0
            else:
                if node.state == NodeState.TRANSMISSION:
                    node.hasCollision = hasCollision(nodes, node.id)

def hasCollision(nodes, currentNodeId):
    for node in nodes:
        if node.id != currentNodeId and node.state == NodeState.TRANSMISSION:
            return True
    return False

def uniform():
    return random.uniform(0, 1)

if __name__ == '__main__':
    main()