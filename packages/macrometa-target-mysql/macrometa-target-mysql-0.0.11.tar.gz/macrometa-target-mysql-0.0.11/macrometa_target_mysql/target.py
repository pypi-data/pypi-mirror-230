"""MySQL target class."""

from __future__ import annotations

import copy
import shutil
import threading
import time
from collections import Counter
from pathlib import PurePath
from threading import Lock
from typing import IO, Counter

import simplejson as json
from prometheus_client import start_http_server
from singer_sdk import typing as th
from singer_sdk.target_base import SQLTarget

from macrometa_target_mysql.constants import (
    export_errors,
    fabric_label,
    region_label,
    registry_package,
    tenant_label,
    workflow_label,
)
from macrometa_target_mysql.sinks import MySQLSink


class MacrometaTargetMySQL(SQLTarget):
    """Sample target for MySQL."""

    name = "macrometa-target-mysql"

    default_sink_class = MySQLSink
    flush_lock = Lock()

    def __init__(
        self,
        *,
        config: dict | PurePath | str | list[PurePath | str] | None = None,
        parse_env_config: bool = False,
        validate_config: bool = True,
    ) -> None:
        super().__init__(
            config=config,
            parse_env_config=parse_env_config,
            validate_config=validate_config,
        )

        # Start the Prometheus HTTP server for exposing metrics
        self.logger.info("MySQL target is starting the metrics server.")
        start_http_server(8001, registry=registry_package)

    config_jsonschema = th.PropertiesList(
        th.Property(
            "username",
            th.StringType,
            secret=True,  # Flag config as protected.
            description="MySQL username",
        ),
        th.Property(
            "password",
            th.StringType,
            secret=True,  # Flag config as protected.
            description="MySQL password",
        ),
        th.Property(
            "host",
            th.StringType,
            description="MySQL host",
        ),
        th.Property(
            "port",
            th.IntegerType,
            description="MySQL port",
        ),
        th.Property(
            "database",
            th.StringType,
            description="MySQL database",
        ),
        th.Property(
            "target_table",
            th.StringType,
            description="MySQL table name",
        ),
        th.Property(
            "batch_flush_interval",
            th.IntegerType,
            description="Batch Flush Interval (Seconds)",
            default=60,
        ),
        th.Property(
            "batch_flush_size", th.IntegerType, description="Batch Size", default=10000
        ),
        th.Property(
            "hard_delete",
            th.BooleanType,
            description="Hard Delete",
            default=True,
        ),
        th.Property(
            "add_metadata_columns",
            th.BooleanType,
            description="Add Metadata Columns",
            default=False,
        ),
        th.Property(
            "ssl",
            th.BooleanType,
            description="Use SSL",
            default=False,
        ),
        th.Property(
            "ssl_check_hostname",
            th.BooleanType,
            description="Check Hostname",
            default=True,
        ),
        th.Property(
            "ssl_root_ca_cert",
            th.StringType,
            description="SSL CA Certificate",
            default="",
        ),
        th.Property(
            "ssl_client_certificate",
            th.StringType,
            description="SSL Client Certificate",
            default="",
        ),
        th.Property(
            "ssl_client_key",
            th.StringType,
            description="SSL Client Key",
            default="",
        ),
    ).to_dict()

    schema_properties = {}

    def _process_lines(self, file_input: IO[str]) -> Counter[str]:
        counter: Counter[str] = None
        flusher = threading.Thread(
            target=self._flush_task, args=[self.config.get("batch_flush_interval")]
        )
        flusher.start()

        try:
            counter = super()._process_lines(file_input)
        except Exception as e:
            self._delete_certficate_files(self.config)
            # Increment export_errors metric
            export_errors.labels(
                region_label, tenant_label, fabric_label, workflow_label
            ).inc()
            raise e

        # Process any missed records before exiting
        with self.flush_lock:
            self.drain_all()

        self._delete_certficate_files(self.config)
        return counter

    def _process_record_message(self, message_dict: dict) -> None:
        """Process a RECORD message.

        Args:
            message_dict: TODO
        """
        self._assert_line_requires(message_dict, requires={"stream", "record"})

        stream_name = message_dict["stream"]
        self._assert_sink_exists(stream_name)

        for stream_map in self.mapper.stream_maps[stream_name]:
            raw_record = copy.copy(message_dict["record"])
            transformed_record = stream_map.transform(raw_record)
            if transformed_record is None:
                # Record was filtered out by the map transform
                continue

            sink = self.get_sink(stream_map.stream_alias, record=transformed_record)
            context = sink._get_context(transformed_record)
            if sink.include_sdc_metadata_properties:
                sink._add_sdc_metadata_to_record(
                    transformed_record,
                    message_dict,
                    context,
                )
            else:
                sink._remove_sdc_metadata_from_record(transformed_record)

            sink._validate_and_parse(transformed_record)
            transformed_record = sink.preprocess_record(transformed_record, context)
            sink._singer_validate_message(transformed_record)

            sink.tally_record_read()
            sink.process_record(transformed_record, context)
            sink._after_process_record(context)

            if sink.is_full:
                locked = self.flush_lock.acquire(False)
                if locked:
                    self.logger.info(
                        "Target sink for '%s' is full. Draining...",
                        sink.stream_name,
                    )
                    try:
                        self.drain_one(sink)
                    finally:
                        self.flush_lock.release()

    def _flush_task(self, interval) -> None:
        while True:
            time.sleep(interval)
            self.logger.debug(
                "Max age %ss reached for the batch. Draining all sinks.",
                interval,
            )
            with self.flush_lock:
                self.drain_all()

    def _handle_max_record_age(self) -> None:
        return

    def _delete_certficate_files(self, config: dict) -> None:
        try:
            cert = None
            if (
                config.get("ssl_root_ca_cert")
                or config.get("ssl_client_certificate")
                or config.get("ssl_client_key")
            ):
                shutil.rmtree(r"/opt/mysql/certs/", ignore_errors=True)
            if cert is not None:
                cert.parent.rmdir()
        except Exception as e:
            self.logger.warning(f"Failed to delete certificate: {e}")


if __name__ == "__main__":
    MacrometaTargetMySQL.cli()
