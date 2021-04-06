#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <iostream>
#include <fstream>
#include <cmath>
#include <vector>
#include <time.h>
#include <cstdlib>

using namespace std;


/*----------Define per Ran2------*/
#define IM1 2147483563
#define IM2 2147483399
#define AM (1.0/IM1)
#define IMM1 (IM1-1)
#define IA1 40014
#define IA2 40692
#define IQ1 53668
#define IQ2 52774
#define IR1 12211
#define IR2 3791
#define NTAB 32
#define NDIV (1+IMM1/NTAB)
#define EPS 1.2e-7
#define RNMX (1.0-EPS)
/*---------------------------------*/

long seed = -50;  //chiave per la funzione random

/*-----Scenario Parameters--------------------*/

#define TotScenario 100      //number of scenarios to be simulated
#define TotPacch    1000    //number of packets to be simulated
#define side        30     //side of the square area where nodes are located (in meters) - not used
#define ray         15    // ray of sphere - not used
#define W           12   //contention window size  //Tmax

#define Pt       0.001     //transmit power - not used
#define Node     20       //number of nodes
#define du       1.13    //source - destionation distance in meters  - not used
#define data     3     //data packet duration in unit of time
#define Tslot    3     //Slot duration in unit of time - Tidle - Tbeacon
#define Tack     3
#define Tout     data+Tack   //Tout=Tdata+Tack
#define Trts     3
#define Tcts     3
#define Twait    data+Tack    //Twait=Tdata+Tack
#define backoff  3    //backoff duration in unit of time
#define rmax     3   //max number of retransmissions

/*---PHY Parameters----*/ // not used

#define alpha 100000 //capture threshold in dB-not used
#define lamda 0.125 //wavelength

/*------Channel Parameters------*/ //not used

#define beta 3    //propagation coefficient

/*----------------MAC Parameters-----------------*/
#define g    1   //probability of transmission for a node - pa

/*---------------------struttura sensore-------------------*/
typedef struct {

    int ns;//node ID
    double x;   //coordinate x of its position
    double y;   //coordinate y of its position
    int token;  //indicates if the node has data in the queue to be transmitted
    int numtx;  //node attempt
    int delay;  //variable used to compute delay
    unsigned long int time;   //instant in which the node will change its status
    unsigned long int tx;     //transmission duration = data
    bool colliso;             //specifies if a node has collided
    bool sense;               //specifies if a CTS is sensed during BO
    bool sense2;              //specifies id a CTS is sensed during OUT
    int state;                //state of the node: 0 = idle; 1 = transmission RTS; 2 = backoff; 3 = out; 4=rx_cts; 5=Tx_data; 6=Wait
    double ctstime;
}sensore;

void inizializza(sensore elenco[], int N, FILE * fout1);
void accesso(sensore elenco[], int N, FILE * fout1);
double uniforme();
int PoissonRandomNumber(double lambda, double area); //not used
double ran2(long *idum);

bool Colliso(sensore elenco[], int *vectState, int sorg, int N, FILE * fout1);
bool Sensing(sensore elenco[], int* vectState,int N, FILE* fout1);
bool Sensing2(sensore elenco[], int* vectState, int N, FILE* fout1);


double Ttot;        //total time to be simulated per scenario for the tarsnmission of numPacch

double *pacchTX;    //vector containing the number of packets transmitted by each source;
double *pacchTXtot; //vector containing the total number of packets transmitted by each source (TX e RITX)
double *pacchRX;    //vector containing the number of packets correctly transmitted by each source/received by the destinatio;
double *pacchColl;  //vector containing the number of packets collided
double* pacchCollIgnored;  //vector containing the number of packets collided
double *pacchCTS;   //vector containing the number of CTS transmitted
double *pacchRTS;   //vector containing the number of RTS transmitted
double *pFree;      //vector containing the number of times the channel is sensed free
double *pBusy;      //vector containing the number of times the channel is sensed busy
double *pChannel;   //vector containing the number of times the channel is sensed
int *vectState;     //vector containing the state of each node saved
int* delayNode;     //vector containing the delay of each node saved


double averpS; //average (over scenarios and nodes) success probability
double averpC;
double averpSnode; //average (over nodes for a scenario) success probability
double averpCnode;
double averpInode;
double averpI;

