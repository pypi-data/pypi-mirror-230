"""Main module."""
import logging
from typing import Any, Dict

from flywheel_gear_toolkit import GearToolkitContext
from fw_classification import Profile
from fw_classification.adapters import FWAdapter, NiftiFWAdapter

log = logging.getLogger(__name__)


def classify(
    file_input: Dict[str, Any], context: GearToolkitContext, profile: Profile
) -> int:
    """Run classification via fw-classification.

    This function is more or less a wrapper around the classification-toolkit
    [fw-classification](https://gitlab.com/flywheel-io/public/classification-toolkit),
    with a few gear specific additions.

    1. Set up correct adapter fw-classification adapter based on file type.
    2. Run classification
    3. Add gear qc information to input file.
    """
    # Needs context for update_*_metadata methods
    log.info("Starting classification.")
    if file_input["object"]["type"] == "nifti":
        fw_adapter = NiftiFWAdapter(file_input, context)
    else:
        fw_adapter = FWAdapter(file_input, context)
    result = fw_adapter.classify(profile)
    log.info(f"Finished classification. Result: {result}")
    if not result:
        log.warning("Unsuccessful classification")
    log.info("Adding gear qc info.")
    # Add qc result "classification"
    context.metadata.add_qc_result(
        file_input, "classification", "PASS" if result else "FAIL"
    )

    return int(not result)
