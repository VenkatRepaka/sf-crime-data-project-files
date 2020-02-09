{\rtf1\ansi\ansicpg1252\cocoartf1671\cocoasubrtf600
{\fonttbl\f0\fswiss\fcharset0 Helvetica;}
{\colortbl;\red255\green255\blue255;}
{\*\expandedcolortbl;;}
\paperw11900\paperh16840\margl1440\margr1440\vieww10800\viewh8400\viewkind0
\pard\tx566\tx1133\tx1700\tx2267\tx2834\tx3401\tx3968\tx4535\tx5102\tx5669\tx6236\tx6803\pardirnatural\partightenfactor0

\f0\fs24 \cf0 import asyncio\
\
from kafka import KafkaConsumer\
from confluent_kafka import Consumer, OFFSET_BEGINNING\
# from confluent_kafka.admin import AdminClient, NewTopic\
\
\
def consume_messages_by_kafka_consumer(topic_name):\
    consumer = KafkaConsumer(topic_name,\
                             group_id='com.udacity.sf.crime.police.service.calls.project-group-1',\
                             bootstrap_servers=["localhost:9092"],\
                             auto_offset_reset = 'earliest')\
    try:\
        for message in consumer:\
            print(f"Offset - \{message.offset\} #### Message Value - \{message.value\}")\
    except Exception as e:\
        print(e)\
    \
\
def consume_messages_by_consumer_subscription(topic_name):\
    consumer = Consumer(\{\
                        "bootstrap.servers":"PLAINTEXT://localhost:9092", \
                        "group.id": "com.udacity.sf.crime.police.service.calls.project-group-2",\
                        "auto.offset.reset": "earliest"\
                        \})\
    consumer.subscribe([topic_name], on_assign=on_assign)\
    while True:\
        messages = consumer.consume(10, timeout=0.5)\
        for message in messages:\
            if message is None:\
                print("No message")\
            elif message.error() is not None:\
                print(f"Error - \{message.error()\}")\
            else:\
                print(f"Offset - \{message.offset()\} #### Message Value - \{message.value()\}")\
\
\
def on_assign(consumer, partitions):\
    for partition in partitions:\
        partition.offset = OFFSET_BEGINNING\
    consumer.assign(partitions)\
    \
    \
def main():\
    try:\
        asyncio.run(consume_messages_by_kafka_consumer("org.sf.crime.police.service.calls"))\
        # asyncio.run(consume_messages_by_consumer_subscription("org.sf.crime.police.service.calls"))\
    except KeyboardInterrupt as e:\
        print("Ending consumer consumption")\
\
\
if __name__ == "__main__":\
    main()}