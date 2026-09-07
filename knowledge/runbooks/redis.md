# Redis Runbook

## Redis connection timeout

If the application reports Redis connection timeouts, check:

1. Whether Redis is running.
2. Whether the Redis host is reachable.
3. Whether port 6379 is accessible.
4. Whether the application connection pool is exhausted.

## Redis memory

If Redis is using excessive memory, check:

- Current memory usage.
- Eviction policy.
- Number of keys.
- Large values.