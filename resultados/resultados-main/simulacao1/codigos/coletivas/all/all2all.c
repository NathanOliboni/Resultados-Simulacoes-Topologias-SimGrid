#include <mpi.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define IT 100  // Iterações

int main(int argc, char *argv[]) {
    int rank, size;
    int i;
    int msg_size = 1024; // 1 KB por parceiro

    MPI_Init(&argc, &argv);
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &size);

    // Alocar apenas o necessário para MPI_Alltoall: msg_size * size
    size_t blk = (size_t)msg_size;
    size_t total = blk * (size_t)size;

    char *send_buffer = (char*) malloc(total);
    char *recv_buffer = (char*) malloc(total);

    if (!send_buffer || !recv_buffer) {
        if (rank == 0) {
            fprintf(stderr, "Falha de alocação: %zu bytes por buffer\n", total);
        }
        free(send_buffer);
        free(recv_buffer);
        MPI_Finalize();
        return 1;
    }

    // Conteúdo distinto por destino, limitado ao intervalo [A..Z]
    for (i = 0; i < size; i++) {
        memset(send_buffer + (size_t)i * blk, 'A' + (rank + i) % 26, blk);
    }

    // Execução do all-to-all
    for (i = 0; i < IT; i++) {
        MPI_Alltoall(send_buffer, msg_size, MPI_CHAR,
                     recv_buffer, msg_size, MPI_CHAR,
                     MPI_COMM_WORLD);
    }

    free(send_buffer);
    free(recv_buffer);
    MPI_Finalize();
    return 0;
}

