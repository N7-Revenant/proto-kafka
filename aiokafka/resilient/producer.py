from aiokafka import AIOKafkaProducer, AIOKafkaClient
from aiokafka.cluster import BrokerMetadata
from aiokafka.structs import RecordMetadata
import asyncio


KAFKA_RETRY_BACKOFF_TIMEOUT_MS = 750
KAFKA_REQUEST_TIMEOUT_MS = 5000

PRODUCER_START_RETRY_INTERVAL_S = 5
MESSAGE_SENDING_INTERVAL_S = 1

KAFKA_TOPIC_NAME = "MyTopic"
KAFKA_MESSAGE_TEXT = "My message"


async def check_result(index: int, message: str, send_future: asyncio.Future):
    try:
        result: RecordMetadata = await send_future
        print(f"[{index}] Message '{message}' successfully sent to topic {result.topic}!")

    except Exception as exc:
        print(f"[{index}] Message '{message}' won't be sent: {exc}!")


async def check_broker_readiness(client: AIOKafkaClient, index: int) -> bool:
    ready = False

    brokers = client.cluster.brokers()
    print(f"[{index}] Brokers: {brokers}")
    for broker in brokers:  # type: BrokerMetadata
        node_ready = await client.ready(node_id=broker.nodeId)
        print(f"[{index}] Node {broker.nodeId} ready: {node_ready}")
        if node_ready:
            ready = True
            break

    return ready


async def send_messages(producer: AIOKafkaProducer, loop: asyncio.AbstractEventLoop):
    index = 0
    print("Working!")
    while True:
        try:
            new_message = f"{KAFKA_MESSAGE_TEXT}_{index}"
            ready = await check_broker_readiness(client=producer.client, index=index)
            if ready:
                print(f"[{index}] Sending '{new_message}'")
                send_future = await producer.send(KAFKA_TOPIC_NAME, new_message.encode())
                loop.create_task(check_result(index=index, message=new_message, send_future=send_future))
            else:
                print(f"[{index}] Not sending '{new_message}': Producer is not ready!")
                break

        except asyncio.CancelledError:
            break

        except Exception as exc:
            print(f"[{index}] Error: {exc}")

        await asyncio.sleep(MESSAGE_SENDING_INTERVAL_S)
        index += 1


async def attempt_work(loop: asyncio.AbstractEventLoop):
    producer = AIOKafkaProducer(bootstrap_servers=['192.168.50.71:19092',
                                                   '192.168.50.72:29092',
                                                   '192.168.50.73:39092'],
                                retry_backoff_ms=KAFKA_RETRY_BACKOFF_TIMEOUT_MS,
                                request_timeout_ms=KAFKA_REQUEST_TIMEOUT_MS)

    initial = True
    started = False
    while not started:
        try:
            if not initial:
                await asyncio.sleep(PRODUCER_START_RETRY_INTERVAL_S)
            await producer.start()
            started = True

        except asyncio.CancelledError:
            break

        except Exception as exc:
            print(f"Unable to start producer: {exc}")
            print(f"Waiting {PRODUCER_START_RETRY_INTERVAL_S} seconds before next attempt...")
            initial = False

    send_messages_task = loop.create_task(send_messages(producer=producer, loop=loop))
    try:
        await send_messages_task

    except asyncio.CancelledError:
        send_messages_task.cancel()

    except Exception as exc:
        print(f"Unexpected error, search for cause: {exc}")

    await producer.stop()


def main():
    print("Producer started!")
    loop = asyncio.get_event_loop()
    while True:
        try:
            loop.run_until_complete(attempt_work(loop=loop))
        except KeyboardInterrupt:
            break
    print("Producer finished!")


if __name__ == '__main__':
    main()
