## Flow to run the Application

### Kafka booting process
1. Zookeeper - `/usr/bin/zookeeper-server-start ./config/zookeeper.properties`
2. Kafka Server - `/usr/bin/kafka-server-start ./config/server.properties`

### Create a topic
Command to create a topic
`kafka-topics --create --zookeeper localhost:2181 --replication-factor 1 --partitions 1 --topic org.sf.crime.police.service.calls`

### Check topic created
Check if the topic is listed in result of below command
`kafka-topics --zookeeper localhost:2181 --list`

### Data into Kafka
1. Data insertion command
`python kafka_server.py`

2. Kafka Console Consumer to check if data is being pushed to Kafka topic
`kafka-console-consumer --bootstrap-server localhost:9092 --topic org.sf.crime.police.service.calls --from-beginning`

### Spark job submit
`spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.11:2.3.4 --master local[*] data_stream.py`

### Kafka Console Consumer Output


### Spark job result
1. Aggregated data result


2. Streaming and Static Data frames join result


### Questions
1. How did changing values on the SparkSession property parameters affect the throughput and latency of the data?

2. What were the 2-3 most efficient SparkSession property key/value pairs? Through testing multiple variations on values, how can you tell these were the most optimal?