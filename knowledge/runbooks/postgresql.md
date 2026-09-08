# PostgreSQL Runbook

## PostgreSQL connection refused

If the application cannot connect to PostgreSQL, check:

1. Whether PostgreSQL is running.
2. Whether the database host is reachable.
3. Whether port 5432 is accessible.
4. Whether the database credentials are correct.

## PostgreSQL slow queries

If PostgreSQL queries are taking too long, check:

- Query execution plans.
- Missing indexes.
- Database CPU usage.
- Number of active connections.