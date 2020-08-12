import re


class StringChunker:
    def __init__(self, full_string, pattern, n):
        self.pattern = pattern
        self.string = full_string
        self.n = n

    @staticmethod
    def get_n_char(string, n):
        """
        Returns n unicode char
        """
        return string[:n]

    def find_last_match_pos(self, string):
        """
        Finds and return the last possible match of the pattern
        """
        match = None
        for match in re.finditer(self.pattern, string):
            pass
        return match.end() if match else -1

    def find_first_match_pos(self, string):
        """
        Finds and return the first possible match of the pattern
        """
        match = None
        for match in re.finditer(self.pattern, string):
            return match.end() if match else -1

    def get_chunk(self, string, n):
        """
        Returns an index of where the string has the last char, if the char is not found in n char,
        the function doubles n and looks for the first char in that double chunk,
        if the char is still not found it looks for the last space in the original chunk,
        if still no space was found in the chunk than just returns n to cut up the string arbitrarily
        """
        chunk = self.get_n_char(string, n)
        index = self.find_last_match_pos(chunk)
        if index > -1:
            return index
        else:
            double_chunk = self.get_n_char(string, n * 2)
            index = self.find_last_match_pos(double_chunk)
            if index > -1:
                return index
            else:
                index = chunk.rfind(" ")
                if index > -1:
                    return index + 1
                else:
                    return n

    def get_chunks(self):
        """
        Returns a list of indexes of the string cut up in chunks of a maximum of n length and cut up at the last
        instance of regex
        """
        list_of_index = [0]
        string = self.string
        while len(string[list_of_index[-1] :]) > self.n:
            index = self.get_chunk(string[list_of_index[-1] :], self.n)
            list_of_index.append(list_of_index[-1] + index)

        list_of_index.append(list_of_index[-1] + len(string[list_of_index[-1] :]))
        return list_of_index
