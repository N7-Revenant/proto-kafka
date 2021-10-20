from aiokafka import AIOKafkaProducer
import asyncio


async def work():
    producer = AIOKafkaProducer(bootstrap_servers='192.168.50.71:9092')
    await producer.start()
    try:
        await producer.send_and_wait("MyTopic", "My message".encode())
    finally:
        await producer.stop()


def main():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(work())


if __name__ == '__main__':
    main()
