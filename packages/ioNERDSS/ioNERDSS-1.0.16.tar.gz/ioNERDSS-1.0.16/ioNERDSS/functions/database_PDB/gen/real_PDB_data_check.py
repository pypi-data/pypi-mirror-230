def real_PDB_data_check(data):
    """
    Check if the PDB data is valid.

    Args:
        data (list): List of PDB data to be checked.

    Returns:
        int: -1 if the length of data is not equal to 12 because the amino acid name combined with previous section
             -2 if the length of data is equal to 12 but the amino acid name is not of length 3.
              1 if the data is valid.

    """
    
    if len(data) != 12:
        if len(data[2]) > 4:
            return -1  # Amino acid name stick with info before
    else:
        if len(data[3]) == 3:
            return 1  # True data
        else:
            return -2  # Wrong amino acid name
