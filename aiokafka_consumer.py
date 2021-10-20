from aiokafka import AIOKafkaConsumer
import asyncio


async def work():
    consumer = AIOKafkaConsumer("MyTopic", bootstrap_servers='192.168.50.71:9092')
    await consumer.start()
    try:
        async for msg in consumer:
            print(
                "{}:{:d}:{:d}: key={} value={} timestamp_ms={}".format(
                    msg.topic, msg.partition, msg.offset, msg.key, msg.value,
                    msg.timestamp))
    finally:
        await consumer.stop()


def main():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(work())


if __name__ == '__main__':
    main()
