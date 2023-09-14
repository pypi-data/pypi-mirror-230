import pkg_resources

from c8connector import C8Connector, ConfigProperty, ConfigAttributeType, Sample, Schema


class MySQLTargetConnector(C8Connector):
    """MySQLTargetConnector's C8Connector impl."""

    def name(self) -> str:
        """Returns the name of the connector."""
        return "MySQL"

    def package_name(self) -> str:
        """Returns the package name of the connector (i.e. PyPi package name)."""
        return "macrometa-target-mysql"

    def version(self) -> str:
        """Returns the version of the connector."""
        return pkg_resources.get_distribution("macrometa_target_mysql").version

    def type(self) -> str:
        """Returns the type of the connector."""
        return "target"

    def description(self) -> str:
        """Returns the description of the connector."""
        return "Send data into a MySQL table."

    def logo(self) -> str:
        """Returns the logo image for the connector."""
        return ""

    def validate(self, integration: dict) -> None:
        """Validate given configurations against the connector.
        If invalid, throw an exception with the cause.
        """
        pass

    def samples(self, integration: dict) -> list[Sample]:
        """Fetch sample data using the given configurations."""
        return []

    def schemas(self, integration: dict) -> list[Schema]:
        """Get supported schemas using the given configurations."""
        return []

    def reserved_keys(self) -> list[str]:
        """List of reserved keys for the connector."""
        return []

    def config(self) -> list[ConfigProperty]:
        """Get configuration parameters for the connector."""
        return [
            ConfigProperty(
                "host",
                "Host",
                ConfigAttributeType.STRING,
                True,
                False,
                description="MySQL host.",
                placeholder_value="mysql_host",
            ),
            ConfigProperty(
                "port",
                "Port",
                ConfigAttributeType.INT,
                True,
                False,
                description="MySQL port.",
                default_value="3306",
            ),
            ConfigProperty(
                "username",
                "Username",
                ConfigAttributeType.STRING,
                True,
                False,
                description="MySQL user.",
                placeholder_value="mysql",
            ),
            ConfigProperty(
                "password",
                "Password",
                ConfigAttributeType.PASSWORD,
                True,
                False,
                description="MySQL password.",
                placeholder_value="password",
            ),
            ConfigProperty(
                "database",
                "Database Name",
                ConfigAttributeType.STRING,
                True,
                True,
                description="MySQL database name.",
                placeholder_value="mysql_db",
            ),
            ConfigProperty(
                "target_table",
                "Target Table",
                ConfigAttributeType.STRING,
                True,
                True,
                description="Destination table name.",
                placeholder_value="mysql_table",
            ),
            ConfigProperty(
                "batch_flush_size",
                "Batch Size",
                ConfigAttributeType.INT,
                False,
                False,
                description="Maximum size of batch. Exceeding this will trigger a batch flush.",
                default_value="10000",
            ),
            ConfigProperty(
                "batch_flush_interval",
                "Batch Flush Interval (Seconds)",
                ConfigAttributeType.INT,
                False,
                False,
                description="Time between batch flush executions.",
                default_value="60",
            ),
            ConfigProperty(
                "hard_delete",
                "Hard Delete",
                ConfigAttributeType.BOOLEAN,
                False,
                False,
                description="When `hard_delete` option is true, then DELETE SQL commands will be performed "
                "in MySQL to delete rows in tables. It is achieved by continuously checking "
                "the `_SDC_DELETED_AT` metadata column sent by the data source. Due to deleting "
                "rows requires metadata columns, `hard_delete` option automatically enables the"
                " `add_metadata_columns` option as well. Calculation of Metrics such as `exported_bytes`,"
                "will include _SDC_ columns' byte count.",
                default_value="true",
            ),
            ConfigProperty(
                "add_metadata_columns",
                "Add Metadata Columns",
                ConfigAttributeType.BOOLEAN,
                False,
                False,
                description="Metadata columns add extra row level information about data ingestion, "
                "(i.e. when was the row read in source, when was inserted or deleted in "
                "mysql etc.) Metadata columns are created automatically by adding extra "
                "columns to the tables with a column prefix `_SDC_`. The column names are "
                "following the stitch naming conventions documented at "
                "https://www.stitchdata.com/docs/data-structure/integration-schemas#sdc-columns.",
                default_value="false",
            ),
            ConfigProperty(
                "ssl",
                "Use SSL",
                ConfigAttributeType.BOOLEAN,
                False,
                False,
                description="If set to `true` then use SSL for connecting with mysql. "
                "If the server does not accept SSL connections or the client certificate is not recognized "
                "then the connection will fail.",
                default_value="false",
            ),
            ConfigProperty(
                "ssl_check_hostname",
                "Check Hostname",
                ConfigAttributeType.BOOLEAN,
                False,
                False,
                description="Flag to configure whether ssl handshake should verify that the certificate "
                "matches the db hostname.",
                default_value="true",
            ),
            ConfigProperty(
                "ssl_root_ca_cert",
                "SSL CA Certificate",
                ConfigAttributeType.FILE,
                False,
                False,
                description="Specific CA certificate in PEM string format. This is most often the case "
                "when using `self-signed` server certificate.",
                placeholder_value="my_ca_certificate",
            ),
            ConfigProperty(
                "ssl_client_certificate",
                "SSL Client Certificate",
                ConfigAttributeType.FILE,
                False,
                False,
                description="Specific client certificate in PEM string format. The private key for client "
                "certificate should be specfied in a different parameter, SSL Client Key.",
                placeholder_value="my_client_certificate",
            ),
            ConfigProperty(
                "ssl_client_key",
                "SSL Client Key",
                ConfigAttributeType.FILE,
                False,
                False,
                description="Specific client key in PEM string format.",
                placeholder_value="my_client_key",
            ),
        ]

    def capabilities(self) -> list[str]:
        """Return the capabilities[1] of the connector."""
        return []
