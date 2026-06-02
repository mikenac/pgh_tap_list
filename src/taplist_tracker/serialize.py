from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .models import BrewerySnapshot, SourceRecord


def snapshots_to_json(snapshots: list[BrewerySnapshot]) -> str:
    payload: list[dict[str, Any]] = [snapshot.as_dict() for snapshot in snapshots]
    return json.dumps(payload, indent=2, sort_keys=True)


def source_records_to_json(records: list[SourceRecord]) -> str:
    payload: list[dict[str, Any]] = [record.as_dict() for record in records]
    return json.dumps(payload, indent=2, sort_keys=True)


def write_snapshot_history(output_file: Path, snapshots: list[BrewerySnapshot]) -> None:
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(snapshots_to_json(snapshots), encoding="utf-8")
