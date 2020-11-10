#include <iostream>


#define Tdata     20   //data packet duration in unit of time  //maggiore uguale 3
#define Tslot    2//Slot duration in unit of time - Tidle - Tbeacon

using namespace std;

typedef struct {
    int ns;//node ID
    unsigned long int time;
    unsigned long int startTransmissionTime;
    unsigned long int stopTransmissionTime;
    int state;
    bool colliso;
} sensore;

bool Colliso(sensore elenco[], int vectState[], int sorg, int N);

void accesso(sensore elenco[], int N);

void inizializza1(sensore elenco[], int N);

void inizializza2(sensore elenco[], int N);

void inizializza3(sensore elenco[], int N);

void inizializza4(sensore elenco[], int N);

int *vectState;

int main() {
    std::cout << "Hello, World!" << std::endl;

    sensore *elenco;//puntatore al tipo sensore per l'array di sensori
    elenco = (sensore *) malloc(2 * sizeof(sensore));//crea l'elenco di sensori

    vectState = new int[2];

    cout << endl << "Collision case 1: the first node start earlier" << endl;
    inizializza1(elenco, 2);
    accesso(elenco, 2);
    free(elenco);
    free(vectState);

    cout << endl << "Collision case 2: the second node start earlier" << endl;
    inizializza2(elenco, 2);
    accesso(elenco, 2);
    free(elenco);
    free(vectState);

    cout << endl << "Collision case 3: both nodes start at the same time" << endl;
    inizializza3(elenco, 2);
    accesso(elenco, 2);
    free(elenco);
    free(vectState);

    cout << endl << "Collision case 4: the second node starts immediately after the first node finished" << endl;
    inizializza4(elenco, 2);
    accesso(elenco, 2);
    free(elenco);
    free(vectState);

    return 0;
}

void accesso(sensore elenco[], int N) {
    for (int t = 0; t < 2 * Tdata + 1; t++) {
        for (int i = 0; i < N; i++) {

            if (t <= elenco[i].stopTransmissionTime && t >= elenco[i].startTransmissionTime) {
                elenco[i].state = 1;
            } else {
                elenco[i].state = 0;
            }

            vectState[i] = elenco[i].state;

            if (t == elenco[i].time) {
                elenco[i].time = elenco[i].stopTransmissionTime;
                if ( t != elenco[i].startTransmissionTime){
                    cout << "Node[" << i << "] finished transmission at time " << t << ", has collision: " << (elenco[i].colliso ? "true" : "false") << endl;
                    elenco[i].colliso = 0;
                }
            }
        }
        for (int i = 0; i < N; i++) {
            if (t != elenco[i].time) {
                if (elenco[i].state == 1) {
                    int has_collison = Colliso(elenco, vectState, elenco[i].ns, N);

                    if (elenco[i].colliso == 0) { // comment this for collision_approach_1
                        elenco[i].colliso = has_collison;
                    } // comment this for collision_approach_1
                }
            }
        }

        cout << "Time=" << t << " results: Node[0].collliso=" << (elenco[0].colliso ? "true" : "false") << ", Node[1].colliso=" << (elenco[1].colliso ? "true" : "false") << endl;
    }
}

void inizializza1(sensore elenco[], int N) {
    vectState[0] = 1;
    vectState[1] = 0;

    elenco[0].ns = 0;
    elenco[0].colliso = 0;
    elenco[0].time = 0;
    elenco[0].startTransmissionTime = 0;
    elenco[0].stopTransmissionTime = Tdata;
    elenco[0].state = 0;

    elenco[1].ns = 1;
    elenco[1].colliso = 0;
    elenco[1].time = 5 * Tslot;
    elenco[1].startTransmissionTime = 5 * Tslot;
    elenco[1].stopTransmissionTime = 5 * Tslot + Tdata;
    elenco[1].state = 0;

    cout << "Setup: Node[0] transmission = {" << elenco[0].startTransmissionTime << ", " << elenco[0].stopTransmissionTime << "}, Node[1] transmission = {" << elenco[1].startTransmissionTime << ", " << elenco[1].stopTransmissionTime << "}" << endl;

}

void inizializza2(sensore elenco[], int N) {
    vectState[0] = 0;
    vectState[1] = 1;

    elenco[0].ns = 0;
    elenco[0].colliso = 0;
    elenco[0].time = 5 * Tslot;
    elenco[0].startTransmissionTime = 5 * Tslot;
    elenco[0].stopTransmissionTime = 5 * Tslot + Tdata;
    elenco[0].state = 0;


    elenco[1].ns = 1;
    elenco[1].colliso = 0;
    elenco[1].time = 0;
    elenco[1].startTransmissionTime = 0;
    elenco[1].stopTransmissionTime = Tdata;
    elenco[1].state = 0;

    cout << "Setup: Node[0] transmission = {" << elenco[0].startTransmissionTime << ", " << elenco[0].stopTransmissionTime << "}, Node[1] transmission = {" << elenco[1].startTransmissionTime << ", " << elenco[1].stopTransmissionTime << "}" << endl;

}

void inizializza3(sensore elenco[], int N) {
    elenco[0].ns = 0;
    elenco[0].colliso = 0;
    elenco[0].time = 0;
    elenco[0].startTransmissionTime = 0;
    elenco[0].stopTransmissionTime = Tdata;
    elenco[0].state = 0;

    elenco[1].ns = 1;
    elenco[1].colliso = 0;
    elenco[1].time = 0;
    elenco[1].startTransmissionTime = 0;
    elenco[1].stopTransmissionTime = Tdata;
    elenco[1].state = 0;

    cout <<  "Setup: Node[0] transmission = {" << elenco[0].startTransmissionTime << ", " << elenco[0].stopTransmissionTime << "}, Node[1] transmission = {" << elenco[1].startTransmissionTime << ", " << elenco[1].stopTransmissionTime << "}" << endl;

}

void inizializza4(sensore elenco[], int N) {
    elenco[0].ns = 0;
    elenco[0].colliso = 0;
    elenco[0].time = 0;
    elenco[0].startTransmissionTime = 0;
    elenco[0].stopTransmissionTime = Tdata;
    elenco[0].state = 0;

    elenco[1].ns = 1;
    elenco[1].colliso = 0;
    elenco[1].time = Tdata;
    elenco[1].startTransmissionTime = Tdata;
    elenco[1].stopTransmissionTime = Tdata + Tdata;
    elenco[1].state = 0;

    cout << "Setup: Node[0] transmission = {" << elenco[0].startTransmissionTime << ", " << elenco[0].stopTransmissionTime << "}, Node[1] transmission = {" << elenco[1].startTransmissionTime << ", " << elenco[1].stopTransmissionTime << "}" << endl;

}

bool Colliso(sensore elenco[], int vectState[], int sorg, int N) {
    int i;
    bool collis = 0;

    for (i = 0; i < N; i++) {
        if (elenco[i].ns != sorg && vectState[i] == 1) {
            collis = 1;
        }
    }

    if (collis == 0) {
        return 0;
    } else {
        return 1;
    }
}