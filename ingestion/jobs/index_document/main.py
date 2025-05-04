import os
from dotenv import load_dotenv
import asyncio
import logging

from kafka import KafkaConsumer
from pyflink.common import WatermarkStrategy, Encoder, Types
from pyflink.datastream import StreamExecutionEnvironment, RuntimeExecutionMode
from pyflink.datastream.connectors.file_system import FileSource, StreamFormat, FileSink, OutputFileConfig, RollingPolicy
from src.helpers.helpers import send_index_document_event

# Load environment variables from .env file
load_dotenv()

# Set up Flink environment
execution_env = StreamExecutionEnvironment.get_execution_environment()
execution_env.set_runtime_mode(RuntimeExecutionMode.BATCH)
execution_env.set_parallelism(1)

# Kafka configs from environment
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC", "create_ontology_topic")
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "ingestion-kafka:9092")
KAFKA_GROUP_ID = os.getenv("KAFKA_GROUP_ID", "create_ontology_group")

def process_text(text):
    asyncio.run(send_index_document_event(text))
    return text

def process_data(input_file_path=None, output_file_path=None, kafka_data=None):
    if input_file_path is not None:
        data_stream = execution_env.from_source(
            source=FileSource.for_record_stream_format(StreamFormat.text_line_format(), input_file_path)
                            .process_static_file_set().build(),
            watermark_strategy=WatermarkStrategy.for_monotonous_timestamps(),
            source_name="file_source"
        )
    elif kafka_data is not None:
        print("Processing data from Kafka")
        data_stream = execution_env.from_collection(kafka_data, type_info=Types.STRING())
    else:
        raise ValueError("Either input_file_path or kafka_data must be provided.")

    data_stream = data_stream.map(lambda text: process_text(text), output_type=Types.STRING())

    if output_file_path is not None:
        data_stream.sink_to(
            sink=FileSink.for_row_format(
                base_path=output_file_path,
                encoder=Encoder.simple_string_encoder())
            .with_output_file_config(
                OutputFileConfig.builder()
                .with_part_prefix("prefix")
                .with_part_suffix(".ext")
                .build())
            .with_rolling_policy(RollingPolicy.default_rolling_policy())
            .build()
        )
    else:
        print("Printing result to stdout.")
        data_stream.print()

    execution_env.execute("Kafka Data Processing Job")

def consume_kafka_messages():
    consumer = KafkaConsumer(
        KAFKA_TOPIC,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        group_id=KAFKA_GROUP_ID,
        auto_offset_reset='earliest'
    )
    for message in consumer:
        kafka_data = [message.value.decode('utf-8')]
        print(f"Received message: {message.value.decode('utf-8')}")
        process_data(kafka_data=kafka_data)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        consume_kafka_messages()
    except KeyboardInterrupt:
        print("Kafka consumer stopped.")