double averpF; //average (over scenarios and nodes) probability that the channel is free
double averpB; //average (over scenarios and nodes) probability that the channel is busy
double averpFnode;
double averpBnode;
double averpCTS;
double averpCTSnode;
double averpCTScycle;

double avertc;
double averrts;
double avertcnode;
double averrtsnode;

double averpcn;
double averpcnnode;
double averpfn;
double averpfnnode;
int delay;
bool *sensed_channel;


/*--------------------------------------------MAIN---------------------------------------------------*/
int main()
{
    FILE *fout1;                                                               //   file
    char file_out1[800];                                                       //    di
    sprintf(file_out1,"Output.txt");                                      //  output
    if ((fout1=fopen(file_out1,"wt"))==NULL)
    {printf("\nErrore nell'apertura del file <%s>\n",file_out1);exit(1);}

    FILE *fout2;                                                               //   file
    char file_out2[800];                                                       //    di
    sprintf(file_out2,"Results_N=%d.txt",Node);                                      //  output
    if ((fout2=fopen(file_out2,"wt"))==NULL)
    {printf("\nErrore nell'apertura del file <%s>\n",file_out2);exit(2);}


    int i,j;
    int N; //numer of sensors deployed
    int numScen;
    double area;

    area=side*side;
    Ttot=100000*Tslot;
//Ttot = 100*Tslot;
    //Ttot = 50 * Tslot;

    fprintf(fout2, "Nodes;Average pS;Average pC;Average pI;Average pFree;Average pBusy\n");

    for (int currentNodesNumber = 1; currentNodesNumber <= Node; currentNodesNumber++) {

        averpS = 0;
        averpC = 0;
        averpI = 0;

        averpF = 0;
        averpB = 0;
        averpCTS = 0;

        avertc = 0;
        averrts = 0;
        averpcn = 0;
        averpfn = 0;
        int tScen = TotScenario;
        // ------------------Beginning of each scenario --------------------------//

        for (int numScen = 1; numScen <= TotScenario; numScen++)  //consider 1000 scenarios
        {
            double j = 0;
            double y = 0;
            N = currentNodesNumber;

            pacchTX = new double[N];
            pacchTXtot = new double[N];
            pacchRX = new double[N];
            pacchColl = new double[N];
            pacchCollIgnored = new double[N];
            pacchCTS = new double[N];
            pacchRTS = new double[N];

            pFree = new double[N];
            pBusy = new double[N];
            pChannel = new double[N];

            vectState = new int[N];
            delayNode= new int[N];
            sensed_channel = new bool[N];


            for (i = 0; i < N; i++)
            {
                pacchTX[i] = 0;
                pacchTXtot[i] = 0;
                pacchRX[i] = 0;
                pacchColl[i] = 0;
                pacchCollIgnored[i] = 0;
                pacchCTS[i] = 0;
                pacchRTS[i] = 0;

                pFree[i] = 0;
                pBusy[i] = 0;
                pChannel[i] = 0;

                vectState[i] = 0;
                delayNode[i] = 0;

                sensed_channel[i] = false;
            }

            sensore* elenco;//puntatore al tipo sensore per l'array di sensori
            elenco = (sensore*)malloc(N * sizeof(sensore));//crea l'elenco di sensori
            inizializza(elenco, N, fout1);


            accesso(elenco, N, fout1);  //accesso al canale da parte dei nodi

            averpSnode = 0;
            averpCnode = 0;
            averpInode = 0;

            averpFnode = 0;
            averpBnode = 0;

            for (i = 0; i < N; i++)
            {

                averpSnode = averpSnode + (pacchCTS[i] / pacchRTS[i]);
                averpCnode = averpCnode + (pacchColl[i] / pacchTXtot[i]);
                averpInode = averpInode + (pacchCollIgnored[i] / pacchTXtot[i]);

                averpFnode = averpFnode + pFree[i] / (pChannel[i]);
                averpBnode = averpBnode + pBusy[i] / (pChannel[i]);

            }

            averpS = averpS + averpSnode / ((double)(N));
            averpC = averpC + averpCnode / ((double)(N));
            averpI = averpI + averpInode / ((double)(N));

            averpF = averpF + averpFnode / ((double)(N));
            averpB = averpB + averpBnode / ((double)(N));

            free(elenco);
            free(pacchTX);
            free(pacchRX);
            free(pacchTXtot);
            free(pacchColl);
            free(pacchCollIgnored);
            free(pacchCTS);
            free(pacchRTS);
            free(pFree);
            free(pBusy);
            free(vectState);
            free(delayNode);

            free(sensed_channel);
            cout << "Scenario " << numScen << " for " << currentNodesNumber << " nodes" << endl;

        }

        averpS = averpS / TotScenario;
        averpC = averpC / TotScenario;
        averpI = averpI / TotScenario;

        averpF = averpF / TotScenario;
        averpB = averpB / TotScenario;

        fprintf(fout2, "%d;%f;%f;%f;%f%;f\n", currentNodesNumber, averpS, averpC, averpI, averpF, averpB);
        //cout << currentNodesNumber << " node: pSuccess= " << averpS << "; pCollsion = " << averpC << "; pFree = " << ";\n" << endl;
    }
    fclose(fout1);
    fclose(fout2);
    return 0;
}//fine main




