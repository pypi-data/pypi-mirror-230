import asyncio
from pathlib import Path

import httpx
import typer
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.shortcuts import confirm
from tabulate import tabulate
from validio_sdk.config import (
    Config,
    ConfigInvalidError,
    ConfigNotFoundError,
    ValidioConfig,
)
from validio_sdk.validio_client import UnauthorizedError, ValidioAPIClient

import validio_cli
from validio_cli import (
    AsyncTyper,
    ConfigDir,
    OutputFormat,
    OutputFormatOption,
    output_json,
)

app = AsyncTyper(help="Configuration for the Validio CLI and SDK")


@app.command(help="Create or edit current credentials")
def init(config_dir: str = ConfigDir):
    config_path = Path(config_dir) if config_dir is not None else None

    cfg = Config(config_path)
    create_type = "updated" if cfg.config_path.is_file() else "created"

    current_config = cfg.read() if cfg.config_path.is_file() else None

    while True:
        current_config = _prompt_for_config(current_config)

        print()
        should_test_config = prompt(
            validio_cli._fixed_width("Test configuration? [Y/n]")
        ).strip()

        if should_test_config and should_test_config.lower() != "y":
            break

        failure_reason = _test_configuration(current_config)
        if failure_reason is None:
            break

        print(f"\n⛔️ Configuration test failed: {failure_reason}\n")
        print("Please correct the configuration\n")

    cfg.write(current_config)

    print(f"\n🎉 Configuration {create_type} successfully!")


@app.command(help="Set default namespace to target")
def ns(
    config_dir: str = ConfigDir,
    namespace: str = typer.Argument(
        "default",
        help="Set default namespace to target from CLI",
    ),
):
    set_default_namespace(namespace or "default", config_dir)


@app.command(help="List current configuration")
def get(
    config_dir: str = ConfigDir,
    output_format: OutputFormat = OutputFormatOption,
):
    config_path = Path(config_dir) if config_dir is not None else None

    cfg = Config(config_path)
    try:
        validio_config = cfg.read()
    except ConfigNotFoundError:
        if confirm("🚫 No configuration found - do you want to create one?"):
            return init(config_dir)

        raise typer.Exit(code=1)
    except ConfigInvalidError:
        if confirm(
            "🚨 Configuration found, but is not valid - do you want to delete it and"
            " create a new one?"
        ):
            cfg.remove()
            return init(config_dir)

        raise typer.Exit(code=1)

    def _highlight_if_missing(value: str) -> str:
        if not value:
            return "⚠️  \033[91m{}\033[0m".format("MISSING")

        return value

    settings = {
        "config_path": cfg.config_path,
        "default_namespace": validio_config.default_namespace,
        "endpoint": validio_config.endpoint,
        "access_key": validio_config.access_key,
        "access_secret": validio_config.access_secret,
    }

    if output_format == OutputFormat.JSON:
        return output_json(settings)

    table = [["KEY", "VALUE"]]

    for k, v in settings.items():
        table.append([k.capitalize().replace("_", " "), _highlight_if_missing(v)])

    print(tabulate(table, tablefmt="plain"))

    return None


def set_default_namespace(namespace: str, default_config_path: str | None = None):
    config_path = Path(default_config_path) if default_config_path is not None else None
    cfg = Config(config_path)

    validio_config = cfg.read()
    validio_config.default_namespace = namespace

    cfg.write(validio_config)

    print(f"Default namespace set to '{namespace}'")


def _prompt_for_config(current_config: ValidioConfig | None) -> ValidioConfig:
    if current_config is None:
        current_config = ValidioConfig()

    endpoint_completer = WordCompleter(["http://localhost:8889"])

    current_config.endpoint = prompt(
        validio_cli._fixed_width("Validio endpoint URI"),
        completer=endpoint_completer,
        default=current_config.endpoint,
    ).strip()

    current_config.access_key = prompt(
        validio_cli._fixed_width("API access key ID"), default=current_config.access_key
    ).strip()

    current_config.access_secret = prompt(
        validio_cli._fixed_width("API secret access key"),
        is_password=True,
        default=current_config._access_secret,
    ).strip()

    return current_config


def _test_configuration(config: ValidioConfig) -> str | None:
    vc = ValidioAPIClient(validio_config=config)

    try:
        # NOTE: Do we need an explicit ping command here?
        event_loop = asyncio.get_event_loop()
        event_loop.run_until_complete(vc.get_users())
    except UnauthorizedError:
        return "Unauthorized"
    except httpx.ConnectError:
        return "Failed to connect to server"

    return None
