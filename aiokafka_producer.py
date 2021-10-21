from aiokafka import AIOKafkaProducer
import asyncio


async def work():
    producer = AIOKafkaProducer(bootstrap_servers='192.168.50.71:9092')
    await producer.start()

    message = "My message"
    while True:
        try:
            print(f"Sending '{message}'")
            await producer.send("MyTopic", "My message".encode())
            await asyncio.sleep(1)
        except Exception as exc:
            print(f"Error: {exc}")
            break

    await producer.stop()


def main():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(work())


if __name__ == '__main__':
    main()
