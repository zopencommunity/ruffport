#include <errno.h>

typedef unsigned int zos_clockid_t;
struct zos_timespec {
    long tv_sec;
    long tv_nsec;
};

/* z/OS compatibility shims for advisory clock APIs used by dependencies. */
int clock_getres(zos_clockid_t clock_id, struct zos_timespec *resolution) {
    (void)clock_id;
    if (resolution != 0) {
        resolution->tv_sec = 0;
        resolution->tv_nsec = 1000;
    }
    return 0;
}

int clock_settime(zos_clockid_t clock_id, const struct zos_timespec *value) {
    (void)clock_id;
    (void)value;
    errno = ENOSYS;
    return -1;
}
