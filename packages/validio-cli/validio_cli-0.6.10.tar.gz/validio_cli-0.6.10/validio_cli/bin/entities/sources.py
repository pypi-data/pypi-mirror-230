import asyncio
import json
import uuid
from pathlib import Path
from typing import Any

import click
import typer
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter
from validio_sdk.config import ValidioConfig
from validio_sdk.graphql_client.input_types import (
    AwsKinesisInferSchemaInput,
    AwsRedshiftInferSchemaInput,
    AwsS3InferSchemaInput,
    CsvParserInput,
    GcpBigQueryInferSchemaInput,
    GcpStorageInferSchemaInput,
    PostgreSqlInferSchemaInput,
    ResourceFilter,
    SnowflakeInferSchemaInput,
)
from validio_sdk.validio_client import ValidioAPIClient

import validio_cli
from validio_cli import (
    AsyncTyper,
    ConfigDir,
    Identifier,
    Namespace,
    OutputFormat,
    OutputFormatOption,
    OutputSettings,
    _single_resource_if_specified,
    components,
    get_client_and_config,
    output_json,
    output_text,
)
from validio_cli.bin.entities import credentials
from validio_cli.namespace import get_namespace

app = AsyncTyper(help="Data sources to ingest data from")

infer_schema_app = AsyncTyper(help="Infer schema")
app.add_typer(infer_schema_app, no_args_is_help=True, name="infer-schema")


def schema_filename_option(schema_type: str):
    return typer.Option(
        Path(Path.cwd(), f"{schema_type}_{uuid.uuid4()}.json"),
        "--filename",
        "-f",
        help="Filename including path for where to write inferred schema",
    )


@app.async_command(help="List all sources")
async def get(
    config_dir: str = ConfigDir,
    output_format: OutputFormat = OutputFormatOption,
    namespace: str = Namespace,
    identifier: str = Identifier,
    credential_id: str = typer.Option(None, help="List sources for this credential id"),
    credential_name: str = typer.Option(
        None, help="List sources for this credential name"
    ),
):
    vc, cfg = await get_client_and_config(config_dir)

    sources: list[Any] = []

    # TODO: UI-1957
    # We don't want to get all resources if identifier is not id.
    # TODO: Add support for namespace
    if identifier is not None and identifier.startswith("SRC_"):
        sources = [await vc.get_source(id=identifier)]
    else:
        sources = await vc.list_sources(
            filter=ResourceFilter(resourceNamespace=get_namespace(namespace, cfg))
        )

    sources = [
        source
        for source in sources
        if _resource_filter(source, credential_id, credential_name)
    ]
    sources = _single_resource_if_specified(sources, identifier)

    if output_format == OutputFormat.JSON:
        return output_json(sources)

    return output_text(
        sources,
        fields={
            "name": OutputSettings(attribute_name="resource_name"),
            "type": OutputSettings.trimmed_upper_snake("typename__", "Source"),
            "state": None,
            "age": OutputSettings(attribute_name="created_at"),
        },
    )


@app.async_command(help="Start source")
async def start(
    config_dir: str = ConfigDir,
    output_format: OutputFormat = OutputFormatOption,
    # ruff: noqa: ARG001
    namespace: str = Namespace,
    identifier: str = Identifier,
):
    vc, cfg = await get_client_and_config(config_dir)

    source_id = await get_source_id(vc, cfg, identifier, namespace)
    if source_id is None:
        return None

    # TODO: Add support for namespace
    result = await vc.start_source(id=source_id)

    if output_format == OutputFormat.JSON:
        return output_json(result)

    return print(result.state)


@app.async_command(help="Stop source")
async def stop(
    config_dir: str = ConfigDir,
    output_format: OutputFormat = OutputFormatOption,
    # ruff: noqa: ARG001
    namespace: str = Namespace,
    identifier: str = Identifier,
):
    vc, cfg = await get_client_and_config(config_dir)

    source_id = await get_source_id(vc, cfg, identifier, namespace)
    if source_id is None:
        return None

    # TODO: Add support for namespace
    result = await vc.stop_source(id=source_id)

    if output_format == OutputFormat.JSON:
        return output_json(result)

    return print(result.state)


