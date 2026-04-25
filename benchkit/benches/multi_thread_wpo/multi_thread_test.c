#include <pthread.h>
#include <stdint.h>
#include <stdio.h>

#ifndef THREAD_COUNT
#define THREAD_COUNT 4
#endif

#ifndef ITERS_PER_THREAD
#define ITERS_PER_THREAD 1000000L
#endif

// `volatile` keeps the read-modify-write visible in memory so the hardware
// cost of writing into adjacent array slots is real (see false-sharing demo).

static pthread_t threads[THREAD_COUNT];
static volatile long counters[THREAD_COUNT];

static void *increment_counter(void *arg) {
    int id = (int)(intptr_t)arg;
    for (long i = 0; i < ITERS_PER_THREAD; i++) {
        counters[id]++;
    }
    printf("thread %d: counters[%d] = %ld\n", id, id, counters[id]);
    return NULL;
}

int main(void) {
    for (int i = 0; i < THREAD_COUNT; i++) {
        pthread_create(&threads[i], NULL, increment_counter, (void *)(intptr_t)i);
    }

    for (int i = 0; i < THREAD_COUNT; i++) {
        pthread_join(threads[i], NULL);
    }

    long total = 0;
    for (int i = 0; i < THREAD_COUNT; i++) total += counters[i];
    
    printf("---\n");
    printf("threads = %d\n", THREAD_COUNT);
    printf("iters/thr= %ld\n", (long)ITERS_PER_THREAD);
    printf("sum = %ld\n", total);
    printf("expected = %ld\n", (long)THREAD_COUNT * (long)ITERS_PER_THREAD);
    return 0;
}