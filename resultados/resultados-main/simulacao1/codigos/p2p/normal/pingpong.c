// smpicc -o pp PingPong.c
// smpirun -platform platform.xml -hostfile hostfile.txt -np 4 -trace -trace-file pp.trace --cfg=smpi/host-speed:1Gf ./pp --cfg=tracing/smpi/internals:yes

#include <mpi.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAX_SIZE 1048576	// 1MB 
#define MIN_SIZE 1      	// 1 byte 
#define IT 100	   		// Iterações


int main(int argc, char *argv[]) {
    int rank, size;
    char *buffer;
    int i, msg_size=1024;
    MPI_Status status;

    // Iniciando
    MPI_Init(&argc, &argv);
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &size);

    // Garante que haja pelo menos 2 processos para este teste
    if (size < 2) {
        if (rank == 0) {
            printf("Este teste requer pelo menos 2 processos MPI.\n");
        }
        MPI_Finalize();
        return 1;
    }

    buffer = (char*) malloc(MAX_SIZE);
    if (buffer == NULL) {
        printf("Error: Falha de memória na alocação do processo %d\n", rank);
        MPI_Finalize();
        return 1;
    }
    
    // Colocando dados
    memset(buffer, 'A' + rank, MAX_SIZE);
    
    // Sincronizando antes de começar
    // MPI_Barrier(MPI_COMM_WORLD);

    // Aqui começa de fato o teste
    // Ficou basicamente um Manager-Worker
    if (rank == 0) {
        for (i = 0; i < IT; i++) {
            // Itera sobre todos os outros processos ("Workers")
            for (int dest = 1; dest < size; dest++) {
                // Envia a mensagem para o processo de destino 
                MPI_Send(buffer, msg_size, MPI_CHAR, dest, 0, MPI_COMM_WORLD);
                // Recebe a resposta do mesmo processo
                MPI_Recv(buffer, msg_size, MPI_CHAR, dest, 0, MPI_COMM_WORLD, &status);
            }
        }
    } else {
        for (i = 0; i < IT; i++) {
            for (int source = 1; source < size; source++) {
                 // Apenas o processo atual se comunicará nesta iteração
                 if (rank == source) {
                    // Recebe a mensagem do processo 0
                    MPI_Recv(buffer, msg_size, MPI_CHAR, 0, 0, MPI_COMM_WORLD, &status);
                    // Envia a resposta de volta para o processo 0
                    MPI_Send(buffer, msg_size, MPI_CHAR, 0, 0, MPI_COMM_WORLD);
                 }
            }
        }
    }
    
    //Sincroniza todos os processos após o teste
    // MPI_Barrier(MPI_COMM_WORLD);

    free(buffer);
    MPI_Finalize();
    return 0;
}
