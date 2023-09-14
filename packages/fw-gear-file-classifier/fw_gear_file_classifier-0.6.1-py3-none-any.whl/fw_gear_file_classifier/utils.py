"""Read and validate classification profiles."""
import logging
import sys
from pathlib import Path
from typing import Any, Dict

import flywheel
import yaml

log = logging.getLogger("root")
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
default_profiles = (Path(__file__).parents[0] / "classification_profiles").resolve()


def get_schema_definition(profile_path: Path) -> Dict:
    """Read yaml profile.

    Args:
        profile_path: path to yaml profile to read.

    Returns:
        dict:yaml profile converted to dictionary.
    """
    yaml_file = profile_path.as_posix()
    with open(yaml_file, "r", encoding="utf8") as file:
        yaml_dict = yaml.load(file, Loader=yaml.FullLoader)

    return yaml_dict


def is_modality_defined(client: flywheel.Client, modality: str) -> bool:
    """Returns True if file modality is defined in site modalities schema, False
    otherwise.

    Args:
        client (flywheel.Client): Flywheel client.
        modality (str): Modality to check.

    Returns:
        bool:true if it exists. false if it doesn't exist
    """
    modalities = [m.id for m in client.get_all_modalities()]

    if modality in modalities:
        log.debug(f"modality {modality} exists in site schema")
        return True
    else:
        log.debug(f"modality {modality} does not exist in site schema")
        return False


def compare_dict(dict1: dict, dict2: dict):
    """Returns True if the dictionaries are similar, False otherwise.

    Compare two dictionaries and return True if they are similar, False otherwise,
    ignoring keys and item value ordering.

    Args:
        dict1 (dict): First dictionary to compare.
        dict2 (dict): Second dictionary to compare.

    Returns:
        bool: True if the dictionaries are similar, False otherwise.
    """
    if sorted(dict1.keys()) == sorted(dict2.keys()):
        for key in dict1.keys():
            if sorted(dict1[key]) != sorted(dict2[key]):
                return False
        return True
    else:
        return False


def validate_modality_schema(client: flywheel.Client, file_obj: Dict[str, Any]) -> None:
    """Validate modality against predefined modality schema.

    Validate if the modality of the file input matches the predefined modality schema
    in the classification profile. Raises otherwise.

    Args:
        client (flywheel.Client): Flywheel client.
        file_obj (Dict[str, Any]): file input object.
    """
    file_modality = file_obj["modality"]
    if not is_modality_defined(client, file_modality):
        log.error(
            f"file modality {file_modality} is not defined in the modality site schema."
            f"Please visit https://gitlab.com/flywheel-io/scientific-solutions/lib/fw-classification-profiles/-/blob/main/README.md?ref_type=heads#how-to-modify-the-classification-schema "
            f"for more details."
        )
        sys.exit(1)

    # Get default schema
    default_schema_path = default_profiles / "fw-modality-classification.yaml"
    classification_schema = get_schema_definition(default_schema_path)

    predefined_schema = classification_schema.get(file_modality)
    if not predefined_schema:  # in case we don't have a schema for this modality
        log.error(f"modality {file_modality} unknown. No schema defined.")
        sys.exit(1)

    instance_schema = client.get_modality(file_modality)["classification"]
    if not compare_dict(predefined_schema, instance_schema):
        log.error(
            "Schema validation failed. Please check that modality schema in your "
            "instance matches the gear schema. For more details, please visit "
            "https://gitlab.com/flywheel-io/scientific-solutions/lib/fw-classification-profiles/-/blob/main/README.md?ref_type=heads#how-to-modify-the-classification-schema"
        )
        sys.exit(1)
    else:
        log.info("Modality schema is valid.")