@app.async_command(help="Backfill source")
async def backfill(
    config_dir: str = ConfigDir,
    output_format: OutputFormat = OutputFormatOption,
    # ruff: noqa: ARG001
    namespace: str = Namespace,
    identifier: str = Identifier,
):
    vc, cfg = await get_client_and_config(config_dir)

    source_id = await get_source_id(vc, cfg, identifier, namespace)
    if source_id is None:
        return None

    # TODO: Add support for namespace
    result = await vc.backfill_source(id=source_id)

    if output_format == OutputFormat.JSON:
        return output_json(result)

    return print(result.state)


@app.async_command(help="Reset source")
async def reset(
    config_dir: str = ConfigDir,
    output_format: OutputFormat = OutputFormatOption,
    # ruff: noqa: ARG001
    namespace: str = Namespace,
    identifier: str = Identifier,
):
    vc, cfg = await get_client_and_config(config_dir)

    source_id = await get_source_id(vc, cfg, identifier, namespace)
    if source_id is None:
        return None

    # TODO: Add support for namespace
    result = await vc.reset_source(id=source_id)

    if output_format == OutputFormat.JSON:
        return output_json(result)

    return print("Source has been successfully reset")


@infer_schema_app.callback(invoke_without_command=True)
def main(
    interactive: bool = typer.Option(
        False, "--interactive", "-i", help="Infer schema with an interactive prompt"
    ),
    config_dir: str = ConfigDir,
    filename: Path = schema_filename_option("schema"),
    namespace: str = Namespace,
) -> None:
    ctx = click.get_current_context()

    # A subcommand was run prior to this, nothing todo
    if ctx.invoked_subcommand is not None:
        return None

    # The interactive flag was used, run the interactive version
    if interactive:
        return asyncio.run(_interactive(config_dir, filename, namespace))

    # A flag for this command was used but not interactive, print the help as if
    # no command was given
    click.echo(ctx.get_help())

    return None


