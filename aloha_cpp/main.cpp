#include <stdio.h>
#include <stdlib.h>
#include <iostream>
#include <vector>

using namespace std;

#define TotScenario 100 //number of scenarios to be simulated
#define side        30     //side of the sqaure area where nodes are located (in meters) - not used
#define Tmax        11 //contention window size  //Nmax
#define NN          10
#define Tdata       20   //Tdata packet duration in unit of time  //maggiore uguale 3
#define Tslot       2     //Slot duration in unit of time - Tidle - Tbeacon
#define Tack        2    //Slot duration in unit of time
#define Tout        2    //Slot duration in unit of time
#define Tbackoff     2    //backoff duration in unit of time
#define nRetx       3    //max number of retransmissions
#define pa          1   //probability of transmission of the NN - pa

enum NodeState {
    idle, transmission, backoff, out
};

typedef struct {
    int id;
    double x; // coordinate x of its position
    double y; // coordinate y of its position
    bool hasDataToTransmit; //indicates if the node has data in the queue to be transmitted
    int attempt; // counts the number of times a packet is transmitted
    int delay; // variable used to compute delay
    unsigned long int time;// instant in which the node will change its state
    unsigned long int tx;  // transmission duration = Tdata
    bool hasCollision;
    NodeState state;
    double cycletime;
    double rtstime;
} node;

void init(node nodes[], int N);

void runSimulation(node nodes[], int N);

bool hasCollision(node nodes[], int sorg, int N);

double uniform();

double mean(vector<double> array);

double Ttot; //total time to be simulated per scenario for the tarsnmission of numPacch
double *pacchTX; //vector containing the number of packets transmitted by each source;
double *pacchTXtot; //vector containing the total number of packets transmitted by each source (TX e RITX)
double *pacchRX; //vector containing the number of packets correctly transmitted by each source/received by the destinatio;
double *pacchColl; //vector containing the number of packets collided
vector<double> *pacchCT; //vector containing the vector of cycle times
vector<double> *pacchRTST; //vector containing the vector of cycle times
double *pacchNCYCLES; //vector containing the average number of cycles
double *pacchNDATA; //vector containing the average number of transmissions
double *pacchNWODATA; //vector containing the average number of failure

double averpS; //average (over scenarios and nodes) success probability
double averpC;
double averpSnode; //average (over nodes for a scenario) success probability
double averpCnode;

double avertc;
double averrts;
double avertcnode;
double averrtsnode;

double averpcn;
double averpcnnode;
double averpfn;
double averpfnnode;

double delay;

