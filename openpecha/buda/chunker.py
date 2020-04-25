def get_n_char(string, n):
    """
    Returns n unicode char
    """
    return string[:n]


def get_chunk(string, n, char):
    """
    Returns an index of where the string has the last char, if the char is not found in n char, the function doubles n
    and looks for the first char in that double chunk, if the char is still not found it looks for the last space in the
    original chunk, if still no space was found in the chunk than just returns n to cut up the string arbitrarily
    """
    chunk = get_n_char(string, n)
    index = chunk.rfind(char)
    if index > -1:
        return index + len(char)
    else:
        double_chunk = get_n_char(string, n * 2)
        index = double_chunk.find(char)
        if index != -1:
            return index + len(char)
        else:
            index = chunk.rfind(" ")
            if index != -1:
                return index + 1
            else:
                return n


def get_chunks(string, n, char):
    """
    Returns a list of indexes of the string cut up in chunks of a maximum of n length and cut up at the last char
    """
    list_of_index = [0]

    while len(string[list_of_index[-1]:]) > n:
        index = get_chunk(string[list_of_index[-1]:], n, char)
        list_of_index.append(list_of_index[-1] + index)

    list_of_index.append(list_of_index[-1] + len(string[list_of_index[-1]:]))
    return list_of_index


