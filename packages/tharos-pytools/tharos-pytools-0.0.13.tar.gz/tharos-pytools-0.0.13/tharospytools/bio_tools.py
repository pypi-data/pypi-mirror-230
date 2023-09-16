"Tools for biological sequences"


def revcomp(string: str, compl: dict = {'A': 'T', 'C': 'G', 'G': 'C', 'T': 'A', 'N': 'N'}) -> str:
    """Tries to compute the reverse complement of a sequence

    Args:
        string (str): original character set
        compl (dict, optional): dict of correspondances. Defaults to {'A': 'T', 'C': 'G', 'G': 'C', 'T': 'A'}.

    Raises:
        IndexError: Happens if revcomp encounters a char that is not in the dict

    Returns:
        str: the reverse-complemented string
    """
    try:
        return ''.join([compl[s] for s in string][::-1])
    except IndexError as exc:
        raise IndexError(
            "Complementarity does not include all chars in sequence.") from exc
