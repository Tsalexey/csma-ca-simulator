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

#define TotScenario 100//number of scenarios to be simulated
#define TotPacch    100 //number of scenarios to be simulated
#define side        30     //side of the sqaure area where nodes are located (in meters) - not used
#define ray         15     // ray della circonferenza inscritta nel cerchio  - not used
#define W           12 //contention window size  //Nmax

#define Pt       0.001 //transmit power - not used
#define Node     10
#define du       1.13    //source - destionation distance in meters  - not used
#define data     30   //data packet duration in unit of time  //maggiore uguale 3
#define Tslot    3//Slot duration in unit of time - Tidle - Tbeacon
#define Tack     3    //Slot duration in unit of time
#define Tout     3   //Slot duration in unit of time
#define Trts     3
#define Tcts     3
//#define Twait    6
#define backoff  3    //backoff duration in unit of time
#define rmax     3   //max number of retransmissions   

/*---PHY Parameters----*/ // not used

#define alpha 100000 //capture threshold in dB
#define lamda 0.125 //lunghezza d'onda  

/*------Channel Parameters------*/ //not used

#define beta 3 //coefficiente di propagazione

/*----------------MAC Parameters-----------------*/
#define g    1   //probability of transmission of the node - pa  

/*---------------------struttura sensore-------------------*/
typedef struct {
                int ns;//node ID
               double x; //coordinate x of its position
			   double y; //coordinate y of its position
			   int token; //indicates if the node has data in the queue to be transmitted    
			   int numtx; //conta il numero di volte in cui un pacchetto è trasmesso
			   int delay; //variable used to compute delay 
			   unsigned long int time;//instant in which the node will change its status
               unsigned long int tx;  //transmission duration = data
		       bool colliso;//specifica se il pacchetto ha colliso
			   bool sense; //specifica se sento un CTS
               int state; //indica lo stato del nodo: 0 = idle; 1 = transmission; 2 = backoff; 3 = out; 4=rx_cts
			   double cycletime;
			   double rtstime;
			   double ctstime;
			   int ctsmessage;
               }sensore;

void inizializza(sensore elenco[], int N, FILE * fout1); 
void accesso(sensore elenco[], int N, FILE * fout1);
double uniforme();
int PoissonRandomNumber(double lambda, double area); //not used
double ran2(long *idum);

bool Colliso(sensore elenco[], int *vectState, int sorg, int N, FILE * fout1);

double Ttot; //total time to be simulated per scenario for the tarsnmission of numPacch

double *pacchTX; //vector containing the number of packets transmitted by each source;
double *pacchTXtot; //vector containing the total number of packets transmitted by each source (TX e RITX)
double *pacchRX; //vector containing the number of packets correctly transmitted by each source/received by the destinatio;
double *pacchColl; //vector containing the number of packets collided
double* pacchCollIgnored;
double *pacchCTS;
double *pacchRTS;
double *pSuccess;
double *pFailure;

double *numCycle;
int *vectState;
int* delayNode;

vector<double>* pacchCT; //vector containing the vector of cycle times
vector<double>* pacchRTST; //vector containing the vector of cycle times
vector<double>* pacchCTStime;
double* pacchNCYCLES; //vector containing the average number of cycles
double* pacchNDATA; //vector containing the average number of transmissions
double* pacchNWODATA; //vector containing the average number of failure

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


double mean(vector<double> array) {
	double sum = 0;
	for (int i = 0; i < array.size(); i++) {
		sum += array[i];
	}
	sum /= array.size();
	return sum;
}

