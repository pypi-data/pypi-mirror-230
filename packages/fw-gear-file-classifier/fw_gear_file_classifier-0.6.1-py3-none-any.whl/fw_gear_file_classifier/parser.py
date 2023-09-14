"""Parser module to parse gear config.json."""
import logging
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from flywheel_gear_toolkit import GearToolkitContext
from fw_classification.classify import Profile
from fw_classification.classify.block import Block
from fw_core_client import CoreClient

from . import PKG_NAME, __version__

log = logging.getLogger(__name__)

default_profiles = (Path(__file__).parents[0] / "classification_profiles").resolve()


def parse_config(
    gear_context: GearToolkitContext,
) -> Tuple[Dict[str, Any], Profile, bool]:  # File input  # Profile to classify with
    """Parse options from gear config.

    Args:
        gear_context (GearToolkitContext): Gear toolkit context.

    Returns:
        tuple:
            - File input as a dictionary
            - Profile to use for classification, defaults to the
                classification-toolkits "main.yml"
    """
    file_input: Dict[str, Any] = gear_context.get_input("file-input")
    validate = gear_context.config["validate"]
    # Get optional custom profile from input
    profile_path: Optional[Path] = gear_context.get_input_path("profile")
    if profile_path:
        log.info(f"Using profile from input {profile_path}")
        profile = Profile(profile_path, include_search_dirs=[default_profiles])
    else:
        # Default to the classification-toolkit's "main.yml" which
        #   should be a "catch-all" and is defined in the fw-classifcation
        #   repo under (fw_classification/profiles/main.yml)
        log.info("Using default profile 'main.yml'")
        profile = Profile(default_profiles / "main.yml")

    # Get optional custom classifications from project context
    project = get_parent_project(file_input, gear_context)
    log.info(f"Looking for custom classifications in project {project.label}")
    classify_context = project.get("info", {}).get("classifications", {})
    custom_block = None
    if classify_context:
        log.debug(f"Context classification: {classify_context}")
        try:
            block = {"name": "custom", "rules": classify_context}
            custom_block, err = Block.from_dict(block)
            if err:
                log.error("\n".join([str(e) for e in err]))
                raise RuntimeError()
            log.info(
                "Found custom classification in project context, parsed as: \n"
                f"{custom_block}"
            )
            # Add custom block to the end of the profile if it's defined.
            profile.handle_block(custom_block, "custom")  # type: ignore
        except:  # pylint: disable=bare-except
            log.warning(
                "Could not handle context classification " f"{classify_context}"
            )

    return file_input, profile, validate


def get_parent(file_input: dict, context: GearToolkitContext):
    """Find parent project for a given file."""
    api_key = context.config_json["inputs"]["api-key"]["key"]
    log.debug("Instantiating CoreClient.")
    fw = CoreClient(api_key=api_key, client_name=PKG_NAME, client_version=__version__)
    parent_ref = file_input["hierarchy"]
    log.debug("Getting parent container.")
    parent = fw.get(f"/{parent_ref['type']}s/{parent_ref['id']}")
    return parent, fw


def get_parent_project(file_input: dict, context: GearToolkitContext):
    """Parent project of a particular file."""
    parent, fw = get_parent(file_input, context)
    log.debug("Getting parent project.")
    project = fw.get(f"/projects/{parent['parents']['project']}")
    return project
