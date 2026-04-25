#define _POSIX_C_SOURCE 199309L
#include <stdio.h>
#include <stdlib.h>
#include <time.h>

struct timespec start, end;


int main(int argc, char *argv[]) {
    // Check correct number of arguments
    if (argc != 3) {
        printf("Usage: %s <dimension> <0=row-major | 1=col-major>\n", argv[0]);
        return 1;
    }

    int dim = atoi(argv[1]);
    int mode = atoi(argv[2]);


    // Allocate memory for dim x dim matrix
    int **matrix = malloc(dim * sizeof(int *));
    if (matrix == NULL) {
        perror("Memory allocation failed");
        return 1;
    }

    for (int i = 0; i < dim; i++) {
        matrix[i] = malloc(dim * sizeof(int));
        if (matrix[i] == NULL) {
            perror("Memory allocation failed");
            return 1;
        }
    }

    
    clock_gettime(CLOCK_MONOTONIC, &start);
    /* ======= SECTION YOU WANT TO TIME ======= */

    if (mode == 0) {
        for (int i = 0; i < dim; i++) {
            for (int j = 0; j < dim; j++) {
                matrix[i][j] += 1;
            }
        }
    } else {
        for (int j = 0; j < dim; j++) {
            for (int i = 0; i < dim; i++) {
                matrix[i][j] += 1;
            }
        }
    }

    /* ========================================= */

    clock_gettime(CLOCK_MONOTONIC, &end);

    long seconds = end.tv_sec - start.tv_sec;
    long nanoseconds = end.tv_nsec - start.tv_nsec;
    long total_ns = seconds * 1000000000L + nanoseconds;

    printf("SECTION_TIME_NS=%ld\n", total_ns);

    // Row-major traversal
    if (mode == 0) {
        // Initialize matrix with sample values
        for (int i = 0; i < dim; i++) {
            for (int j = 0; j < dim; j++) {
                matrix[i][j] = 0;
            }
        }
    }
    // Column-major traversal
    else {
        for (int j = 0; j < dim; j++) {
            for (int i = 0; i < dim; i++) {
                matrix[i][j] = 0;
            }
        }
    }

    // Free allocated memory
    for (int i = 0; i < dim; i++) {
        free(matrix[i]);
    }
    free(matrix);

    return 0;
}