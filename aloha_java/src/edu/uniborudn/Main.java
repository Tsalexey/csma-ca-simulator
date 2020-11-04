package edu.uniborudn;

import java.io.BufferedWriter;
import java.io.FileWriter;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import java.util.Random;

class Node {
    public int id;
    public double x; // coordinate x of its position
    public double y; // coordinate y of its position
    public boolean hasDataToTransmit; //indicates if the node has data in the queue to be transmitted
    public int attempt; // counts the number of times a packet is transmitted
    public int delay; // variable used to compute delay
    public long time;// instant in which the node will change its state
    public long tx;  // transmission duration = Tdata
    public boolean hasCollision;
    public Main.NodeState state;
    public double cycletime;
    public double rtstime;

    double pacchTX; //vector containing the number of packets transmitted by each source;
    double pacchTXtot; //vector containing the total number of packets transmitted by each source (TX e RITX)
    double pacchRX; //vector containing the number of packets correctly transmitted by each source/received by the destinatio;
    double pacchColl; //vector containing the number of packets collided
    List<Double> pacchCT; //vector containing the vector of cycle times
    List<Double> pacchRTST; //vector containing the vector of cycle times
    double pacchNCYCLES; //vector containing the average number of cycles
    double pacchNDATA; //vector containing the average number of transmissions
    double pacchNWODATA; //vector containing the average number of failure

    public Node() {
    }
}

public class Main {

    public static int TotScenario = 100; //number of scenarios to be simulated
    public static int side = 30;     //side of the sqaure area where nodes are located (in meters) - not used
    public static int Tmax = 11; //contention window size  //Nmax
    public static int NN = 10;
    public static int Tdata = 20;   //Tdata packet duration in unit of time  //maggiore uguale 3
    public static int Tslot = 2;     //Slot duration in unit of time - Tidle - Tbeacon
    public static int Tack = 2;    //Slot duration in unit of time
    public static int Tout = 2;    //Slot duration in unit of time
    public static int Tbackoff = 2;    //backoff duration in unit of time
    public static int nRetx = 3;    //max number of retransmissions
    public static int pa = 1;   //probability of transmission of the NN - pa
    public static int Ttot = 20000 * Tslot;

    enum NodeState {
        IDLE, TRANSMISSION, BACKOFF, OUT;
    }

    public static double averpS; //average (over scenarios and nodes) success probability
    public static double averpC;
    public static double averpSnode; //average (over nodes for a scenario) success probability
    public static double averpCnode;

    public static double avertc;
    public static double averrts;
    public static double avertcnode;
    public static double averrtsnode;

    public static double averpcn;
    public static double averpcnnode;
    public static double averpfn;
    public static double averpfnnode;

    public static void main(String[] args) throws IOException {
        BufferedWriter out = null;
        try {

            FileWriter fstream = new FileWriter("Results_N=[" + 1 + "-" + NN + "].txt");
            out = new BufferedWriter(fstream);
            out.write("Nodes;Average pS;Average pC;Average Etc time;Average Tdata time;Average p{cycle success};Average p{cycle failure}\n");


            for (int currentNodesNumber = 1; currentNodesNumber <= NN; currentNodesNumber++) {
                averpS = 0;
                averpC = 0;
                avertc = 0;
                averrts = 0;
                averpcn = 0;
                averpfn = 0;

                for (int numScen = 1; numScen <= TotScenario; numScen++) {
                    List<Node> nodes = new ArrayList<>();
                    init(nodes, currentNodesNumber);
                    runSimulation(nodes, currentNodesNumber);

                    averpSnode = 0;
                    averpCnode = 0;
                    avertcnode = 0;
                    averrtsnode = 0;
                    averpcnnode = 0;
                    averpfnnode = 0;

                    for (Node node : nodes) {
                        averpSnode = averpSnode + node.pacchRX / node.pacchTX;
                        averpCnode = averpCnode + node.pacchColl / (node.pacchRX + node.pacchColl);
                        avertcnode = avertcnode + mean(node.pacchCT);
                        averrtsnode = averrtsnode + mean(node.pacchRTST);
                        averpcnnode = averpcnnode + node.pacchNDATA / node.pacchNCYCLES;
                        averpfnnode = averpfnnode + node.pacchNWODATA / node.pacchNCYCLES;
                    }

                    averpS = averpS + averpSnode / ((double) (currentNodesNumber));
                    averpC = averpC + averpCnode / ((double) (currentNodesNumber));
                    avertc = avertc + avertcnode / ((double) (currentNodesNumber));
                    averrts = averrts + averrtsnode / ((double) (currentNodesNumber));
                    averpcn = averpcn + averpcnnode / ((double) (currentNodesNumber));
                    averpfn = averpfn + averpfnnode / ((double) (currentNodesNumber));

                    System.out.println("Scenario " + numScen + " for " + currentNodesNumber + " nodes");
                }

                averpS = averpS / TotScenario;
                averpC = averpC / TotScenario;
                avertc = avertc / TotScenario;
                averrts = averrts / TotScenario;
                averpcn = averpcn / TotScenario;
                averpfn = averpfn / TotScenario;

                out.write(String.format("%d;%f;%f;%f;%f;%f;%f\n", currentNodesNumber, averpS, averpC, avertc, averrts, averpcn, averpfn));
            }
        } catch (IOException e) {
            System.err.println("Error: " + e.getMessage());
        } finally {
            if (out != null) {
                out.close();
            }
        }
    }

