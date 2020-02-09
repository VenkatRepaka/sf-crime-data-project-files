import producer_server


def run_kafka_server():
	# TODO get the json file path
    input_file = "./police-department-calls-for-service.json"

    # TODO fill in blanks
    # kafka-topics --create --zookeeper localhost:2181 --replication-factor 1 --partitions 1 --topic org.sf.crime.police.service.calls
    producer = producer_server.ProducerServer(
        input_file=input_file,
        topic="org.sf.crime.police.service.calls",
        bootstrap_servers="localhost:9092",
        client_id="com.udacity.sf.crime.police.service.calls.project-client"
    )

    return producer


def feed():
    producer = run_kafka_server()
    producer.generate_data()


if __name__ == "__main__":
    feed()
