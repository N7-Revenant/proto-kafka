# proto-kafka

Kafka interaction prototype - Тестовое окружение для развертывания Kafka и набор прототипов, представляющих пример организации взаимодействия с Kafka из Python

 * aiokafka/complex/producer.py - AIOKafkaProducer из aiokafka, обернутый в класс-коннектор для удобства работы
 * aiokafka/example/producer.py - пример реализации Producer'а для Kafka с использованием библиотеки aiokafka
 * aiokafka/example/consumer.py - пример реализации Consumer'а для Kafka с использованием библиотеки aiokafka
 * aiokafka/resilient/producer.py - отказоустойчивый Kafka Producer для передачи некритичных данных на основе aiokafka
 * kafka-python/example/producer.py - пример реализации Producer'а для Kafka с использованием библиотеки kafka-python
