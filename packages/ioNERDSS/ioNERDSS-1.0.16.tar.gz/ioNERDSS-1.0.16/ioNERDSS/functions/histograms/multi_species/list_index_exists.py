def list_index_exists(lst,index):
    """Checks if a there is something at index of the list

    Args:
        lst (list): the list you are checking
        index (int): the index of the list you are checking

    Returns:
        boolean: if that index exists for that list
    """
    
    try:
        lst[index]
        return True
    except IndexError:
        return False
