#include <mpi.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAX_SIZE 1048576    // 1MB 
#define MIN_SIZE 4          // 4 bytes (1 int)
#define IT 100             // Iterações

int main(int argc, char *argv[]) {
    int rank, size;
    int *send_buffer, *recv_buffer;
    int i, msg_size=1024, num_elements;
    
    // Iniciando MPI
    MPI_Init(&argc, &argv);
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &size);
    
    // Alocando buffers (usando int para operações de redução)
    send_buffer = (int*) malloc(MAX_SIZE);
    if (send_buffer == NULL) {
        printf("Error: Falha de memória na alocação do send_buffer no processo %d\n", rank);
        MPI_Finalize();
        return 1;
    }
    
    // Processo root precisa do buffer de recepção
    if (rank == 0) {
        recv_buffer = (int*) malloc(MAX_SIZE);
        if (recv_buffer == NULL) {
            printf("Error: Falha de memória na alocação do recv_buffer no processo 0\n");
            free(send_buffer);
            MPI_Finalize();
            return 1;
        }
    }
    
    // Colocando dados
    num_elements = MAX_SIZE / sizeof(int);
    for (i = 0; i < num_elements; i++) {
        send_buffer[i] = rank + 1;
    }
        
    // Calculando número de elementos para este tamanho
    int elements = msg_size / sizeof(int);
    if (elements == 0) elements = 1;
        
    // Sincronizando
    // MPI_Barrier(MPI_COMM_WORLD);
        
    // Aqui começa de fato o teste
        
    for (i = 0; i < IT; i++) {
        MPI_Reduce(send_buffer, recv_buffer, elements, MPI_INT, MPI_SUM, 0, MPI_COMM_WORLD);
    }
        
    // Sincroniza após teste
    // MPI_Barrier(MPI_COMM_WORLD);
    
    free(send_buffer);
    if (rank == 0) free(recv_buffer);
    MPI_Finalize();
    return 0;
}