int main() {

    FILE *fout;
    char file_out[200];
    sprintf(file_out, "Results_N=[1,%d].txt", NN);
    if ((fout = fopen(file_out, "wt")) == NULL)
    {
        printf("\nError opening the file <%s>\n", file_out);
        exit(2);
    }

    fprintf(fout, "Nodes;Average pS;Average pC;Average Etc time;Average Tdata time;Average p{cycle success};Average p{cycle failure}\n");

    Ttot = 20000 * Tslot;

    for (int currentNodesNumber = 1; currentNodesNumber <= NN; currentNodesNumber++)
    {

        averpS = 0;
        averpC = 0;
        avertc = 0;
        averrts = 0;
        averpcn = 0;
        averpfn = 0;

        for (int numScen = 1; numScen <= TotScenario; numScen++)
        {
            pacchTX = new double[currentNodesNumber];
            pacchTXtot = new double[currentNodesNumber];
            pacchRX = new double[currentNodesNumber];
            pacchColl = new double[currentNodesNumber];
            pacchCT = new vector<double>[currentNodesNumber];
            pacchRTST = new vector<double>[currentNodesNumber];
            pacchNCYCLES = new double[currentNodesNumber];
            pacchNDATA = new double[currentNodesNumber];
            pacchNWODATA = new double[currentNodesNumber];

            for (int i = 0; i < currentNodesNumber; i++)
            {
                pacchTX[i] = 0;
                pacchTXtot[i] = 0;
                pacchRX[i] = 0;
                pacchColl[i] = 0;
                pacchCT[i] = {};
                pacchRTST[i] = {};
                pacchNCYCLES[i] = 0;
                pacchNDATA[i] = 0;
                pacchNWODATA[i] = 0;
            }

            node *nodes;
            nodes = (node *) malloc(currentNodesNumber * sizeof(node));
            init(nodes, currentNodesNumber);

            runSimulation(nodes, currentNodesNumber);

            averpSnode = 0;
            averpCnode = 0;
            avertcnode = 0;
            averrtsnode = 0;
            averpcnnode = 0;
            averpfnnode = 0;

            for (int i = 0; i < currentNodesNumber; i++)
            {
                averpSnode = averpSnode + pacchRX[i] / pacchTX[i];
                averpCnode = averpCnode + pacchColl[i] / (pacchRX[i] + pacchColl[i]);
                avertcnode = avertcnode + mean(pacchCT[i]);
                averrtsnode = averrtsnode + mean(pacchRTST[i]);
                averpcnnode = averpcnnode + pacchNDATA[i] / pacchNCYCLES[i];
                averpfnnode = averpfnnode + pacchNWODATA[i] / pacchNCYCLES[i];
            }

            averpS = averpS + averpSnode / ((double) (currentNodesNumber));
            averpC = averpC + averpCnode / ((double) (currentNodesNumber));
            avertc = avertc + avertcnode / ((double) (currentNodesNumber));
            averrts = averrts + averrtsnode / ((double) (currentNodesNumber));
            averpcn = averpcn + averpcnnode / ((double) (currentNodesNumber));
            averpfn = averpfn + averpfnnode / ((double) (currentNodesNumber));

            free(nodes);
            free(pacchTX);
            free(pacchRX);
            free(pacchTXtot);
            free(pacchColl);
            free(pacchNDATA);
            free(pacchNCYCLES);
            free(pacchNWODATA);

            cout << "Scenario " << numScen << " for " << currentNodesNumber << " nodes" << endl;
        }

        averpS = averpS / TotScenario;
        averpC = averpC / TotScenario;
        avertc = avertc / TotScenario;
        averrts = averrts / TotScenario;
        averpcn = averpcn / TotScenario;
        averpfn = averpfn / TotScenario;

        fprintf(fout, "%d;%f;%f;%f;%f;%f;%f\n", currentNodesNumber, averpS, averpC, avertc, averrts, averpcn, averpfn);
    }

    fclose(fout);
    return 0;
}

void init(node nodes[], int N) {
    for (int i = 0; i < N; i++)
    {
        nodes[i].id = i;
        nodes[i].hasDataToTransmit = true;
        nodes[i].x = uniform() * side;
        nodes[i].y = uniform() * side;
        nodes[i].tx = Tdata;
        nodes[i].hasCollision = false;
        nodes[i].attempt = 0;
        nodes[i].delay = 0;
        nodes[i].state = idle;
        nodes[i].time = Tslot;
        nodes[i].cycletime = Tslot;
        nodes[i].rtstime = 0;
    }
}