/*--------------------------------------------MAIN---------------------------------------------------*/
int main()
{
 FILE *fout1;                                                               //   file 
 char file_out1[200];                                                       //    di
 sprintf(file_out1,"Output.txt");                                      //  output
 if ((fout1=fopen(file_out1,"wt"))==NULL) 
 {printf("\nErrore nell'apertura del file <%s>\n",file_out1);exit(1);}

 FILE *fout2;                                                               //   file 
 char file_out2[200];                                                       //    di
 sprintf(file_out2,"Results_N=%d.txt",Node);                                      //  output
 if ((fout2=fopen(file_out2,"wt"))==NULL) 
 {printf("\nErrore nell'apertura del file <%s>\n",file_out2);exit(2);}


 int i,j;
 int N; //numer of sensors deployed 
 int numScen;
 double area;
 
 //srand(time(NULL));

 area=side*side;
 Ttot=20000*Tslot;
//Ttot = 100*Tslot;

 fprintf(fout2, "Nodes;Average pS;Average pC;Average Etc time;Average DATA time;Percentage CTS;Average p{cycle success};Average p{cycle failure}\n");

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

	 // ------------------Beginning of each scenario --------------------------// 

	 for (int numScen = 1; numScen <= TotScenario; numScen++)  //consider 1000 scenarios 
	 {

		 //N = Node;
		 N = currentNodesNumber;
		 //fprintf(fout1,"Number of distributed nodes = %d\n",N);
		 pacchTX = new double[N];
		 pacchTXtot = new double[N];
		 pacchRX = new double[N];
		 pacchColl = new double[N];
		 pacchCollIgnored = new double[N];
		 pacchCTS = new double[N];
		 pacchRTS = new double[N];
		 pSuccess = new double[N];
		 pFailure = new double[N];

		 numCycle = new double[N];
		 vectState = new int[N];
		 delayNode= new int[N];

		 pacchCT = new vector<double>[N];
		 pacchRTST = new vector<double>[N];
		 pacchCTStime = new vector<double>[N];
		 pacchNCYCLES = new double[N];
		 pacchNDATA = new double[N];
		 pacchNWODATA = new double[N];

		 for (i = 0; i < N; i++)
		 {
			 pacchTX[i] = 0;
			 pacchTXtot[i] = 0;
			 pacchRX[i] = 0;
			 pacchColl[i] = 0;
			 pacchCollIgnored[i] = 0;
			 pacchCTS[i] = 0;
			 pacchRTS[i] = 0;
			 pSuccess[i] = 0;
			 pFailure[i] = 0;

			 numCycle[i] = 0;
			 vectState[i] = 0;
			 delayNode[i] = 0;

			 pacchCT[i] = {};
			 pacchRTST[i] = {};
			 pacchCTStime[i] = {};
			 pacchNCYCLES[i] = 0;
			 pacchNDATA[i] = 0;
			 pacchNWODATA[i] = 0;

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
		 averpCTSnode = 0;
		 averpCTScycle = 0;
		 avertcnode = 0;
		 averrtsnode = 0;
		 averpcnnode = 0;
		 averpfnnode = 0;

		 for (i = 0; i < N; i++)
		 {	
			 averpSnode = averpSnode + pacchCTS[i] / (pacchRTS[i]);
			 //averpCnode = averpCnode + pacchColl[i] / (pacchColl[i] + pacchCTS[i]);
			 averpCnode = averpCnode + pacchColl[i] / (pacchTXtot[i]);
			
			 avertcnode = avertcnode + mean(pacchCT[i]);
			 averrtsnode = averrtsnode + mean(pacchRTST[i]);
			 averpCTSnode = averpCTSnode + mean(pacchCTStime[i]);
			 averpcnnode = averpcnnode + pacchNDATA[i] / pacchNCYCLES[i];
			 averpfnnode = averpfnnode + pacchNWODATA[i] / pacchNCYCLES[i];

			 //fprintf(fout2, "Pacchetti TX tot; Pacchetti Collisi; RTS; CTS; IGNORED; n FREE; n BUSY; n CHANNEL SENSED\n");
			 //fprintf(fout2, "%f;%f;%f;%f;%f;%f;%f;%f\n", pacchTXtot[i], pacchColl[i], pacchRTS[i], pacchCTS[i], pacchCollIgnored[i], pFree[i],pBusy[i],pChannel[i]);
			 //fprintf(fout2, "Pacchetti TX tot; Pacchetti Collisi; CTS; IGNORED;\n");
			 //fprintf(fout2, "%f;%f;%f;%f\n", pacchTXtot[i], pacchColl[i], pacchCTS[i], pacchCollIgnored[i]);
		 }

		 averpS = averpS + averpSnode / ((double)(N));
		 averpC = averpC + averpCnode / ((double)(N));
		 
		 avertc = avertc + avertcnode / ((double)(N));
		 averpCTScycle = averpCTScycle + averpCTSnode / ((double)(N));
		 averpCTS = 1-(averpCTS + averpCTScycle / avertc);
		 averrts = averrts + averrtsnode / ((double)(N));
		 averpcn = averpcn + averpcnnode / ((double)(N));
		 averpfn = averpfn + averpfnnode / ((double)(N));

		 free(elenco);
		 free(pacchTX);
		 free(pacchRX);
		 free(pacchTXtot);
		 free(pacchColl);
		 free(pacchCollIgnored);
		 free(pacchCTS);
		 free(pacchRTS);
		 free(pSuccess);
		 free(pFailure);
		 free(vectState);
		 free(delayNode);
		 
		 free(pacchNDATA);
		 free(pacchNCYCLES);
		 free(pacchNWODATA);
		 cout << "Scenario " << numScen << " for " << currentNodesNumber << " nodes" << endl;

	 }

	 averpS = averpS / TotScenario;
	 averpC = averpC / TotScenario;
	 averpI = averpI / TotScenario;

	 averpF = averpF / TotScenario;
	 averpB = averpB / TotScenario;

	 avertc = avertc / TotScenario;
	 averrts = averrts / TotScenario;
	 averpcn = averpcn / TotScenario;
	 averpfn = averpfn / TotScenario;

	 //fprintf(fout2, "Average pS= %f\n", averpS);
	 //fprintf(fout2, "Average pC= %f\n", averpC);

	 fprintf(fout2, "%d;%f;%f;%f;%f;%f;%f;%f\n", currentNodesNumber, averpS, averpC,avertc, averrts,averpCTS, averpcn, averpfn);
	 
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
		elenco[i].numtx = 0;
		//if(elenco[i].ns==0){fprintf(fout1,"Num tx per nodo 0 = %d\n",elenco[i].numtx);}
		elenco[i].delay = 0;
		elenco[i].state=0; //the node enetres in idle till the next slot
		elenco[i].time=Tslot;
		elenco[i].cycletime = Tslot;
		elenco[i].rtstime = 0;
		elenco[i].ctstime = 0;
     }
}