/*------------funzione che inizializza l'array di sensori--------------*/
void inizializza(sensore elenco[], int N, FILE *fout1)
{   int i;

    double prob; //evaluate the probability to transmit

    for(i=0; i<N; i++)
    {

        elenco[i].ns = i;
        elenco[i].token = 1; //means that the source can trasnmit data
        elenco[i].x = uniforme()*side; //assegno le posizioni ai sensori
        elenco[i].y = uniforme()*side; //assegno le posizioni ai sensori
        elenco[i].tx =data;
        elenco[i].colliso = 0;
        elenco[i].sense = 0;
        elenco[i].sense2 = 0;
        elenco[i].numtx = 0;
        elenco[i].delay = 0;
        elenco[i].state=0;   //the node enetres in idle till the next slot
        elenco[i].time=Tslot;
        elenco[i].ctstime = 0;
    }
}



/*----------------funzione che realizza l'accesso al canale da parte di CH tramite CSMA----------------*/
void accesso(sensore elenco[], int N, FILE *fout1)
{ int i;
    int z = 0;
    int t = 0; //timer, simulates time passing
    int y = 0;
    double prob; //to compute the probability that the node transmits

//  fprintf(fout1,"Inizio l'accesso \n");
    for (t=0; t<Ttot; t++)
    {
        for (i = 0; i < N; i++) //per ogni nodo valuto lo stato attuale e lo aggiorno
        {
            vectState[i] = elenco[i].state;
            //cout << "Node " << elenco[i].ns << " has vectState " << vectState[i] << "\n" << endl;
        }
        for (i = 0; i < N; i++) //evaluation of each node state and update it
        {
            if (t==elenco[i].time)  //final instant of Idle o TX-RTS o BO o out o wait o RX-CTS o TX-DATA
            {
                switch (vectState[elenco[i].ns]) //check the status
                {
                    case 0:  //Idle
                    {
                        //cout << "Node " << elenco[i].ns << " is in IDLE: attempt " << elenco[i].numtx << "\n" << endl;

                        prob = uniforme();  //for evaluating pa

                        if ((elenco[i].token==1)&&(prob<=g)) //if node has a packet ready to be transmitted
                        {
                            elenco[i].numtx++; //increase node attempt
                            int p = pow(2, elenco[i].numtx); //power of 2: 2^(i) where i= node attempt
                            delay = 1 + (rand() % (p*W));    // delay random between 1 and W*2^(i)

                            elenco[i].state=2;               //go to BO state
                            elenco[i].sense = 0;
                            delayNode[i] = delay;            //save delay in a vector for that specific node

                            elenco[i].time = elenco[i].time + delay*backoff;   //update value of elenco[i].time to specify for how long the node remains in BO state

                            //cout << "Node " << elenco[i].ns << " from IDLE goes to BACKOFF with delay " << delay << " until t= " << elenco[i].time << " (attempt: " << elenco[i].numtx << " )\n" << endl;
                        }

                        else //remain in idle
                        {
                            elenco[i].time=elenco[i].time+Tslot;
                            //cout << "t= " << elenco[i].time << "\n" << endl;

                        }
                        break;
                    }

                    case 1:  //TX RTS
                    {

                        if (elenco[i].colliso == 0) {          //check if there could be a collision at the end of RTS transmission
                            elenco[i].colliso = Colliso(elenco, vectState, elenco[i].ns, N, fout1);
                        }

                        if (elenco[i].colliso == 0) {         //no collision

                            elenco[i].state = 4;              //the node enters in RX_CTS

                            elenco[i].time = elenco[i].time + Tcts;

                            pacchCTS[i]++;                    //GW sends a CTS to the node that had success

                            //cout << "Node " << elenco[i].ns << " does not collide and enters in RX-CTS until t= " << elenco[i].time << "(attempt " << elenco[i].numtx << " )\n" << endl;
                            //cout << "Value of paccCTS[" << elenco[i].ns << "] = " << pacchCTS[i] << "\n" << endl;

                        }
                        else {                                //collision

                            elenco[i].state = 3;              //the node enters in Tout state
                            elenco[i].time = elenco[i].time + Tout;

                            pacchColl[i]++;                  //increase number of packets collided

                            /*for (int j = 0; j < N; j++) { //CASE RTS IGNORED
                                if (vectState[j] == 1 && j != i) { //CHECK FOR COLLISION
                                    z = 1;
                                }
                            }
                            for (int j = 0; j < N; j++) {
                                if (z != 1) {
                                if (vectState[j] == 4 && j != i) { // CHECK FOR RTS IGNORED

                                        z = 2;
                                    }
                                    // cout << "Since node " << elenco[j].ns << " is in RX-CTS, RTS  is ignored for node " << elenco[i].ns << " )\n" << endl;
                                }
                            }

                            if (z == 1) {
                                pacchColl[i]++;
                                z = 0;
                            }
                            if (z == 2) {
                                pacchCollIgnored[i]++;
                                z = 0;
                            }
                            */

                            //cout << "Node " << elenco[i].ns << " collides and goes to OUT until t= " << elenco[i].time << " (attempt " << elenco[i].numtx << " )\n" << endl;
                            //cout << "Value of paccColl[" << elenco[i].ns << "] = " << pacchColl[i] << "\n" << endl;

                        }

                        break;
                    }

                    case 2:  //Backoff
                    {

                        elenco[i].sense = Sensing(elenco, vectState, N, fout1);   //sensing of the channel

                        if (elenco[i].sense == 0) {                               //no CTS

                            elenco[i].state = 1;                                 // RTS transmission
                            elenco[i].colliso = 0;
                            elenco[i].token = 0;

                            elenco[i].time = elenco[i].time + Trts;

                            pacchTXtot[i]++;                                     //accounts also for retransmissions
                            pFree[i]++;                                          //channel free
                            pChannel[i]++;

                            //cout << "Node " << elenco[i].ns << " senses channel FREE and goes to TX-RTS until t= "<< elenco[i].time<<" (attempt " << elenco[i].numtx << " )\n" << endl;

                            if (elenco[i].numtx == 1) // first attempt of the node -> I increase paccRTS[i], we don't account for Retransmissions
                            {
                                pacchRTS[i]++;
                                //cout << "Value of paccRTS[" << elenco[i].ns << "] = " << pacchRTS[i] << "\n" << endl;

                            }
                            //cout << "Value of paccTXtot[" << elenco[i].ns << "] = " << pacchTXtot[i] << "\n" << endl;
                        }
                        else {                                                   //channel busy

                            pBusy[i]++;
                            pChannel[i]++;
                            elenco[i].state = 6;                                //go to wait
                            elenco[i].time = elenco[i].time + Twait;

                            //cout << "Node " << elenco[i].ns << " senses channel BUSY and goes to WAIT until t= " << elenco[i].time << " (attempt " << elenco[i].numtx << " )\n" << endl;

                        }

                        break;
                    }

                    case 3:  //out
                    {
                        elenco[i].sense2 = Sensing2(elenco, vectState, N, fout1);  //sensing of the channel

                        if (elenco[i].sense2 == 0 && sensed_channel[i] == false) { //channel is free and also in the previous slots was free

                            elenco[i].numtx++;                                     //increase node attempt

                            if (elenco[i].numtx <= rmax + 1)                       //node can retransmit again
                            {

                                int p = pow(2, elenco[i].numtx);

                                delay = 1 + (rand() % (p * W));

                                //cout << "Node " << elenco[i].ns << " has collided, goes to OUT (attempt " << elenco[i].numtx << " ); NEW delay: " << delay << "\n" << endl;

                                elenco[i].state = 2;                              //go to backoff
                                delayNode[i] = delay;
                                elenco[i].sense2 = 0;
                                elenco[i].time = elenco[i].time + delay * backoff;

                                //	cout << "Node " << elenco[i].ns << " has delay " << delay << ", goes from OUT to backoff, since channel is FREE, until t= " <<elenco[i].time <<" (attempt " << elenco[i].numtx << " )\n" << endl;

                            }

                            else            //maximum number of retransmissions reached
                            {

                                elenco[i].state = 0;       //the node enters in idle for 1 slot
                                elenco[i].colliso = 0;
                                elenco[i].sense2 = 0;
                                elenco[i].time = elenco[i].time + Tslot;

                                elenco[i].token = 1;
                                elenco[i].numtx = 0;
                                pFree[i]++;
                                pChannel[i]++;
                                //cout << "Node " << elenco[i].ns << " has finished retransmissions, goes back to idle until t= "<< elenco[i].time<<" (attempt " << elenco[i].numtx << " )\n" << endl;
                                //cout << "pacchFailure[" << elenco[i].ns << "] = " << pacchNWODATA[i] << "\n" << endl;
                            }
                        }
                        else if (elenco[i].sense2 == 1){     //channel sensed busy at the end of out

                            elenco[i].state = 3;             //go back to out
                            elenco[i].sense2 = 0;
                            sensed_channel[i] = false;
                            elenco[i].time = elenco[i].time + Tout;
                            pBusy[i]++;
                            pChannel[i]++;
                            //	cout << "Node " << elenco[i].ns << " is in OUT, channel is BUSY, remains in OUT until t= " << elenco[i].time << "\n" << endl;

                        }

                        else if (sensed_channel[i] == true && elenco[i].sense2 == 0) {   //channel is free but in the previous slots was busy

                            elenco[i].state = 3;              //remains in out
                            elenco[i].sense2 = 0;
                            sensed_channel[i] = false;
                            elenco[i].time = elenco[i].time + (elenco[i].ctstime*Tslot);
                            pFree[i]++;
                            pChannel[i]++;
                            //	cout << "Node " << elenco[i].ns << " is in OUT, channel is BUSY since before, remains in OUT until t= " << elenco[i].time << "\n" << endl;
                        }
                        break;
                    }

                    case 4: //RX-CTS
                    {
                        elenco[i].state = 5; //go to transmission of data and reception of ack from the node
                        elenco[i].time = elenco[i].time+elenco[i].tx;
                        elenco[i].colliso = 0;
                        //	cout << "Node " << elenco[i].ns << " has received CTS and tx data until t= " << elenco[i].time << " (attempt " << elenco[i].numtx << " )\n" << endl;

                        break;
                    }

                    case 5://TX-DATA e ACK
                    {

                        elenco[i].state = 0; //back to idle

                        elenco[i].colliso = 0;
                        elenco[i].sense = 0;
                        elenco[i].token = 1;
                        elenco[i].time = elenco[i].time + Tack + Tslot; //transmission of ack and back to idle

                        elenco[i].numtx = 0;                            //node attempt returns to 0
                        //cout << "Node " << elenco[i].ns << " has tx data,receives ack and goes to idle until t= " << elenco[i].time << " (attempt " << elenco[i].numtx << " )\n" << endl;
                        //cout << "pacchSuccess[" << elenco[i].ns << "] = " << pacchNDATA[i] << "\n" << endl;
                        break;
                    }

                    case 6: //WAIT
                    {

                        int p = pow(2, elenco[i].numtx);
                        delay = rand() % ((p * W)+1);    //delay between 0 and W*2^(i)

                        if (delay == 0) {                //if delay is 0 we go directly to RTS transmission

                            elenco[i].state = 1;
                            elenco[i].time = elenco[i].time + Trts;
                            //cout << "Node " << elenco[i].ns << " goes from WAIT directly to TX-RTS; attempt: "<<elenco[i].numtx<<"\n" << endl;
                            elenco[i].colliso = 0;
                            elenco[i].token = 0;

                            pacchTXtot[i]++;

                            if (elenco[i].numtx == 1) { //first attempt of the node
                                pacchRTS[i]++;
                                //cout << "Value of paccRTS[" << elenco[i].ns << "] = " << pacchRTS[i] << "\n" << endl;
                            }

                            //cout << "Value of paccTXtot[" << elenco[i].ns << "] = " << pacchTXtot[i] << "\n" << endl;
                        }

                        else {
                            elenco[i].state = 2;   //back to backoff
                            elenco[i].sense = 0;
                            elenco[i].token = 0;

                            delayNode[i] = delay; // save delay in a vector for that specific node

                            elenco[i].time = elenco[i].time + delay * backoff;

                            //cout << "Node " << elenco[i].ns << " goes from WAIT to backoff until t = " << elenco[i].time << " and delay " << delay << " attempt: " << elenco[i].numtx << "\n" << endl;
                        }

                        break;

                    }

                } //chiudo lo switch
            } //chiude if


            else  //during backoff state or OUT state
            {
                switch (vectState[elenco[i].ns]){

                    case 2:  //backoff
                    {
                        elenco[i].sense = Sensing(elenco, vectState, N, fout1);
                        //	cout << "Node " << elenco[i].ns << " during backoff senses the channel at t= "<<t<<"\n" << endl;

                        if (elenco[i].sense == 0) {

                            for (int j = 1; j <= delayNode[i]; j++) {

                                if (t == elenco[i].time - (j * backoff)) {
                                    elenco[i].state = 2; //remain in backoff
                                    pFree[i]++;
                                    pChannel[i]++;

                                    //cout << "Node " << elenco[i].ns << " senses the channel FREE at t= "<<t<<" and continues backoff \n" << endl;
                                    //cout << "pFree for node " << elenco[i].ns << "= " << pFree[i] << "\n" << endl;
                                }
                            }
                        }

                        else {
                            for (int j = 1; j <= delayNode[i]; j++) {

                                if (t == elenco[i].time - (j * backoff)) { //t=end of a backoff slot

                                    elenco[i].state = 6;   //go to wait

                                    elenco[i].time = t + Twait;
                                    pBusy[i]++;
                                    pChannel[i]++;
                                    elenco[i].sense = 0;

                                    //cout << "Node " << elenco[i].ns << " senses the channel BUSY at t= "<<t<<" and goes to wait until t = " << elenco[i].time << "\n" << endl;
                                    //cout << "pBusy for node " << elenco[i].ns << "= " << pBusy[i] << "\n" << endl;
                                    break;
                                }
                            }
                        }
                        break;
                    }

                    case 3:  //out
                    {
                        elenco[i].sense2 = Sensing2(elenco, vectState, N, fout1);
                        //cout << "Node " << elenco[i].ns << " during OUT senses the channel at t= "<<t<<"\n" << endl;

                        if (elenco[i].sense2 == 1) {

                            for (int j = 1; j < (Tout/Tslot); j++) {

                                if (t == elenco[i].time - (j * Tslot)) {

                                    elenco[i].state = 3;   //go to out state for the remaining needed time

                                    elenco[i].ctstime = (Tout/Tslot)-j;
                                    elenco[i].sense2 = 0;
                                    sensed_channel[i] = true;
                                    pBusy[i]++;
                                    pChannel[i]++;
                                    //cout << "Node " << elenco[i].ns << " senses the channel BUSY at t= "<<t<<" and remains in OUT\n " << endl;
                                    //cout << "pBusy for node " << elenco[i].ns << "= " << pBusy[i] << "\n" << endl;
                                    //break;
                                }
                            }
                        }
                        else {
                            for (int j = 1; j < (Tout / Tslot); j++) {
                                if (t == elenco[i].time - (j * Tslot)) {
                                    pFree[i]++;
                                    pChannel[i]++;
                                }
                            }
                        }

                        break;
                    }

                } //chiude switch
            } //chiude else
        } //chiude for
    } //chiude for
    if (t >= Ttot ) {
        // cout << "TEMPO t= " << t << endl;
        for (int i = 0; i < N; i++) {
            if (elenco[i].state == 1) {
                pacchTXtot[i] = pacchTXtot[i] - 1;
                if (elenco[i].numtx == 1) {
                    pacchRTS[i] = pacchRTS[i] - 1;
                }

            }

        }

    }
} //chiude accesso