async def _interactive(config_dir: str, filename: Path, namespace: str):
    vc, cfg = await get_client_and_config(config_dir)

    credentials = await vc.list_credentials(
        filter=ResourceFilter(resourceNamespace=get_namespace(namespace, cfg))
    )

    if len(credentials) == 0:
        print(f"No credentials found in namespace {namespace}")
        raise typer.Exit(code=0)

    credential_name_to_id = [(c.id, c.name) for c in credentials]

    credential_id = await components.radiolist_dialog(
        title="Credentials to use",
        values=credential_name_to_id,
        navigation_help=True,
    )

    if credential_id is None:
        return

    credential_type = next(
        (c.typename__ for c in credentials if c.id == credential_id), None
    )
    if credential_type is None:
        return

    credential_type_to_source_type = {
        "AwsCredential": [
            ("kinesis", "Amazon Kinesis"),
            ("s3", "Amazon S3"),
        ],
        "DemoCredential": [("demo", "Demo")],
        "GcpCredential": [
            ("bigquery", "Google BigQuery"),
            ("gcs", "Google Cloud Storage"),
            ("pubsub", "Google Pub/Sub"),
            ("pubsub_lite", "Google Pub/Sub Lite"),
        ],
        "PostgreSqlCredential": [("postgresql", "PostgreSQL")],
        "RedshiftCredentiall": [("redshift", "Amazon Redshift")],
        "SnowflakeCredential": [("snowflake", "Snowflake")],
        "KafkaCredential": [("kafka", "Kafka")],
    }

    if credential_type not in credential_type_to_source_type:
        print(f"Unsupported credential type {credential_type} for inferring schema")
        return

    if len(credential_type_to_source_type[credential_type]) > 1:
        print()
        inference_type = await components.radiolist_dialog(
            title="Source type",
            values=credential_type_to_source_type[credential_type],
        )
    else:
        inference_type = credential_type_to_source_type[credential_type][0][0]

    if inference_type is None:
        return

    match inference_type:
        case "demo":
            await _infer_schema_demo(vc, filename)
        case "kinesis":
            info = await _multip_prompt(
                [
                    (
                        "Region",
                        # https://docs.aws.amazon.com/general/latest/gr/ak.html
                        [
                            "us-east-2",
                            "us-east-1",
                            "us-west-1",
                            "us-west-2",
                            "af-south-1",
                            "ap-east-1",
                            "ap-south-2",
                            "ap-southeast-3",
                            "ap-southeast-4",
                            "ap-south-1",
                            "ap-northeast-3",
                            "ap-northeast-2",
                            "ap-southeast-1",
                            "ap-southeast-2",
                            "ap-northeast-1",
                            "ca-central-1",
                            "eu-central-1",
                            "eu-west-1",
                            "eu-west-2",
                            "eu-south-1",
                            "eu-west-3",
                            "eu-south-2",
                            "eu-north-1",
                            "eu-central-2",
                            "me-south-1",
                            "me-central-1",
                            "sa-east-1",
                            "us-gov-east-1",
                            "us-gov-west-1",
                        ],
                        "",
                    ),
                    ("Stream name", [], ""),
                ]
            )
            await _infer_schema_kinesis(
                vc,
                filename,
                credential_id,
                info.get("region", ""),
                info.get("stream_name", ""),
            )
        case "s3":
            info = await _multip_prompt(
                [
                    ("Bucket", [], ""),
                    ("File pattern", [], "*.csv"),
                    ("Prefix", [], ""),
                    ("CSV delimiter", [",", "|"], ","),
                ]
            )

            print()
            null_marker = await _get_null_marker()

            await _infer_schema_s3(
                vc,
                filename,
                credential_id,
                info.get("bucket", ""),
                info.get("file_pattern", ""),
                info.get("prefix", ""),
                info.get("csv_delimiter", ""),
                null_marker,
            )
        case "postgresql":
            info = await _multip_prompt(
                [
                    ("Schema", [], ""),
                    ("Database", [], ""),
                    ("Table", [], ""),
                ]
            )
            await _infer_schema_postgresql(
                vc,
                filename,
                credential_id,
                info.get("schema", ""),
                info.get("database", ""),
                info.get("table", ""),
            )
        case "redshift":
            info = await _multip_prompt(
                [
                    ("Schema", [], ""),
                    ("Database", [], ""),
                    ("Table", [], ""),
                ]
            )
            await _infer_schema_redshift(
                vc,
                filename,
                credential_id,
                info.get("schema", ""),
                info.get("database", ""),
                info.get("table", ""),
            )
        case "snowflake":
            info = await _multip_prompt(
                [
                    ("Schema", [], ""),
                    ("Database", [], ""),
                    ("Table", [], ""),
                    ("Warehouse", [], ""),
                    ("Role", [], ""),
                ]
            )
            await _infer_schema_snowflake(
                vc,
                filename,
                credential_id,
                info.get("schema", ""),
                info.get("database", ""),
                info.get("table", ""),
                info.get("role", ""),
                info.get("warehouse", ""),
            )
        case "bigquery":
            info = await _multip_prompt(
                [
                    ("Project", [], ""),
                    ("Dataset", [], ""),
                    ("Table", [], ""),
                ]
            )
            await _infer_schema_bigquery(
                vc,
                filename,
                credential_id,
                info.get("project", ""),
                info.get("dataset", ""),
                info.get("table", ""),
            )
        case "gcs":
            info = await _multip_prompt(
                [
                    ("Project", [], ""),
                    ("Bucket", [], ""),
                    ("Folder", [], ""),
                    ("File pattern", ["*.csv"], "*.csv"),
                    ("CSV delimiter", [",", "|"], ","),
                ]
            )

            print()
            null_marker = await _get_null_marker()

            await _infer_schema_gcs(
                vc,
                filename,
                credential_id,
                info.get("project", ""),
                info.get("bucket", ""),
                info.get("folder", ""),
                info.get("file_pattern", ""),
                info.get("csv_delimiter", ""),
                null_marker,
            )
        case _:
            print("Not yet implemented...")
            return


@infer_schema_app.async_command(help="Infer Demo schema")
async def demo(
    config_dir: str = ConfigDir,
    filename: Path = schema_filename_option("demo"),
):
    vc, _ = await get_client_and_config(config_dir)
    await _infer_schema_demo(vc, filename)