void runSimulation(node nodes[], int N)
{
    for (int timer = 0; timer < Ttot; timer++)
    {
        for (int i = 0; i < N; i++)
        {
            if (timer == nodes[i].time)
            {
                switch (nodes[i].state)
                {
                    case idle:
                    {
                        if ((nodes[i].hasDataToTransmit == true) && (uniform() <= pa))
                        {
                            delay = rand() % (Tmax - 1);

                            nodes[i].attempt++;

                            if (delay == 0)
                            {
                                nodes[i].state = transmission;
                                nodes[i].hasCollision = false;
                                nodes[i].hasDataToTransmit = false;
                                nodes[i].time = nodes[i].time + nodes[i].tx;

                                nodes[i].rtstime = nodes[i].rtstime + nodes[i].tx;
                                nodes[i].cycletime = nodes[i].cycletime + nodes[i].tx;

                                pacchTX[i]++;
                            } else
                            {
                                nodes[i].state = backoff;
                                nodes[i].time = nodes[i].time + delay * Tbackoff;

                                nodes[i].cycletime = nodes[i].cycletime + delay * Tbackoff;
                            }
                        } else
                        {
                            nodes[i].time = nodes[i].time + Tslot;
                            nodes[i].cycletime = nodes[i].cycletime + Tslot;
                        }
                        break;
                    }

                    case transmission:
                    {
                        if (nodes[i].hasCollision == false)
                        {
                            nodes[i].state = idle;
                            nodes[i].time = nodes[i].time + Tack + Tslot;

                            nodes[i].cycletime = nodes[i].cycletime + Tack + Tslot;
                            pacchCT[i].push_back(nodes[i].cycletime);
                            pacchRTST[i].push_back(nodes[i].rtstime);
                            nodes[i].rtstime = 0;
                            nodes[i].cycletime = 0;
                            pacchNDATA[i]++;
                            pacchNCYCLES[i]++;

                            pacchRX[i]++;
                            nodes[i].attempt = 0;

                            nodes[i].hasDataToTransmit = true;
                        } else
                        {
                            nodes[i].state = out;
                            nodes[i].time = nodes[i].time + Tout;

                            nodes[i].cycletime = nodes[i].cycletime + Tout;
                        }
                        break;
                    }

                    case backoff:
                    {
                        nodes[i].state = transmission;
                        nodes[i].hasCollision = false;
                        nodes[i].hasDataToTransmit = false;
                        nodes[i].time = nodes[i].time + nodes[i].tx;

                        nodes[i].rtstime = nodes[i].rtstime + nodes[i].tx;
                        nodes[i].cycletime = nodes[i].cycletime + nodes[i].tx;

                        if (nodes[i].attempt == 1)
                        {
                            pacchTX[i]++;

                        }

                        break;
                    }

                    case out:
                    {
                        nodes[i].attempt++;
                        pacchColl[i]++;
                        if (nodes[i].attempt <= nRetx + 1)
                        {
                            delay = rand() % ((Tmax * nodes[i].attempt) - 1);

                            if (delay == 0)
                            {
                                nodes[i].state = transmission;
                                nodes[i].hasCollision = false;
                                nodes[i].hasDataToTransmit = false;
                                nodes[i].time = nodes[i].time + nodes[i].tx;

                                nodes[i].rtstime = nodes[i].rtstime + nodes[i].tx;
                                nodes[i].cycletime = nodes[i].cycletime + nodes[i].tx;

                            } else
                            {
                                nodes[i].state = backoff;
                                nodes[i].time = nodes[i].time + delay * Tbackoff;

                                nodes[i].cycletime = nodes[i].cycletime + delay * Tbackoff;
                            }
                        } else
                        {
                            nodes[i].state = idle;
                            nodes[i].time = nodes[i].time + Tslot;

                            nodes[i].cycletime = nodes[i].cycletime + Tslot;
                            pacchCT[i].push_back(nodes[i].cycletime);
                            pacchRTST[i].push_back(nodes[i].rtstime);
                            nodes[i].rtstime = 0;
                            nodes[i].cycletime = 0;
                            pacchNCYCLES[i]++;
                            pacchNWODATA[i]++;

                            nodes[i].hasDataToTransmit = true;
                            nodes[i].attempt = 0;
                        }
                        break;
                    }
                }
            } else
            {
                switch (nodes[i].state) {
                    case transmission:
                    {
                        nodes[i].hasCollision = hasCollision(nodes, nodes[i].id, N);

                        if (nodes[i].hasCollision == 1) {
                            break;
                        }
                    }
                }
            }
        }
    }
}

double mean(vector<double> array) {
    double sum = 0;
    for (int i = 0; i < array.size(); i++) {
        sum += array[i];
    }
    sum /= array.size();
    return sum;
}

bool hasCollision(node nodes[], int currentNodeId, int nodesCount) {
    for (int i = 0; i < nodesCount; i++) {
        if (nodes[i].id != currentNodeId && nodes[i].state == 1) {
            return true;
        }
    }

    return false;
}

/*-----------------generates a uniform RV between 0 and 1---------------*/
double uniform(void) {
    return rand() / (RAND_MAX + 1.);
}
