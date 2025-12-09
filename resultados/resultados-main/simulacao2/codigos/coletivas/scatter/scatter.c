#include <mpi.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAX_SIZE 1048576    // 1MB 
#define MIN_SIZE 1          // 1 byte 
#define IT 100                // Iterações

int main(int argc, char *argv[]) {
    int rank, size;
    char *send_buffer, *recv_buffer;
    int i, msg_size=1024;
    
    // Iniciando MPI
    MPI_Init(&argc, &argv);
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &size);
    
    // Alocando buffer de recepção para todos os processos
    recv_buffer = (char*) malloc(MAX_SIZE);
    if (recv_buffer == NULL) {
        printf("Error: Falha de memória na alocação do recv_buffer no processo %d\n", rank);
        MPI_Finalize();
        return 1;
    }
    
    // Processo root precisa do buffer de envio
    if (rank == 0) {
        send_buffer = (char*) malloc(MAX_SIZE * size);
        if (send_buffer == NULL) {
            printf("Error: Falha de memória na alocação do send_buffer no processo 0\n");
            free(recv_buffer);
            MPI_Finalize();
            return 1;
        }
        
        // Colocando dados diferentes para cada processo
        for (i = 0; i < size; i++) {
            memset(send_buffer + i * MAX_SIZE, 'A' + i, MAX_SIZE);
        }
    }
           
    // Sincronizando
    // MPI_Barrier(MPI_COMM_WORLD);
        
    // Aqui começa de fato o teste   
    for (i = 0; i < IT; i++) {
        MPI_Scatter(send_buffer, msg_size, MPI_CHAR,
                   recv_buffer, msg_size, MPI_CHAR,
                   0, MPI_COMM_WORLD);
    }
        
    // Sincroniza após teste
    // MPI_Barrier(MPI_COMM_WORLD);
        
    free(recv_buffer);
    if (rank == 0) free(send_buffer);
    MPI_Finalize();
    return 0;
}
