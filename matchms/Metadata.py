from collections.abc import Mapping
import numpy as np
from pickydict import PickyDict
from .filtering.add_precursor_mz import _add_precursor_mz_metadata
from .filtering.interpret_pepmass import _interpret_pepmass_metadata
from .filtering.make_charge_int import _convert_charge_to_int
from .utils import load_known_key_conversions


_key_regex_replacements = {r"\s": "_",
                           r"[!?.,;:]": ""}
_key_replacements = load_known_key_conversions()


class Metadata:
    """Class to handle spectrum metadata in matchms.


    """
    def __init__(self, metadata: PickyDict = None,
                 harmonize_defaults: bool = True):
        """

        Parameters
        ----------
        metadata : PickyDict
            Spectrum metadata as a dictionary.
        harmonize_defaults : bool, optional
            Set to False if metadata harmonization to default keys is not desired.
            The default is True.

        """
        if metadata is None:
            self._data = PickyDict({})
        elif isinstance(metadata, Mapping):
            self._data = PickyDict(metadata)
        else:
            raise ValueError("Unexpected data type for metadata (should be dictionary, or None).")

        self.harmonize_defaults = harmonize_defaults
        if harmonize_defaults is True:
            self.harmonize_metadata()

    def __eq__(self, other_metadata):
        if self.keys() != other_metadata.keys():
            return False
        for key, value in self.items():

            if isinstance(value, np.ndarray):
                if not np.all(value == other_metadata.get(key)):
                    return False
            elif value != other_metadata.get(key):
                return False
        return True

    def harmonize_metadata(self):
        """Runs default harmonization of metadata.

        Method harmonized metadata field names which includes setting them to lower-case
        and runing a series of regex replacements followed by default field name
        replacements (such as precursor_mass --> precursor_mz).

        """
        self._data.key_regex_replacements = _key_regex_replacements
        self._data.key_replacements = _key_replacements
        self._data = _interpret_pepmass_metadata(self._data)
        if self.get("ionmode") is not None:
            self._data["ionmode"] = self.get("ionmode").lower()
        if self.get("ionmode") is None:
            self._data["ionmode"] = "n/a"
        self._data = _add_precursor_mz_metadata(self._data)
        charge = self.get("charge")
        if not isinstance(charge, int) and not _convert_charge_to_int(charge) is None:
            self._data["charge"] = _convert_charge_to_int(charge)

    def set_pickyness(self, key_replacements: dict = None,
                      key_regex_replacements: dict = None,
                      force_lower_case: bool = True):
        """Function to set the pickyness of the underlying metadata dictionary.

        Will automatically also run the new replacements if the dictionary already exists.

        Parameters
        ----------
        key_replacements : dict, optional
            This is second dictionary within PickyDict containing mappings of all
            keys which the user wants to force into a specific form (see code example).
        key_regex_replacements : dict, optional
            This additional dictionary contains pairs of regex (regular expression) strings
            and replacement strings to clean and harmonize the main dictionary keys.
            An example would be {r"\\s": "_"} which will replace all spaces with underscores.
        force_lower_case : bool, optional
            If set to True (default) all dictionary keys will be forced to be lower case.
        """
        self._data.set_pickyness(key_replacements=key_replacements,
                                 key_regex_replacements=key_regex_replacements,
                                 force_lower_case=force_lower_case)

    # ------------------------------
    # Getters and Setters
    # ------------------------------
    def get(self, key: str, default=None):
        """Retrieve value from :attr:`metadata` dict.
        """
        return self._data.copy().get(key, default)

    def set(self, key: str, value):
        """Set value in :attr:`metadata` dict.
        """
        self._data[key] = value
        if self.harmonize_defaults is True:
            self.harmonize_metadata()
        return self

    def keys(self):
        """Retrieve all keys of :attr:`.metadata` dict.
        """
        return self._data.keys()

    def values(self):
        """Retrieve all values of :attr:`.metadata` dict.
        """
        return self._data.values()

    def items(self):
        """Retrieve all items (key, value pairs) of :attr:`.metadata` dict.
        """
        return self._data.items()

    def __getitem__(self, key=None):
        return self.get(key)

    def __setitem__(self, key, newvalue):
        self.set(key, newvalue)

    @property
    def data(self):
        return self._data.copy()

    @data.setter
    def data(self, value):
        self._data = value