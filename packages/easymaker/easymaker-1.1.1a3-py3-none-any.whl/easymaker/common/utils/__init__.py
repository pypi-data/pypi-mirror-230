from easymaker.common import constants
from easymaker.common.exceptions import EasyMakerRegionError, EasyMakerError


def validate_region(region: str) -> bool:
    """Validates region against supported regions.

    Args:
        region: region to validate
    Returns:
        bool: True if no errors raised
    Raises:
        ValueError: If region is not in supported regions.
    """
    if not region:
        raise EasyMakerRegionError(
            f"Please provide a region"
        )

    region = region.lower()
    if region not in constants.SUPPORTED_REGIONS:
        raise EasyMakerRegionError(
            f"Unsupported region"
        )

    return True


def from_name_to_id(list: list, name: str) -> str:
    for item in list:
        if item['name'] == name:
            return item['id']

    raise EasyMakerError(
        f"Invalid name : {name}"
    )
