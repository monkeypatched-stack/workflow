import asyncio
from concurrent.futures import ThreadPoolExecutor
import logging
import os
from kafka import KafkaConsumer
from dotenv import load_dotenv

from pyflink.common import WatermarkStrategy, Encoder, Types
from pyflink.datastream import StreamExecutionEnvironment, RuntimeExecutionMode
from pyflink.datastream.connectors.file_system import FileSource, StreamFormat, FileSink, OutputFileConfig, RollingPolicy

from src.helpers.helpers import fetch_entity_details

# Load environment variables
load_dotenv()

# Logging config
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Kafka configs
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC", "create_ontology_topic")
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
KAFKA_GROUP_ID = os.getenv("KAFKA_GROUP_ID", "create_ontology_group")


def process_text(text):
    async def run_fetch():
        loop = asyncio.get_event_loop()
        num_threads = os.cpu_count() or 10
        with ThreadPoolExecutor(max_workers=num_threads) as thread_pool:
            return await fetch_entity_details(text, thread_pool)
    return asyncio.run(run_fetch())

def process_data(kafka_data=None, input_file_path=None, output_file_path=None):
    execution_env = StreamExecutionEnvironment.get_execution_environment()
    execution_env.set_runtime_mode(RuntimeExecutionMode.BATCH)
    execution_env.set_parallelism(1)
    logger.info("Processing data from Kafka")
    if input_file_path:
        data_stream = execution_env.from_source(
            source=FileSource.for_record_stream_format(
                StreamFormat.text_line_format(), input_file_path)
                .process_static_file_set().build(),
            watermark_strategy=WatermarkStrategy.for_monotonous_timestamps(),
            source_name="file_source"
        )
    elif kafka_data:
        data_stream = execution_env.from_collection(kafka_data, type_info=Types.STRING())
    else:
        raise ValueError("Provide either input_file_path or kafka_data.")

    data_stream = data_stream.map(lambda text: process_text(text), output_type=Types.STRING())

    if output_file_path:
        data_stream.sink_to(
            FileSink.for_row_format(
                base_path=output_file_path,
                encoder=Encoder.simple_string_encoder()
            )
            .with_output_file_config(
                OutputFileConfig.builder()
                .with_part_prefix("prefix")
                .with_part_suffix(".ext")
                .build())
            .with_rolling_policy(RollingPolicy.default_rolling_policy())
            .build()
        )
    else:
        data_stream.print()

    execution_env.execute("Data Processing Job")


def consume_kafka_messages():
    consumer = KafkaConsumer(
        KAFKA_TOPIC,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        group_id=KAFKA_GROUP_ID,
        auto_offset_reset='earliest',
        enable_auto_commit=True
    )
    try:
        for message in consumer:
            message_text = message.value.decode('utf-8')
            logger.info(f"Received message: {message_text}")
            process_data(kafka_data=[message_text])
    except KeyboardInterrupt:
        logger.info("Kafka consumer interrupted by user.")
    finally:
        consumer.close()
        logger.info("Kafka consumer closed.")


if __name__ == "__main__":
    consume_kafka_messages()
