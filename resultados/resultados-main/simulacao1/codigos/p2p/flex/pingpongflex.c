// smpicc -o ppf PingPongFlex.c
// smpirun -platform platform.xml -hostfile hostfile.txt -np 12 -trace -trace-file ppf.trace --cfg=smpi/host-speed:1Gf ./ppf --cfg=tracing/smpi/internals:yes
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
    
    int master_rank;
    
    // Iniciando
    MPI_Init(&argc, &argv);
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &size);
    
    if (argc > 1) {
        master_rank = atoi(argv[1]);
    } else {
        master_rank = 0; // Padrão: rank 0
    }
    
    if (master_rank < 0 || master_rank >= size) {
        if (rank == 0) {
            printf("Erro: O rank do master (%d) é inválido. Deve estar entre 0 e %d.\n", master_rank, size - 1);
        }
        MPI_Finalize();
        return 1;
    }
    
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
    
    memset(buffer, 'A' + rank, MAX_SIZE);
    
    // Sincronizando antes de começar
//    MPI_Barrier(MPI_COMM_WORLD);
    // Aqui começa de fato o teste
    
    if (rank == master_rank) {
        for (i = 0; i < IT; i++) {
            // Itera sobre todos os processos para se comunicar
            for (int dest = 0; dest < size; dest++) {
                // Pula o envio para si mesmo
                if (dest == master_rank) {
                    continue;
                }
                // Envia a mensagem para o processo de destino
                MPI_Send(buffer, msg_size, MPI_CHAR, dest, 0, MPI_COMM_WORLD);
                // Recebe a resposta do mesmo processo
                MPI_Recv(buffer, msg_size, MPI_CHAR, dest, 0, MPI_COMM_WORLD, &status);
            }
        }
    } else {
        for (i = 0; i < IT; i++) {
            // Espera receber uma mensagem do processo Master
            MPI_Recv(buffer, msg_size, MPI_CHAR, master_rank, 0, MPI_COMM_WORLD, &status);
            // Envia a resposta de volta para o processo Master
            MPI_Send(buffer, msg_size, MPI_CHAR, master_rank, 0, MPI_COMM_WORLD);
        }
    }
    
    //Sincroniza todos os processos após o teste
    //MPI_Barrier(MPI_COMM_WORLD);
    free(buffer);
    MPI_Finalize();
    return 0;
}
