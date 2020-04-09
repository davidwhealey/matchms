from matchms.utils import mol_converter


def clean_inchis(spectrum, rescue_smiles=True):
    """Make inchi style more consistent and wrongly given smiles.

    Read spectrum, look for inchi. Then:
    1) Make line with inchi homogeneously looking like: '"InChI=..."'
    2) if rescue_smiles is True then try to detect inchi that are actually smiles
    and convert to proper inchi (using openbabel based function from MS_functions.py).
    """
    # Empirically found list of strings that represent empty entries
    empty_entry_types = ['N/A', 'n/a', 'NA', 0, '0', '""', '', 'nodata',
                         '"InChI=n/a"', '"InChI="', 'InChI=1S/N\n', '\t\r\n']
    inchi = spectrum.metadata["inchi"]
    if inchi in empty_entry_types:
        inchi = 'n/a'
    else:
        inchi = inchi.replace(" ", "")  # Remove empty spaces
        if inchi.split('InChI=')[-1][0] in ['C', 'c', 'O', 'N']:
            if rescue_smiles:
                # Try to 'rescue' given inchi which are actually smiles!
                assumed_smile = inchi.split('InChI=')[-1].replace('"', '')
                inchi = mol_converter(assumed_smile, "smi", "inchi")
                print('new inchi:', inchi, assumed_smile)

        inchi = inchi.strip().split('InChI=')[-1]
        if inchi.endswith('"'):
            inchi = '"InChI=' + inchi
        elif inchi.endswith('\n'):
            inchi = '"InChI=' + inchi[:-2] + '"'
        elif inchi.endswith('\n"'):
            inchi = '"InChI=' + inchi[:-3] + '"'
        else:
            inchi = '"InChI=' + inchi + '"'
    spectrum.metadata["inchi"] = inchi
    return spectrum
