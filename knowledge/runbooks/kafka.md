# Kafka Runbook

## Kafka consumer lag

If a Kafka consumer has high lag, check:

1. Whether the consumer is running.
2. Whether the consumer is processing messages slowly.
3. Whether there are too many messages in the topic.
4. Whether the number of consumer instances is sufficient.

## Kafka broker unavailable

If a Kafka broker is unavailable, check:

- Broker health.
- Network connectivity.
- Broker logs.
- Available disk space.