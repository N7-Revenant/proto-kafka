from kafka import KafkaProducer
from kafka.producer.future import RecordMetadata

import asyncio


async def work():
    def on_send_success(record_metadata: RecordMetadata):
        print(f"Successfully sent message to topic: {record_metadata.topic}!")

    def on_send_error(e: Exception):
        print(f"Error: {type(e)}:{e}")

    producer = KafkaProducer(bootstrap_servers=['192.168.50.71:19092',
                                                '192.168.50.71:29092',
                                                '192.168.50.71:39092'])
    message = "My message"
    print("Working!")

    while True:
        producer.send("MyTopic", message.encode()).add_callback(on_send_success).add_errback(on_send_error)
        try:
            await asyncio.sleep(1)

        except asyncio.CancelledError:
            break

        except Exception as exc:
            print(f"Unexpected Error: {exc}")
            break

    producer.flush(timeout=3)
    producer.close()


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
