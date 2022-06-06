from aiokafka import AIOKafkaConsumer
import asyncio


async def work():
    consumer = AIOKafkaConsumer("MyTopic", bootstrap_servers=['192.168.56.71:19092',
                                                              '192.168.56.71:29092',
                                                              '192.168.56.71:39092'])
    await consumer.start()
    try:
        async for msg in consumer:
            print(
                "{}:{:d}:{:d}: key={} value={} timestamp_ms={}".format(
                    msg.topic, msg.partition, msg.offset, msg.key, msg.value,
                    msg.timestamp))

    except asyncio.CancelledError:
        pass

    finally:
        await consumer.stop()


def main():
    print("Consumer started!")
    loop = asyncio.get_event_loop()
    task = loop.create_task((work()))
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        task.cancel()
    loop.stop()
    print("Consumer finished!")


if __name__ == '__main__':
    main()