@infer_schema_app.async_command(help="Infer Amazon S3 schema")
async def s3(
    config_dir: str = ConfigDir,
    filename: Path = schema_filename_option("s3"),
    namespace: str = Namespace,
    credential_id: str = typer.Option(..., help="Credential name or ID"),
    bucket: str = typer.Option(..., help="S3 bucket name"),
    file_pattern: str = typer.Option(
        "*.csv", help="File glob pattern - files to use for inference"
    ),
    prefix: str = typer.Option("", help="Prefix in the bucket, a directory"),
    csv_delimiter: str = typer.Option(",", help="Delimiter between columns in file"),
    null_marker: str = typer.Option(None, help="Null marker (values to treat as NULL)"),
):
    vc, cfg = await get_client_and_config(config_dir)

    resolved_credential_id = await credentials.get_credential_id(
        vc, cfg, credential_id, namespace
    )
    if resolved_credential_id is None:
        return

    await _infer_schema_s3(
        vc,
        filename,
        resolved_credential_id,
        bucket,
        file_pattern,
        prefix,
        csv_delimiter,
        null_marker,
    )


@infer_schema_app.async_command(help="Infer Amazon Kinesis schema")
async def kinesis(
    config_dir: str = ConfigDir,
    filename: Path = schema_filename_option("kinesis"),
    credential_id: str = typer.Option(..., help="Credential name or ID"),
    region: str = typer.Option(..., help="AWS region"),
    stream_name: str = typer.Option(..., help="AWS Kinesis stream name"),
    namespace: str = Namespace,
):
    vc, cfg = await get_client_and_config(config_dir)

    resolved_credential_id = await credentials.get_credential_id(
        vc, cfg, credential_id, namespace
    )
    if resolved_credential_id is None:
        return

    await _infer_schema_kinesis(
        vc, filename, resolved_credential_id, region, stream_name
    )


@infer_schema_app.async_command(help="Infer PostgreSQL schema")
async def postgresql(
    config_dir: str = ConfigDir,
    filename: Path = schema_filename_option("postgresql"),
    namespace: str = Namespace,
    credential_id: str = typer.Option(..., help="Credential name or ID"),
    schema: str = typer.Option(..., help="Schema name"),
    database: str = typer.Option(..., help="Database name"),
    table: str = typer.Option(..., help="Table name"),
):
    vc, cfg = await get_client_and_config(config_dir)

    resolved_credential_id = await credentials.get_credential_id(
        vc, cfg, credential_id, namespace
    )
    if resolved_credential_id is None:
        return

    await _infer_schema_postgresql(
        vc, filename, resolved_credential_id, schema, database, table
    )


@infer_schema_app.async_command(help="Infer Amazon Redshift schema")
async def redshift(
    config_dir: str = ConfigDir,
    filename: Path = schema_filename_option("redshift"),
    namespace: str = Namespace,
    credential_id: str = typer.Option(..., help="Credential name or ID"),
    schema: str = typer.Option(..., help="Schema name"),
    database: str = typer.Option(..., help="Database name"),
    table: str = typer.Option(..., help="Table name"),
):
    vc, cfg = await get_client_and_config(config_dir)

    resolved_credential_id = await credentials.get_credential_id(
        vc, cfg, credential_id, namespace
    )
    if resolved_credential_id is None:
        return

    await _infer_schema_redshift(
        vc, filename, resolved_credential_id, schema, database, table
    )


@infer_schema_app.async_command(help="Infer Snowflake schema")
async def snowflake(
    config_dir: str = ConfigDir,
    filename: Path = schema_filename_option("snowflake"),
    namespace: str = Namespace,
    credential_id: str = typer.Option(..., help="Credential name or ID"),
    schema: str = typer.Option(..., help="Schema name"),
    database: str = typer.Option(..., help="Database name"),
    table: str = typer.Option(..., help="Table name"),
    role: str = typer.Option(..., help="Role name"),
    warehouse: str = typer.Option(..., help="Warehouse name"),
):
    vc, cfg = await get_client_and_config(config_dir)

    resolved_credential_id = await credentials.get_credential_id(
        vc, cfg, credential_id, namespace
    )
    if resolved_credential_id is None:
        return

    await _infer_schema_snowflake(
        vc, filename, resolved_credential_id, schema, database, table, role, warehouse
    )


