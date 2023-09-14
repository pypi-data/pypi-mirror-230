from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any

import typer
from validio_sdk.graphql_client import (
    GetSegmentIncidentsSegmentIncidents,
    GetSourceIncidentsSourceIncidentsSegmentLimitExceededNotification,
    GetValidatorIncidentsValidatorIncidents,
    GetValidatorSegmentIncidentsValidatorSegmentIncidents,
)
from validio_sdk.graphql_client.input_types import (
    SegmentIncidentsInput,
    SourceIncidentsInput,
    TimeRangeInput,
    ValidatorIncidentsInput,
    ValidatorSegmentIncidentsInput,
)

from validio_cli import (
    AsyncTyper,
    ConfigDir,
    Namespace,
    OutputFormat,
    OutputFormatOption,
    OutputSettings,
    _format_relative_time,
    get_client_and_config,
    output_json,
    output_text,
)
from validio_cli.bin.entities import sources, validators

app = AsyncTyper(help="Incidents from validators")


@app.async_command(help="""List all incidents.

By default you will get incidents from the last hour. You can specify a time
range for when the incident occurred by specifying when the incident ended.

You can list incidents in different ways:

* Listing all incidents

* Listing all source incidents for a specific source with --source

* Listing all incidents for a specific validator with --validator

* Listing all incidents for a specific segment with --segment

* Listing all incidents for a specific validator and segment with --validator
and --segment together
""")
async def get(
    config_dir: str = ConfigDir,
    output_format: OutputFormat = OutputFormatOption,
    namespace: str = Namespace,
    ended_before: datetime = typer.Option(
        datetime.utcnow(),
        help="The incident ended before this timestamp",
    ),
    ended_after: datetime = typer.Option(
        (datetime.utcnow() - timedelta(hours=1)),
        help="The incident ended after this timestamp",
    ),
    validator: str = typer.Option(None, help="Validator to fetch incidents for"),
    segment: str = typer.Option(None, help="Segment to fetch incidents for"),
    source: str = typer.Option(None, help="Source to fetch incidents for"),
):
    vc, cfg = await get_client_and_config(config_dir)

    if validator is not None:
        validator_id = await validators.get_validator_id(vc, cfg, validator, namespace)
        if validator_id is None:
            return None

    if source is not None:
        source_id = await sources.get_source_id(vc, cfg, source, namespace)
        if source_id is None:
            return None

    # TODO(UI-2006): These should all support namespace

    incidents: None | list[GetValidatorIncidentsValidatorIncidents] | list[
        GetValidatorSegmentIncidentsValidatorSegmentIncidents
    ] | list[GetSegmentIncidentsSegmentIncidents] = None

    if validator and segment:
        incidents = await vc.get_validator_segment_incidents(
            ValidatorSegmentIncidentsInput(
                time_range=TimeRangeInput(
                    start=ended_after,
                    end=ended_before,
                ),
                validator_id=validator_id,
                segment_id=segment,
            )
        )
    elif validator:
        incidents = await vc.get_validator_incidents(
            ValidatorIncidentsInput(
                time_range=TimeRangeInput(
                    start=ended_after,
                    end=ended_before,
                ),
                validator_id=validator_id,
            )
        )
    elif segment:
        incidents = await vc.get_segment_incidents(
            SegmentIncidentsInput(
                time_range=TimeRangeInput(
                    start=ended_after,
                    end=ended_before,
                ),
                segment_id=segment,
            )
        )
    elif source:
        # Since source incidents looks completely different we hand them off to
        # a separate function, we can't re-use any of the rendering.
        return _output_text_source_incidents(
            output_format,
            await vc.get_source_incidents(
                SourceIncidentsInput(
                    time_range=TimeRangeInput(
                        start=ended_after,
                        end=ended_before,
                    ),
                    source_id=source_id,
                )
            ),
        )
    else:
        print("You need to specify one of --validator and/or --segment or --source")
        raise typer.Exit(code=1)

    if output_format == OutputFormat.JSON:
        return output_json(incidents)

    return output_text(
        incidents,
        fields={
            "operator": OutputSettings(
                attribute_name="metric",
                reformat=calculate_operator,
            ),
            "bound": OutputSettings(
                attribute_name="metric",
                reformat=calculate_bound,
            ),
            "value": OutputSettings(
                attribute_name="metric",
                reformat=lambda x: x.value,
            ),
            "age": OutputSettings(
                attribute_name="metric",
                reformat=lambda x: _format_relative_time(x.end_time),
            ),
        },
    )


def _output_text_source_incidents(output_format: OutputFormat, incidents: list[Any]):
    if output_format == OutputFormat.JSON:
        return output_json(incidents)

    @dataclass
    class SchemaChange:
        field: str
        change_type: str
        old_value: str
        new_value: str

    change_type_to_key = {
        "Nullability": "nullable",
        "JtdType": "type",
        "UnderlyingType": "underlying_type",
    }

    changes = []
    for item in incidents:
        # TODO: We only show schema changes for now
        if item.typename__ != "SchemaChangeNotification":
            continue

        for field, field_changes in item.payload.items():
            for ct in field_changes["change_types"]:
                k = change_type_to_key.get(ct)

                changes.append(
                    SchemaChange(
                        field=field,
                        change_type=ct,
                        old_value=field_changes["old"][k] if k else "-",
                        new_value=field_changes["new"][k] if k else "-",
                    )
                )

    return output_text(
        changes,
        fields={
            "field": None,
            "change_type": None,
            "old_value": None,
            "new_value": None,
        },
    )


def calculate_operator(item: Any):
    type_ = item.typename__[len("ValidatorMetricWith") :]
    if type_ == "DynamicThreshold":
        operator = item.decision_bounds_type
    else:
        operator = item.operator

    return f"{type_}/{operator}"


def calculate_bound(item: Any):
    type_ = item.typename__[len("ValidatorMetricWith") :]
    if type_ == "DynamicThreshold":
        bound = f"{item.lower_bound:.2f} - {item.upper_bound:.2f}"
    elif type_ == "FixedThreshold":
        bound = item.bound
    else:
        bound = "-"

    return bound


def _output_text_source_incidents_segment_limit_exceeded(
    incidents: list[GetSourceIncidentsSourceIncidentsSegmentLimitExceededNotification],
):
    return output_text(
        incidents,
        fields={
            "limit": None,
            "age": OutputSettings(attribute_name="created_at"),
        },
    )


if __name__ == "__main__":
    typer.run(app())
