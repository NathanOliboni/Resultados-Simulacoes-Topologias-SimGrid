#include <mpi.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAX_SIZE 1048576    // 1MB 
#define MIN_SIZE 1          // 1 byte 
#define IT 100               // Iterações

int main(int argc, char *argv[]) {
    int rank, size;
    char *buffer;
    int i, msg_size=1024;
    
    // Iniciando MPI
    MPI_Init(&argc, &argv);
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &size);
    
    // Alocando buffer
    buffer = (char*) malloc(MAX_SIZE);
    if (buffer == NULL) {
        printf("Error: Falha de memória na alocação do processo %d\n", rank);
        MPI_Finalize();
        return 1;
    }
    
    // Colocando dados
    memset(buffer, 'A' + rank, MAX_SIZE);
        
    // Sincronizando
    // MPI_Barrier(MPI_COMM_WORLD);
        
    // Aqui começa de fato o teste        
    for (i = 0; i < IT; i++) {
        MPI_Bcast(buffer, msg_size, MPI_CHAR, 0, MPI_COMM_WORLD);
    }
      
    // Sincroniza após teste
    // MPI_Barrier(MPI_COMM_WORLD);
    
    free(buffer);
    MPI_Finalize();
    return 0;
}