/*----------------funzione che realizza l'accesso al canale da parte di CH tramite CSMA----------------*/
void accesso(sensore elenco[], int N, FILE *fout1)
{ int i;
int z = 0;
  int t = 0; //timer, simulates time passing 
  double prob; //to compute the probability that the node transmits

//  fprintf(fout1,"Inizio l'accesso \n");
  for (t=0; t<Ttot; t++)
  {	
	  for (i = 0; i < N; i++) //per ogni nodo valuto lo stato attuale e lo aggiorno 
	  {
		  vectState[i] = elenco[i].state;
		  //cout << "Node " << elenco[i].ns << " has vectState " << vectState[i] << "\n" << endl;
	  }
		for (i = 0; i < N; i++) //per ogni nodo valuto lo stato attuale e lo aggiorno 
		{
		  if (t==elenco[i].time)  //sto terminando l'operazione di Idle o TX o BO o out
	  	{	switch (elenco[i].state) //check the status
			{	case 0:  //Idle                                         
				{ // se il nodo deve ancora transmettere dei pacchetti   
					if (elenco[i].ns==0)
					{fprintf(fout1,"Il nodo 0 ha num tx = %d \n",elenco[i].numtx);}
					
					//cout << "Node " << elenco[i].ns << " is in IDLE: attempt " << elenco[i].numtx << "\n" << endl;
					//cout << "t= " << elenco[i].time << "\n" << endl;
					
					prob = uniforme();  //per pa
					
					if ((elenco[i].token==1)&&(prob<=g)) // se ha un pacchetto da trasmettere 
					{
						
						delay=rand()%(W);
						delayNode[i] = delay;
						elenco[i].numtx++; //increase node attempt
						
						if (delay==0) //il nodo tx subito l'RTS
						{   
							elenco[i].state=1; 
							elenco[i].colliso=0;
							elenco[i].token=0;
							elenco[i].time=elenco[i].time+Trts; //resto nello stato 1 per Trts
							
							elenco[i].cycletime = elenco[i].cycletime + Trts;
							elenco[i].rtstime = elenco[i].rtstime + Trts;

							pacchRTS[i]++;  //incremento numero RTS trasmessi
							pacchTXtot[i]++;
							
							//cout << "Node " << elenco[i].ns << " from IDLE goes directly to TX-RTS until t= " << elenco[i].time << " (attempt " << elenco[i].numtx << " )\n" << endl;

						}
						else //va in stato di backoff per delay poi TX RTS
						{	
						
						    elenco[i].state=2; 
							elenco[i].sense = 0;
							delayNode[i] = delay;

							elenco[i].time = elenco[i].time + delay*backoff;
							elenco[i].cycletime = elenco[i].cycletime + delay * backoff;
							
							//cout << "Node " << elenco[i].ns << " from IDLE goes to BACKOFF with delay " << delay << " until t= " << elenco[i].time << " (attempt: " << elenco[i].numtx << " )\n" << endl;
						}
					}
					else //resta in idle
					{	
						fprintf(fout1,"Il nodo %d attende uno slot per vedere se arriva un pacchetto\n",elenco[i].ns);
					    elenco[i].time=elenco[i].time+Tslot; 
						//cout << "t= " << elenco[i].time << "\n" << endl;
						elenco[i].cycletime = elenco[i].cycletime + Tslot;

					}
					break;
				}
  				
				case 1:  //TX RTS
				{	
					if (elenco[i].colliso == 0) { //check if there could be a collision at the end
						elenco[i].colliso = Colliso(elenco, vectState, elenco[i].ns, N, fout1);
					}

					if (elenco[i].colliso == 0) {
						
							elenco[i].state = 4; //the node enters in RX_CTS
							
							elenco[i].time = elenco[i].time + Tcts;
							elenco[i].cycletime = elenco[i].cycletime + Tcts;
							elenco[i].ctstime = elenco[i].ctstime + Tcts;
							pacchCTStime[i].push_back(elenco[i].ctstime);
							
							pacchCTS[i]++; //mando un CTS al nodo che ha avuto successo in RTS_TX

							//cout << "Node " << elenco[i].ns << " does not collide and enters in RX-CTS until t= " << elenco[i].time << "(attempt " << elenco[i].numtx << " )\n" << endl;
							//cout << "Value of paccCTS[" << elenco[i].ns << "] = " << pacchCTS[i] << "\n" << endl;

					}
					else {

						elenco[i].state = 3; //the node enters in Tout state  
						elenco[i].time = elenco[i].time + Tout;
						elenco[i].cycletime = elenco[i].cycletime + Tout;
						
						pacchColl[i]++; //RTS NOT IGNORED
						//cout << "Node " << elenco[i].ns << " collides and goes to OUT until t= " << elenco[i].time << " (attempt " << elenco[i].numtx << " )\n" << endl;
						//cout << "Value of paccColl[" << elenco[i].ns << "] = " << pacchColl[i] << "\n" << endl;
						
					}
					
				    break;
				}
						
				case 2:  //Backoff                                         
				{	
							
							elenco[i].state = 1;  //entra in trasmissione RTS
							
							elenco[i].colliso = 0;
							//elenco[i].sense = 0;
							elenco[i].token = 0;

							elenco[i].time = elenco[i].time + Trts;
							elenco[i].cycletime = elenco[i].cycletime + Trts;
							elenco[i].rtstime = elenco[i].rtstime + Trts;
							
							pacchTXtot[i]++; //accounts also for retransmissions
							
							//cout << "Node " << elenco[i].ns << " senses channel FREE and goes to TX-RTS until t= "<< elenco[i].time<<" (attempt " << elenco[i].numtx << " )\n" << endl;

							if (elenco[i].numtx == 1) //se è la prima trasmissione del pacchetto, incremento il numero di pacchetti trasmessi
							{
								pacchRTS[i]++;
								
							}
					
					break;
				}
				case 3:  //out
				{	
					elenco[i].numtx++;

				    if (elenco[i].numtx<=rmax+1) //il nodo può ancora ritrasmettere
					{	
						delay=rand()%((W*elenco[i].numtx));
						
						delayNode[i] = delay;

						//cout << "Node " << elenco[i].ns << " has collided, goes to OUT (attempt " << elenco[i].numtx << " ); NEW delay: " << delay << "\n" << endl;

						if (delay==0) //il nodo ritx subito il pacchetto
						{   
							
							elenco[i].state=1;
							elenco[i].colliso=0;
							elenco[i].token=0;
							elenco[i].time=elenco[i].time+Trts;
							elenco[i].cycletime = elenco[i].cycletime + Trts;
							elenco[i].rtstime = elenco[i].rtstime + Trts;
							pacchTXtot[i]++;
							//cout << "Node " << elenco[i].ns << " has delay 0, goes from OUT to TX-RTS until t= "<<elenco[i].time<<" (attempt " << elenco[i].numtx << " )\n" << endl;
						
						}

						else //va in stato di backoff per delay poi TX 
						{	
							if (elenco[i].ns==0){fprintf(fout1,"Il nodo %d entra in BO prima di ritrasmettere \n",elenco[i].ns);}
							
							elenco[i].state=2; 
							elenco[i].sense = 0;
						    elenco[i].time = elenco[i].time + delay*backoff;
							elenco[i].cycletime = elenco[i].cycletime + delay * backoff;
							
							//cout << "Node " << elenco[i].ns << " has delay " << delay << ", goes from OUT to backoff until t= " <<elenco[i].time <<" (attempt " << elenco[i].numtx << " )\n" << endl;
						}
					}

					else //il nodo ha esaurito le ritrasmissioni 
					{   
						
						if (elenco[i].ns==0){fprintf(fout1,"Il nodo %d non può più ritrasmettere  \n",elenco[i].ns);}
					    
						elenco[i].state=0; //the node enters in idle for 1 slot 
						elenco[i].colliso = 0;
						elenco[i].sense = 0;
						elenco[i].time=elenco[i].time+Tslot;
						elenco[i].cycletime = elenco[i].cycletime + Tslot;
						//pFailure[i]++; //il nodo ha fallito
						//numCycle[i]++; //termine del ciclo per il nodo
						
						pacchCT[i].push_back(elenco[i].cycletime);
						pacchRTST[i].push_back(elenco[i].rtstime);
						elenco[i].rtstime = 0;
						elenco[i].cycletime = 0;
						elenco[i].ctstime = 0;
						pacchNCYCLES[i]++;
						pacchNWODATA[i]++;

						elenco[i].token=1; 
						elenco[i].numtx=0;
						
						//cout << "Node " << elenco[i].ns << " has finished retransmissions, goes back to idle until t= "<< elenco[i].time<<" (attempt " << elenco[i].numtx << " )\n" << endl;
			    	}
					break;
				}

				case 4:
				{
					
					elenco[i].state = 5; //torno in idle
					
					elenco[i].time = elenco[i].time+elenco[i].tx;
					elenco[i].cycletime = elenco[i].cycletime + elenco[i].tx;
					
					//cout << "Node " << elenco[i].ns << " has received CTS and tx data until t= " << elenco[i].time << " (attempt " << elenco[i].numtx << " )\n" << endl;
					break;
				}
				case 5:
				{
					
					elenco[i].state = 0; //torno in idle
					
					elenco[i].colliso = 0;
					elenco[i].sense = 0;
					elenco[i].token = 1;
					elenco[i].time = elenco[i].time + Tack + Tslot;
					elenco[i].cycletime = elenco[i].cycletime + Tack + Tslot;
					//pSuccess[i]++; //il nodo ha avuto successo
					//pacchRX[i]++; //pacchetto ricevuto dal GW con successo
					//numCycle[i]++; // termine ciclo per il nodo
					
					pacchCT[i].push_back(elenco[i].cycletime); //insert element at the end
					pacchRTST[i].push_back(elenco[i].rtstime);
					elenco[i].rtstime = 0;
					elenco[i].cycletime = 0;
					elenco[i].ctstime = 0;
					pacchNDATA[i]++;
					pacchNCYCLES[i]++;

					elenco[i].numtx = 0;
					//cout << "Node " << elenco[i].ns << " has tx data,receives ack and goes to idle until t= " << elenco[i].time << " (attempt " << elenco[i].numtx << " )\n" << endl;
					break;
				}


			} //chiudo lo switch
		 } //chiude if
		 
		 
		else  //sto ancora svolgendo la mia operazione di Idle o di TX-RTS o BACKOFF
		{	switch (elenco[i].state)
			{	case 1:  //TX-RTS
				{	
					if (elenco[i].colliso == 0) {
						elenco[i].colliso = Colliso(elenco, vectState, elenco[i].ns, N, fout1);
					}
				
					break;
				}
			} //chiude switch
	    } //chiude else
    } //chiude for
  } //chiude for
  if (t >= Ttot) {
	  cout << "TEMPO t= " << t << endl;
	  for (int i = 0; i < N; i++) {
		  if (elenco[i].state == 1) {
			  pacchTXtot[i] = pacchTXtot[i] - 1;
		  }
	  }
	  
  }
} //chiude accesso



bool Colliso(sensore elenco[],int *vectState, int sorg, int N, FILE* fout1)
{	int i;
	bool collis=0;
	
	for (i = 0; i < N; i++)
	{
		if (elenco[i].ns != sorg && vectState[i] == 1) //it is node the source we are considering and it is transmitting 
		{

				collis = 1;

		}
	}

	if (collis==0) //il nodo non ha colliso
	{return 0;}
	else
	{	//fprintf(fout1,"Pacchetto non catturato\n"); 
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
