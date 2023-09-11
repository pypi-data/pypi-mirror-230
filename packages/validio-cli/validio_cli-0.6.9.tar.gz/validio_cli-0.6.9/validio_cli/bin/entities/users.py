import typer

from validio_cli import (
    AsyncTyper,
    ConfigDir,
    Identifier,
    OutputFormat,
    OutputFormatOption,
    OutputSettings,
    _single_resource_if_specified,
    get_client_and_config,
    output_json,
    output_text,
)

app = AsyncTyper(help="Users in the Validio system")


@app.async_command(help="Get users")
async def get(
    config_dir: str = ConfigDir,
    output_format: OutputFormat = OutputFormatOption,
    identifier: str = Identifier,
):
    vc, _ = await get_client_and_config(config_dir)

    # TODO: Get a single resource by id/name to not have to list.
    users = await vc.get_users()
    users = [] if users is None else _single_resource_if_specified(users, identifier)

    if output_format == OutputFormat.JSON:
        return output_json(users)

    return output_text(
        users,
        fields={
            "name": OutputSettings(attribute_name="resource_name"),
            "role": None,
            "status": None,
            "identities": OutputSettings(reformat=lambda x: len(x)),
            "age": OutputSettings(attribute_name="created_at"),
        },
    )


if __name__ == "__main__":
    typer.run(app())
