# macrometa-target-mongo

`macrometa-target-mysql` is a Macrometa connector for writing data into MySQL, can be used as a target for any
Data Mesh Integration.

## Installation

Use PIP for installation:

```bash
pip install macrometa-target-mysql
```

## Configuration

The available configuration options for `macrometa-target-mysql` are:

| Property                            | Type              | Required?  | Description                                                                                         |
|-------------------------------------|-------------------|------------|-----------------------------------------------------------------------------------------------------|
| host                                | String            | Yes        | MySQL host                                                                                         |
| port                                | Int               | Yes        | MySQL port                                                                                         |
| username                            | String            | Yes        | MySQL user                                                                                         |
| password                            | Password          | Yes        | MySQL password                                                                                     |
| database                            | String            | Yes        | MySQL database name                                                                                |
| target_table                        | String            | Yes        | Destination table name                                                                             |
| batch_flush_size                    | Int               | No         | Maximum size of batch. Exceeding this will trigger a batch flush                                   |
| batch_flush_interval                | Int               | No         | Time between batch flush executions                                                                |
| hard_delete                         | Boolean           | No         | When `hard_delete` option is true, DELETE SQL commands will be performed in MySQL to delete rows   |
| add_metadata_columns                | Boolean           | No         | Metadata columns add extra row level information about data ingestion,                             |
|                                     |                   |            | (i.e. when was the row read in source, when was inserted or deleted in MySQL etc.) Metadata       |
|                                     |                   |            | columns are created automatically by adding extra columns to the tables with a column prefix `_SDC_`. |
|                                     |                   |            | The column names are following the stitch naming conventions documented at                         |
|                                     |                   |            | [link](https://www.stitchdata.com/docs/data-structure/integration-schemas#sdc-columns).              |
| ssl                                 | Boolean           | No         | If set to `true` then use SSL for connecting with MySQL.                                          |
|                                     |                   |            | If the server does not accept SSL connections or the client certificate is not recognized         |
|                                     |                   |            | then the connection will fail.                                                                     |
| ssl_check_hostname                 | Boolean           | No         | Flag to configure whether SSL handshake should verify that the certificate                        |
|                                     |                   |            | matches the DB hostname.                                                                           |
| ssl_root_ca_cert                   | File              | No         | Specific CA certificate in PEM string format. This is most often the case                         |
|                                     |                   |            | when using `self-signed` server certificate.                                                       |
| ssl_client_certificate             | File              | No         | Specific client certificate in PEM string format. The private key for the client                    |
|                                     |                   |            | certificate should be specified in a different parameter, SSL Client Key.                          |
| ssl_client_key                     | File              | No         | Specific client key in PEM string format.                                                          |

Configurations can be stored in a JSON configuration file and specified using the `--config` flag with
`macrometa-target-mysql`.

## Usage

```bash
cat <input_stream> | macrometa-target-mysql --config <config.json>
```

- `<input_stream>`: Input data stream
- `<config.json>`: JSON configuration file

`macrometa-target-mysql` reads data from a Singer Tap and writes it to a MySQL database. Run Singer Tap to generate
data before launching `macrometa-target-mysql`.

Here's an example of using Singer Tap with `macrometa-target-mysql`:

```bash
tap-exchangeratesapi | target-mysql --config config.json
```

In this case, `tap-exchangeratesapi` is a Singer Tap that generates exchange rate data. The data is passed to
`macrometa-target-mysql` through a pipe(`|`), and `macrometa-target-mysql` writes it to a MySQL database. `config.json` contains
`macrometa-target-mysql` settings.

## Developer Resources

### Initializing the Development Environment

```bash
pipx install poetry
poetry install
```

### Creating and Running Tests

Create tests in the `macrometa_target_mysql/tests` subfolder and run:

```bash
poetry run pytest
```

Use `poetry run` to test `macrometa-target-mysql` CLI interface:

```bash
poetry run target-mysql --help
```

### Testing with [Meltano](https://meltano.com/)

_**Note:** This target functions within a Singer environment and does not require Meltano._

Firstly, install Meltano and necessary plugins:

```bash
# Install Meltano
pipx install meltano

# Initialize Meltano in this directory
cd target-mysql
meltano install
```

Then, test and orchestrate with Meltano:

```bash
# Call tests:
meltano invoke macrometa-target-mysql --version

# Or execute pipeline with Carbon Intensity sample tap:
meltano run tap-carbon-intensity target-mysql
```

## Reference Links

- [Meltano Target SDK Documentation](https://sdk.meltano.com)
- [Singer Specification](https://github.com/singer-io/getting-started/blob/master/docs/SPEC.md)
- [Meltano](https://meltano.com/)
- [Singer.io](https://www.singer.io/)
