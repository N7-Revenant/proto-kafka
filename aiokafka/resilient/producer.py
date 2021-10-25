from aiokafka import AIOKafkaProducer, AIOKafkaClient
from aiokafka.cluster import BrokerMetadata
from time import time
import asyncio


KAFKA_RETRY_BACKOFF_TIMEOUT_MS = 750

MESSAGE_SENDING_INTERVAL_S = 1


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


async def work():
    producer = AIOKafkaProducer(bootstrap_servers='192.168.50.71:9092', retry_backoff_ms=KAFKA_RETRY_BACKOFF_TIMEOUT_MS)
    await producer.start()

    start_ts = time()
    print(f"[{int(time()-start_ts)}] Working!")
    message = "My message"
    while True:
        try:
            fut = None
            ready = await check_broker_readiness(client=producer.client)
            if ready:
                print(f"[{int(time() - start_ts)}] Sending '{message}'")
                fut = await producer.send("MyTopic", "My message".encode())
            else:
                print(f"[{int(time() - start_ts)}] Not sending '{message}': Producer is not ready!")

            await asyncio.sleep(MESSAGE_SENDING_INTERVAL_S)
            if fut is not None:
                print(f"[{int(time() - start_ts)}] Done:{fut.done()}")

        except Exception as exc:
            print(f"[{int(time()-start_ts)}] Error: {exc}")
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