bool Colliso(sensore elenco[],int *vectState, int sorg, int N, FILE* fout1)
{	int i;
    bool collis=0;

    for (i = 0; i < N; i++)
    {

        if (elenco[i].ns != sorg)
        {
            /*if(vectState[i]==1 || vectState[i]==4 || vectState[i]==5){

            collis = 1;

        }*/
            if (vectState[i] == 1 || vectState[i] == 4) {

                collis = 1;

            }
        }
    }

    if (collis==0) //no collision
    {return 0;}
    else
    {	//fprintf(fout1,"Pacchetto non catturato\n");
        return 1;
    }
}

bool Sensing(sensore elenco[], int* vectState, int N, FILE* fout1)
{
    int i;
    bool sense = 0;

    for (i = 0; i < N; i++)
    {
        if (vectState[i] == 4)
        {
            sense = 1; //c'� un nodo che ha avuto successo a trasmettere l'RTS e si trova in 4.
            //cout << "Node " << sorg <<" sensed channel BUSY from node "<< elenco[i].ns << endl;
        }

    }

    if (sense == 0)
    {
        return 0;
    }
    else
    {
        return 1;
    }
}

bool Sensing2(sensore elenco[], int* vectState, int N, FILE* fout1)
{
    int i;
    bool sense2 = 0;

    for (i = 0; i < N; i++)
    {
        if (vectState[i] == 4)
        {
            sense2 = 1; //c'� un nodo che ha avuto successo a trasmettere l'RTS e si trova in 4.
            //cout << "Node " << sorg <<" sensed channel BUSY from node "<< elenco[i].ns << endl;
        }

    }

    if (sense2 == 0)
    {
        return 0;
    }
    else
    {
        return 1;
    }
}


