import asyncio
from concurrent.futures import ThreadPoolExecutor
import logging
import os
import threading

from kafka import KafkaConsumer
from pyflink.common import WatermarkStrategy, Encoder, Types
from pyflink.datastream import StreamExecutionEnvironment, RuntimeExecutionMode
from pyflink.datastream.connectors.file_system import FileSource, StreamFormat, FileSink, OutputFileConfig, RollingPolicy

from src.helpers.helpers import fetch_entity_details

logger = logging.getLogger(__name__)


# Set up Flink environment
execution_env = StreamExecutionEnvironment.get_execution_environment()
execution_env.set_runtime_mode(RuntimeExecutionMode.BATCH)
execution_env.set_parallelism(1)

def process_text(text):
    num_threads = os.cpu_count() or 10
    with ThreadPoolExecutor(max_workers=num_threads) as thread_pool:
        asyncio.run(fetch_entity_details(text, thread_pool))
    return text

# Define the process_data function
def process_data(input_file_path=None, output_file_path=None, kafka_data=None):
    # Define the source
    if input_file_path is not None:
        data_stream = execution_env.from_source(
            source=FileSource.for_record_stream_format(StreamFormat.text_line_format(), input_file_path)
                            .process_static_file_set().build(),
            watermark_strategy=WatermarkStrategy.for_monotonous_timestamps(),
            source_name="file_source"
        )
    elif kafka_data is not None:
        print("Executing process_data example with data consumed from Kafka consumer")
        data_stream = execution_env.from_collection(kafka_data, type_info=Types.STRING())
    else:
        raise ValueError("Either input_file_path or kafka_data must be provided.")

    # Transform
    data_stream = data_stream.map(lambda text: process_text(text), output_type=Types.STRING())

    # Sink
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
        print("Printing result to stdout. Use --output to specify output path.")
        data_stream.print()

    # Execute
    execution_env.execute("Kafka Data Processing Job")


# Kafka consumer setup
def consume_kafka_messages():
    consumer = KafkaConsumer(
        'create_ontology_topic',
        bootstrap_servers='localhost:9092',
        group_id='create_ontology_group',
        auto_offset_reset='earliest'
    )
    for message in consumer:
        kafka_data = [message.value.decode('utf-8')]
        print(f"Received message: {message.value.decode('utf-8')}")
        # process_data(kafka_data=kafka_data)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        consume_kafka_messages()
    except KeyboardInterrupt:
        print("Kafka consumer stopped.")