@infer_schema_app.async_command(help="Infer Google BigQuery schema")
async def bigquery(
    config_dir: str = ConfigDir,
    filename: Path = schema_filename_option("bigquery"),
    namespace: str = Namespace,
    credential_id: str = typer.Option(..., help="Credential name or ID"),
    project: str = typer.Option(..., help="Google project name"),
    dataset: str = typer.Option(..., help="Dataset name"),
    table: str = typer.Option(..., help="Table name"),
):
    vc, cfg = await get_client_and_config(config_dir)

    resolved_credential_id = await credentials.get_credential_id(
        vc, cfg, credential_id, namespace
    )
    if resolved_credential_id is None:
        return

    await _infer_schema_bigquery(
        vc, filename, resolved_credential_id, project, dataset, table
    )


@infer_schema_app.async_command(help="Infer Google Cloud Storage schema")
async def gcs(
    config_dir: str = ConfigDir,
    filename: Path = schema_filename_option("gcs"),
    namespace: str = Namespace,
    credential_id: str = typer.Option(..., help="Credential name or ID"),
    project: str = typer.Option(..., help="Google project name"),
    bucket: str = typer.Option(..., help="GCS bucket"),
    folder: str = typer.Option("", help="Folder in the bucket"),
    file_pattern: str = typer.Option("*.csv", help="File glob"),
    csv_delimiter: str = typer.Option(",", help="Delimiter between columns in file"),
    null_marker: str = typer.Option(None, help="Null marker (values to treat as NULL)"),
):
    vc, cfg = await get_client_and_config(config_dir)

    resolved_credential_id = await credentials.get_credential_id(
        vc, cfg, credential_id, namespace
    )
    if resolved_credential_id is None:
        return

    await _infer_schema_gcs(
        vc,
        filename,
        resolved_credential_id,
        project,
        bucket,
        folder,
        file_pattern,
        csv_delimiter,
        null_marker,
    )


async def _infer_schema_demo(
    vc: ValidioAPIClient,
    filename: Path,
):
    schema = await vc.infer_demo_schema()
    _write_schema(filename, schema)


async def _infer_schema_s3(
    vc: ValidioAPIClient,
    filename: Path,
    credential_id: str,
    bucket: str,
    file_pattern: str,
    prefix: str,
    csv_delimiter: str,
    null_marker: str | None,
):
    schema = await vc.infer_aws_s3_schema(
        AwsS3InferSchemaInput(
            credential_id=credential_id,
            bucket=bucket,
            filePattern=file_pattern,
            prefix=prefix,
            csv=CsvParserInput(
                delimiter=csv_delimiter,
                nullMarker=null_marker,
            ),
        )
    )
    _write_schema(filename, schema)


async def _infer_schema_kinesis(
    vc: ValidioAPIClient,
    filename: Path,
    credential_id: str,
    region: str,
    stream_name: str,
):
    schema = await vc.infer_aws_kinesis_schema(
        AwsKinesisInferSchemaInput(
            credential_id=credential_id,
            region=region,
            stream_name=stream_name,
        )
    )
    _write_schema(filename, schema)


async def _infer_schema_postgresql(
    vc: ValidioAPIClient,
    filename: Path,
    credential_id: str,
    db_schema: str,
    database: str,
    table: str,
):
    schema = await vc.infer_postgre_sql_schema(
        PostgreSqlInferSchemaInput(
            credential_id=credential_id,
            schema=db_schema,
            database=database,
            table=table,
        )
    )
    _write_schema(filename, schema)


async def _infer_schema_redshift(
    vc: ValidioAPIClient,
    filename: Path,
    credential_id: str,
    db_schema: str,
    database: str,
    table: str,
):
    schema = await vc.infer_aws_redshift_schema(
        AwsRedshiftInferSchemaInput(
            credential_id=credential_id,
            schema=db_schema,
            database=database,
            table=table,
        )
    )
    _write_schema(filename, schema)


