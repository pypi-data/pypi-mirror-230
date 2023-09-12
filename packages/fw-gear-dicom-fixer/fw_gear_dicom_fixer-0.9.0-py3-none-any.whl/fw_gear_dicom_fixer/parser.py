"""Parser module to parse gear config.json."""
import os
import typing as t
from pathlib import Path

from flywheel_gear_toolkit import GearToolkitContext
from fw_file.dicom import get_config


def parse_config(
    gear_context: GearToolkitContext,
) -> t.Tuple[Path, bool, bool, str]:
    """Parse config.json and return relevant inputs and options."""
    input_path = Path(gear_context.get_input_path("dicom")).resolve()
    transfer_syntax = gear_context.config.get("standardize_transfer_syntax", False)
    unique = gear_context.config.get("unique", False)
    zip_single = gear_context.config.get("zip-single-dicom", "match")

    config = get_config()
    config.reading_validation_mode = (
        "2" if gear_context.config.get("strict-validation", False) else "1"
    )
    if gear_context.config.get("dicom-standard", "local") == "current":
        config.standard_rev = "current"

    return input_path, transfer_syntax, unique, zip_single
