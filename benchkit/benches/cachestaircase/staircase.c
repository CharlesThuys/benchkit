#include <stdlib.h>

#define TOTAL_ACCESSES (64*1024*1024L)

int main(int argc, char *argv[]) {

    int array_bytes = atoi(argv[1]);
    int access_pattern = atoi(argv[2]);;

    long n = array_bytes / sizeof(double);
    long iters = TOTAL_ACCESSES / n;

    double *array = malloc(array_bytes);
    for (long i = 0; i < n; i++) array[i] = i;
    long *indices = malloc(n * sizeof(long));
    for (long i = 0; i < n; i++) indices[i] = i;

    int acc = 0;
    if (access_pattern == 0) {
        printf("Sequential access\n");
        // Sequential: spatial locality
        for (long rep = 0; rep < iters; rep++)
        for (long i = 0; i < n; i++) acc += array[i];
    } else {
        printf("Random access\n");
        // Random: shuffled indices
        // shuffle(indices, n); // Fisher-Yates

        //implementation of Fisher
        int i, j, tmp; // create local variables to hold values for shuffle

        for (i = n - 1; i > 0; i--) { // for loop to shuffle
            j = rand() % (i + 1); //randomise j for shuffle with Fisher Yates
            tmp = indices[j];
            indices[j] = indices[i];
            indices[i] = tmp;
        }
        
        for (long rep = 0; rep < iters; rep++)
        for (long i = 0; i < n; i++)
        acc += array[indices[i]];  
    }
}

