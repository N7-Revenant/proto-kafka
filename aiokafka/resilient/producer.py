from aiokafka import AIOKafkaProducer, AIOKafkaClient
from aiokafka.cluster import BrokerMetadata
from time import time
import asyncio


KAFKA_RETRY_BACKOFF_TIMEOUT_MS = 750

PRODUCER_START_RETRY_INTERVAL_S = 5
MESSAGE_SENDING_INTERVAL_S = 1

KAFKA_TOPIC_NAME = "MyTopic"
KAFKA_MESSAGE_TEXT = "My message"


async def check_broker_readiness(client: AIOKafkaClient, start_ts: float = time()) -> bool:
    ready = False

    brokers = client.cluster.brokers()
    print(f"[{int(time() - start_ts)}] Brokers: {brokers}")
    for broker in brokers:  # type: BrokerMetadata
        node_ready = await client.ready(node_id=broker.nodeId)
        print(f"[{int(time() - start_ts)}] Node {broker.nodeId} ready: {node_ready}")
        if node_ready:
            ready = True
            break

    return ready


async def send_messages(producer: AIOKafkaProducer):
    i = 0
    start_ts = time()
    print(f"[{int(time()-start_ts)}] Working!")
    while True:
        fut = None
        try:
            new_message = f"{KAFKA_MESSAGE_TEXT}_{i}"
            ready = await check_broker_readiness(client=producer.client, start_ts=start_ts)
            if ready:
                print(f"[{int(time() - start_ts)}] Sending '{new_message}'")
                fut = await producer.send(KAFKA_TOPIC_NAME, new_message.encode())
            else:
                print(f"[{int(time() - start_ts)}] Not sending '{new_message}': Producer is not ready!")

        except asyncio.CancelledError:
            break

        except Exception as exc:
            print(f"[{int(time()-start_ts)}] Error: {exc}")

        await asyncio.sleep(MESSAGE_SENDING_INTERVAL_S)
        if fut is not None:
            print(f"[{int(time() - start_ts)}] Done:{fut.done()}")

        i += 1


async def attempt_work(loop: asyncio.AbstractEventLoop):
    producer = AIOKafkaProducer(bootstrap_servers='192.168.50.71:9092',
                                retry_backoff_ms=KAFKA_RETRY_BACKOFF_TIMEOUT_MS)

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

    send_messages_task = loop.create_task(send_messages(producer=producer))
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
    task = loop.create_task((attempt_work(loop=loop)))
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        task.cancel()
    loop.stop()
    print("Producer finished!")


if __name__ == '__main__':
    main()