/*-----------------generates a uniform RV between 0 and 1---------------*/
double uniforme(void)
{
    double z;
    z = ran2(&seed);
    return z;
}




/*-----------------estrae un numero random-----------------------*/
double ran2(long *idum)  //--------------------------------NON TOCCARE----------------------
/*Long period (> 2 . 10 18 ) random number generator of L'Ecuyer with Bays-Durham shu.e
and added safeguards. Returns a uniform random deviate between 0.0 and 1.0 (exclusive of
the endpoint values). Call with idum a negative integer to initialize; thereafter, do not alter
idum between successive deviates in a sequence. RNMX should approximate the largest oating
value that is less than 1.*/
{
    int j;
    long k;
    static long idum2=123456789;
    static long iy=0;
    static long iv[NTAB];
    double temp;

    if (*idum <= 0)
    {                     /*Initialize.*/
        if (-(*idum) < 1) *idum=1;        /*Be sure to prevent idum = 0.*/
        else *idum = -(*idum);
        idum2=(*idum);
        for (j=NTAB+7;j>=0;j--)
        {        /* Load the shu.e table (after 8 warm-ups).*/
            k=(*idum)/IQ1;
            *idum=IA1*(*idum-k*IQ1)-k*IR1;
            if (*idum < 0) *idum += IM1;
            if (j < NTAB) iv[j] = *idum;
        }
        iy=iv[0];
    }
    k=(*idum)/IQ1;                        /*Start here when not initializing.*/
    *idum=IA1*(*idum-k*IQ1)-k*IR1;        /*Compute idum=(IA1*idum) % IM1 without over ows by Schrage's method. */
    if (*idum < 0) *idum += IM1;
    k=idum2/IQ2;
    idum2=IA2*(idum2-k*IQ2)-k*IR2;       /*Compute idum2=(IA2*idum) % IM2 likewise.*/
    if (idum2 < 0) idum2 += IM2;
    j=iy/NDIV;                            /*Will be in the range 0..NTAB-1.*/
    iy=iv[j]-idum2;                        /*Here idum is shu.ed, idum and idum2 are combined to generate output. */
    iv[j] = *idum;
    if (iy < 1) iy += IMM1;
    if ((temp=AM*iy) > RNMX) return RNMX;    /*Because users don't expect endpoint values.*/
    else {return temp;}
}

/*----------------Generation of a Poisson RV----------------*/

int PoissonRandomNumber(double lambda, double area)
{
    //   Input, real LAMBDA, the average number of events per unit time.
    //   Input, real TIME, the amount of time to observe.
    //   Output, integer N, the number of Poisson events observed.

    int n = 0;
    double t = 0.0;
    double t1;
    double dt;
    while ( t < area )
    { dt = - log((long double)rand())/lambda;
        n = n + 1;
        t1=t;
        t = t + dt;
    }
    return n;
}

int IntCasuale(int min, int max)
{
    return rand() % (max - min + 1) + min;
}