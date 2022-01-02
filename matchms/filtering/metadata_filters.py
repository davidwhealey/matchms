import logging
from matchms.utils import get_first_common_element


logger = logging.getLogger("matchms")


_default_key = "precursor_mz"
_accepted_keys = ["precursormz", "precursor_mass"]
_accepted_types = (float, str, int)
_accepted_missing_entries = ["", "N/A", "NA", "n/a"]


def _convert_precursor_mz(precursor_mz):
    """Convert precursor_mz to number if possible. Otherwise return None."""
    if precursor_mz is None:
        return None
    if isinstance(precursor_mz, str) and precursor_mz in _accepted_missing_entries:
        return None
    if not isinstance(precursor_mz, _accepted_types):
        logger.warning("Found precursor_mz of undefined type.")
        return None
    if isinstance(precursor_mz, str):
        try:
            return float(precursor_mz.strip())
        except ValueError:
            logger.warning("%s can't be converted to float.", precursor_mz)
            return None
    return precursor_mz


def _add_precursor_mz_metadata(metadata):
    precursor_mz_key = get_first_common_element(metadata.keys(),
                                                [_default_key] + _accepted_keys)
    precursor_mz = metadata.get(precursor_mz_key)
    precursor_mz = _convert_precursor_mz(precursor_mz)
    if isinstance(precursor_mz, (float, int)):
        metadata["precursor_mz"] = float(precursor_mz)
        for key in _accepted_keys:
            metadata.pop(key, None)
        return metadata

    pepmass = metadata.get("pepmass", None)
    if pepmass is not None and _convert_precursor_mz(pepmass[0]) is not None:
        metadata["precursor_mz"] = pepmass[0]
        logger.info("Added precursor_mz entry based on field 'pepmass'.")
        return metadata

    logger.warning("No precursor_mz found in metadata.")
    return metadata