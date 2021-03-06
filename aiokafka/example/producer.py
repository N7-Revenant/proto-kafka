from aiokafka import AIOKafkaProducer
import asyncio


async def work():
    producer = AIOKafkaProducer(bootstrap_servers=['192.168.56.71:19092',
                                                   '192.168.56.71:29092',
                                                   '192.168.56.71:39092'])
    await producer.start()

    print("Working!")
    message = "My message"
    while True:
        try:
            print(f"Sending '{message}'")
            await producer.send("MyTopic", message.encode())
            await asyncio.sleep(1)
        except Exception as exc:
            print(f"Error: {exc}")
            break

    await producer.stop()


def main():
    print("Producer started!")
    loop = asyncio.get_event_loop()
    task = loop.create_task((work()))
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        task.cancel()
    loop.stop()
    print("Producer finished!")


if __name__ == '__main__':
    main()
