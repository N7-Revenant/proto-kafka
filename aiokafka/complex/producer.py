from aiokafka import AIOKafkaProducer
from aiokafka.cluster import BrokerMetadata
import asyncio

PRODUCER_START_RETRY_INTERVAL_S = 15


class KafkaProducerConnector:
    def __init__(self, bootstrap_servers: list, loop: asyncio.AbstractEventLoop):
        self.__loop = loop
        self.__producer_connector = AIOKafkaProducer(bootstrap_servers=bootstrap_servers)
        self.__worker_task = None
        self.__stopping_flag = asyncio.locks.Event()

    async def start(self):
        if self.__worker_task is None:
            if self.__stopping_flag.is_set():
                self.__stopping_flag.clear()
            self.__worker_task = self.__loop.create_task(self.__worker(shutdown_flag=self.__stopping_flag))

    async def stop(self):
        if self.__worker_task is not None:
            if not self.__stopping_flag.is_set():
                self.__stopping_flag.set()

            await self.__worker_task
            self.__worker_task = None

    async def __worker(self, shutdown_flag: asyncio.locks.Event):
        connect_required = True
        while not shutdown_flag.is_set():
            if connect_required:
                # Выполняем попытку подключения
                try:
                    print("Creating Kafka connection...")
                    await self.__producer_connector.start()
                except Exception as exc:
                    print(f"Unable to establish Kafka connection: {exc}!")
                else:
                    print("Successfully established Kafka connection!")
                    connect_required = False
            else:
                # Подключение не требуется, анализируем состояние имеющегося
                brokers_ready = await self.__check_broker_readiness()
                if not brokers_ready:
                    # Нет доступных брокеров, планируем переподключение
                    print("Closing Kafka Producer Connection...")
                    await self.__producer_connector.stop()
                    connect_required = True
                else:
                    print(f"Kafka brokers connected!")

            print(f"Checking again after {PRODUCER_START_RETRY_INTERVAL_S} seconds...")
            await asyncio.sleep(PRODUCER_START_RETRY_INTERVAL_S)

    async def __check_broker_readiness(self):
        ready = False

        brokers = self.__producer_connector.client.cluster.brokers()
        print(f"Brokers: {brokers}")
        if len(brokers) > 0:
            for broker in brokers:  # type: BrokerMetadata
                node_ready = await self.__producer_connector.client.ready(node_id=broker.nodeId)
                print(f"Node {broker.nodeId} ready: {node_ready}")
                if node_ready:
                    ready = True
        else:
            print("No brokers available!")

        return ready


async def work():
    loop = asyncio.get_running_loop()
    producer_connector = KafkaProducerConnector(
        bootstrap_servers=[
            '192.168.56.71:19092',
            '192.168.56.71:29092',
            '192.168.56.71:39092'],
        loop=loop)

    print("Working!")
    await producer_connector.start()
    while True:
        try:
            await asyncio.sleep(1)
        except asyncio.CancelledError:
            await producer_connector.stop()

        except Exception as exc:
            print(f"Error: {exc}")
            break


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
