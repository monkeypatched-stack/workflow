import argparse
import asyncio
import json
import logging
import sys

from kafka import KafkaConsumer
from pyflink.common import WatermarkStrategy, Encoder, Types
from pyflink.datastream import StreamExecutionEnvironment, RuntimeExecutionMode
from pyflink.datastream.connectors.file_system import FileSource, StreamFormat, FileSink, OutputFileConfig, RollingPolicy
from src.helpers.helpers import send_index_document_event

# Set up Flink environment
execution_env = StreamExecutionEnvironment.get_execution_environment()
execution_env.set_runtime_mode(RuntimeExecutionMode.BATCH)
execution_env.set_parallelism(1)

def process_text(text):
    asyncio.run(send_index_document_event(text))
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
kafka_consumer = KafkaConsumer(
    'indexing_topic',
    bootstrap_servers='localhost:9092',
    auto_offset_reset='earliest',
    group_id='my-group'
)

# Consume messages and call process_data
for kafka_message in kafka_consumer:
    decoded_message = kafka_message.value.decode('utf-8')
    print(f"Received: {decoded_message}")
    kafka_data = [decoded_message]
    process_data(kafka_data=kafka_data)
