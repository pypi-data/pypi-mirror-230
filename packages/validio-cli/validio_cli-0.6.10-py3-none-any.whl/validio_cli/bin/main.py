import os
import sys

import httpx
import typer
import validio_sdk.metadata
from tabulate import tabulate
from validio_sdk.validio_client import UnauthorizedError

import validio_cli.metadata
from validio_cli.bin.entities import (
    channels,
    code,
    config,
    credentials,
    destinations,
    incidents,
    metrics,
    notification_rules,
    recommendations,
    resources,
    segmentations,
    segments,
    sources,
    users,
    validators,
    windows,
)

app = typer.Typer(
    help="Validio CLI tool", no_args_is_help=True, pretty_exceptions_enable=False
)

app.add_typer(channels.app, no_args_is_help=True, name="channels")
app.add_typer(code.app, no_args_is_help=True, name="code")
app.add_typer(config.app, no_args_is_help=True, name="config")
app.add_typer(credentials.app, no_args_is_help=True, name="credentials")
app.add_typer(destinations.app, no_args_is_help=True, name="destinations")
app.add_typer(incidents.app, no_args_is_help=True, name="incidents")
app.add_typer(metrics.app, no_args_is_help=True, name="metrics")
app.add_typer(resources.app, no_args_is_help=True, name="resources")
app.add_typer(notification_rules.app, no_args_is_help=True, name="notification-rules")
app.add_typer(recommendations.app, no_args_is_help=True, name="recommendations")
app.add_typer(segmentations.app, no_args_is_help=True, name="segmentations")
app.add_typer(segments.app, no_args_is_help=True, name="segments")
app.add_typer(sources.app, no_args_is_help=True, name="sources")
app.add_typer(users.app, no_args_is_help=True, name="users")
app.add_typer(validators.app, no_args_is_help=True, name="validators")
app.add_typer(windows.app, no_args_is_help=True, name="windows")


@app.command(help="Show current version")
def version():
    print(
        tabulate(
            [
                ["SDK version", validio_sdk.metadata.version()],
                ["CLI version", validio_cli.metadata.version()],
            ]
        )
    )


def main():
    exit_code = 1

    try:
        app()
        exit_code = 0

    except BrokenPipeError:
        # If the pipe is broken we can't print more so just return asap.
        return

    except UnauthorizedError:
        print("🛑 Unauthorized!")
        print(
            "Make sure you have proper credentials and run 'validio config' to add them"
        )

    except httpx.ConnectError as e:
        print(f"🛑 Failed to connect to server: {e}")
        print(
            "Check your network environment or run 'validio config' to set a proper"
            " server endpoint"
        )

    except Exception as e:
        print(f"Something went wrong: {e}")

        if os.getenv("VALIDIO_CLI_DEBUG") is not None:
            raise e

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