    private static void init(List<Node> nodes, int currentNodesNumber) {
        for (int i = 0; i < currentNodesNumber; i++) {
            Node node = new Node();

            node.id = i;
            node.hasDataToTransmit = true;
            node.x = uniform() * side;
            node.y = uniform() * side;
            node.tx = Tdata;
            node.hasCollision = false;
            node.attempt = 0;
            node.delay = 0;
            node.state = NodeState.IDLE;
            node.time = Tslot;
            node.cycletime = Tslot;
            node.rtstime = 0;

            node.pacchTX = 0;
            node.pacchTXtot = 0;
            node.pacchRX = 0;
            node.pacchColl = 0;
            node.pacchCT = new ArrayList<>();
            node.pacchRTST = new ArrayList<>();
            node.pacchNCYCLES = 0;
            node.pacchNDATA = 0;
            node.pacchNWODATA = 0;

            nodes.add(node);
        }
    }

    private static void runSimulation(List<Node> nodes, int N) {
        {
            Random rand = new Random();

            for (int timer = 0; timer < Ttot; timer++) {
                for (Node node : nodes)
                    if (timer == node.time) {
                        switch (node.state) {
                            case IDLE: {
                                if ((node.hasDataToTransmit == true) && (uniform() <= pa)) {
                                    int delay = rand.nextInt(Tmax - 1);

                                    node.attempt++;

                                    if (delay == 0) {
                                        node.state = NodeState.TRANSMISSION;
                                        node.hasCollision = false;
                                        node.hasDataToTransmit = false;
                                        node.time = node.time + node.tx;

                                        node.rtstime = node.rtstime + node.tx;
                                        node.cycletime = node.cycletime + node.tx;

                                        node.pacchTX++;
                                    } else {
                                        node.state = NodeState.BACKOFF;
                                        node.time = node.time + delay * Tbackoff;

                                        node.cycletime = node.cycletime + delay * Tbackoff;
                                    }
                                } else {
                                    node.time = node.time + Tslot;
                                    node.cycletime = node.cycletime + Tslot;
                                }
                                break;
                            }

                            case TRANSMISSION: {
                                if (node.hasCollision == false) {
                                    node.state = NodeState.IDLE;
                                    node.time = node.time + Tack + Tslot;

                                    node.cycletime = node.cycletime + Tack + Tslot;
                                    node.pacchCT.add(node.cycletime);
                                    node.pacchRTST.add(node.rtstime);
                                    node.rtstime = 0;
                                    node.cycletime = 0;
                                    node.pacchNDATA++;
                                    node.pacchNCYCLES++;

                                    node.pacchRX++;
                                    node.attempt = 0;

                                    node.hasDataToTransmit = true;
                                } else {
                                    node.state = NodeState.OUT;
                                    node.time = node.time + Tout;

                                    node.cycletime = node.cycletime + Tout;
                                }
                                break;
                            }

                            case BACKOFF: {
                                node.state = NodeState.TRANSMISSION;
                                node.hasCollision = false;
                                node.hasDataToTransmit = false;
                                node.time = node.time + node.tx;

                                node.rtstime = node.rtstime + node.tx;
                                node.cycletime = node.cycletime + node.tx;

                                if (node.attempt == 1) {
                                    node.pacchTX++;
                                }

                                break;
                            }

                            case OUT: {
                                node.attempt++;
                                node.pacchColl++;

                                if (node.attempt <= nRetx + 1) {
                                    int delay = rand.nextInt((Tmax * node.attempt) - 1);

                                    if (delay == 0) {
                                        node.state = NodeState.TRANSMISSION;
                                        node.hasCollision = false;
                                        node.hasDataToTransmit = false;
                                        node.time = node.time + node.tx;

                                        node.rtstime = node.rtstime + node.tx;
                                        node.cycletime = node.cycletime + node.tx;

                                    } else {
                                        node.state = NodeState.BACKOFF;
                                        node.time = node.time + delay * Tbackoff;

                                        node.cycletime = node.cycletime + delay * Tbackoff;
                                    }
                                } else {
                                    node.state = NodeState.IDLE;
                                    node.time = node.time + Tslot;

                                    node.cycletime = node.cycletime + Tslot;
                                    node.pacchCT.add(node.cycletime);
                                    node.pacchRTST.add(node.rtstime);
                                    node.rtstime = 0;
                                    node.cycletime = 0;
                                    node.pacchNCYCLES++;
                                    node.pacchNWODATA++;

                                    node.hasDataToTransmit = true;
                                    node.attempt = 0;
                                }
                                break;
                            }
                        }
                    } else {
                        switch (node.state) {
                            case TRANSMISSION: {
                                node.hasCollision = hasCollision(nodes, node.id, N);

                                if (node.hasCollision == true) {
                                    break;
                                }
                            }
                        }
                    }
            }
        }
    }


    public static boolean hasCollision(List<Node> nodes, int currentNodeId, int nodesCount) {
        for (int i = 0; i < nodesCount; i++) {
            if (nodes.get(i).id != currentNodeId && nodes.get(i).state.equals(NodeState.TRANSMISSION)) {
                return true;
            }
        }

        return false;
    }

    static double mean(List<Double> list) {
        double sum = 0;

        for (Double value : list) {
            sum += value;
        }

        sum /= list.size();

        return sum;
    }

    public static double uniform() {
        return Math.random();
    }
}
