from typing import Any

import typer
from validio_sdk.config import ValidioConfig
from validio_sdk.graphql_client.input_types import ResourceFilter
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
    get_client_and_config,
    output_json,
    output_text,
)
from validio_cli.namespace import get_namespace

app = AsyncTyper(help="Validators monitor data from your Source")


@app.async_command(help="Get Validators")
async def get(
    config_dir: str = ConfigDir,
    output_format: OutputFormat = OutputFormatOption,
    namespace: str = Namespace,
    identifier: str = Identifier,
    source: str = typer.Option(
        None, help="List Validators for this Source (name or ID)"
    ),
    destination: str = typer.Option(
        None, help="List Validators for this Destination (name or ID)"
    ),
    window: str = typer.Option(
        None, help="List Validators for this Window (name or ID)"
    ),
    segmentation: str = typer.Option(
        None, help="List Validators for this Segmentation (name or ID)"
    ),
):
    vc, cfg = await get_client_and_config(config_dir)

    validators: list[Any] = []

    # TODO: UI-1957
    # We don't want to get all resources if identifier is not id.
    # TODO: Add support for namespace
    if identifier is not None and identifier.startswith("MTR_"):
        validators.append(await vc.get_validator(id=identifier))
    elif source is None or not source.startswith("SRC_"):
        for s in await vc.list_sources(
            filter=ResourceFilter(resourceNamespace=get_namespace(namespace, cfg))
        ):
            validators.extend(await vc.list_validators(s.id))
    else:
        validators = await vc.list_validators(
            id=source,
            filter=ResourceFilter(resourceNamespace=get_namespace(namespace, cfg)),
        )

    validators = [
        validator
        for validator in validators
        if validio_cli._resource_filter(validator, ["source_config", "source"], source)
        and validio_cli._resource_filter(validator, ["source_config", "window"], window)
        and validio_cli._resource_filter(
            validator, ["source_config", "segmentation"], segmentation
        )
        and validio_cli._resource_filter(validator, ["destination"], destination)
    ]
    validators = _single_resource_if_specified(validators, identifier)

    if output_format == OutputFormat.JSON:
        return output_json(validators)

    return output_text(
        validators,
        fields={
            "name": OutputSettings(attribute_name="resource_name"),
            "type": OutputSettings.trimmed_upper_snake("typename__", "Validator"),
            "age": OutputSettings(attribute_name="created_at"),
        },
    )


async def get_validator_id(
    vc: ValidioAPIClient, cfg: ValidioConfig, identifier: str, namespace: str
) -> str | None:
    """
    Ensure the identifier is a resource id.

    If it doesn't have the expected prefix, do a resource lookup by name.
    """
    identifier_type = "validator"
    prefix = "MTR_"

    if identifier is None:
        print(f"Missing {identifier_type} id or name")
        return None

    if identifier.startswith(prefix):
        return identifier

    resource = await vc.get_validator_by_resource_name(
        resource_name=identifier,
        resource_namespace=get_namespace(namespace, cfg),
    )

    if resource is None:
        print(f"No {identifier_type} with name or id {identifier} found")
        return None

    return resource.id


if __name__ == "__main__":
    app()