async def _infer_schema_snowflake(
    vc: ValidioAPIClient,
    filename: Path,
    credential_id: str,
    db_schema: str,
    database: str,
    table: str,
    role: str,
    warehouse: str,
):
    schema = await vc.infer_snowflake_schema(
        SnowflakeInferSchemaInput(
            credential_id=credential_id,
            schema=db_schema,
            database=database,
            table=table,
            role=role,
            warehouse=warehouse,
        )
    )
    _write_schema(filename, schema)


async def _infer_schema_bigquery(
    vc: ValidioAPIClient,
    filename: Path,
    credential_id: str,
    project: str,
    dataset: str,
    table: str,
):
    schema = await vc.infer_gcp_big_query_schema(
        GcpBigQueryInferSchemaInput(
            credential_id=credential_id,
            project=project,
            dataset=dataset,
            table=table,
        )
    )
    _write_schema(filename, schema)


async def _infer_schema_gcs(
    vc: ValidioAPIClient,
    filename: Path,
    credential_id: str,
    project: str,
    bucket: str,
    folder: str,
    file_pattern: str,
    csv_delimiter: str,
    null_marker: str | None,
):
    schema = await vc.infer_gcp_storage_schema(
        GcpStorageInferSchemaInput(
            credential_id=credential_id,
            project=project,
            bucket=bucket,
            folder=folder,
            filePattern=file_pattern,
            csv=CsvParserInput(
                delimiter=csv_delimiter,
                nullMarker=null_marker,
            ),
        )
    )
    _write_schema(filename, schema)


def _write_schema(filename: Path, schema: Any):
    filename.write_text(json.dumps(schema, indent=2))

    print(f"Schema written to {filename}")


async def _multip_prompt(questions: list[tuple[str, list[str], str]]) -> dict[str, str]:
    answers = {}
    session: PromptSession = PromptSession()
    for f in questions:
        title, values, default = f
        answer_key = title.replace(" ", "_").lower()
        completer = WordCompleter(values)

        answers[answer_key] = await session.prompt_async(
            validio_cli._fixed_width(title),
            completer=completer,
            default=default,
            complete_in_thread=True,
        )

    return answers


async def _get_null_marker() -> str | None:
    null_marker = await components.radiolist_dialog(
        title="Null marker - What value should be treated as NULL",
        values=[
            ("none", "None (No value is treated as NULL)"),
            ("NULL", "The literal string 'NULL', f.ex. 'a,NULL,c'"),
            ("empty", "Empty (\"\", f.ex 'a,,c')"),
            ("other", "Set manually"),
        ],
    )

    # User hit escape sequence, don't return None in this case.
    if null_marker is None:
        raise typer.Exit(code=1)

    if null_marker == "other":
        session: PromptSession = PromptSession()
        null_marker = await session.prompt_async(
            validio_cli._fixed_width("Null marker"),
        )

    if null_marker == "none":
        return None

    # We can't map the value to '""' because it will make it pre-selected in the
    # dialog which we don't want.
    if null_marker == "empty":
        return ""

    return null_marker


async def get_source_id(
    vc: ValidioAPIClient, cfg: ValidioConfig, identifier: str, namespace: str
) -> str | None:
    """
    Ensure the identifier is a resource id.

    If it doesn't have the expected prefix, do a resource lookup by name.
    """
    identifier_type = "source"
    prefix = "SRC_"

    if identifier is None:
        print(f"Missing {identifier_type} id or name")
        return None

    if identifier.startswith(prefix):
        return identifier

    resource = await vc.get_source_by_resource_name(
        resource_name=identifier,
        resource_namespace=get_namespace(namespace, cfg),
    )

    if resource is None:
        print(f"No {identifier_type} with name or id {identifier} found")
        return None

    return resource.id


def _resource_filter(
    source: Any, credential_id: str | None, credential_name: str | None
) -> bool:
    if credential_id is not None and source.credential.id != credential_id:
        return False

    if (
        credential_name is not None
        and source.credential.resource_name != credential_name
    ):
        return False

    return True


if __name__ == "__main__":
    typer.run(app())
