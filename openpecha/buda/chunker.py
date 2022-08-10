import re


class StringChunker:
    def __init__(self, full_string, pattern, target_len = 1500, start_cc = 0, end_cc = 0):
        self.pattern  = pattern
        self.string   = full_string
        self.target_len  = target_len
        self.start_cc = start_cc
        self.end_cc   = end_cc if end_cc > 0 else len(full_string)

    def get_next_chunk_index(self, last_index):
        """
        Returns an index of where the string has the last char, if the char is not found in n char,
        the function doubles n and looks for the first char in that double chunk,
        if the char is still not found it looks for the last space in the original chunk,
        if still no space was found in the chunk than just returns n to cut up the string arbitrarily
        """
        end_cc = min(self.end_cc, last_index + 2 * self.target_len)
        next_target = last_index + self.target_len
        next_idx_before_target_len = -1
        for match in self.pattern.finditer(self.string, last_index, end_cc):
            if match.end() < next_target:
                next_idx_before_target_len = match.end()
            else:
                if next_idx_before_target_len != -1:
                    return next_idx_before_target_len
                return match.end()
        return next_target

    def get_chunks(self):
        """
        Returns a list of indexes of the string cut up in chunks of a maximum of n length and cut up at the last
        instance of regex
        """
        list_of_index = [0]
        string = self.string
        index = self.start_cc
        while self.end_cc - index > self.target_len:
            index = self.get_next_chunk_index(index)
            list_of_index.append(index)
        if index != self.end_cc:
            list_of_index.append(self.end_cc)
        return list_of_index


ENG_PATTERN = re.compile(r"\.")

class EnglishEasyChunker(StringChunker):
    def __init__(self, full_string, max_len, start_cc = 0, end_cc = 0):
        StringChunker.__init__(
            self,
            full_string,
            ENG_PATTERN,
            max_len,
            start_cc,
            end_cc
        )


TIB_PATTERN = re.compile(r"([སའངགདནབམརལཏ]ོ།[^ཀ-ཬ]*|།།[^ཀ-ཬ༠-༩]*།[^ཀ-ཬ༠-༩]*)")


class TibetanEasyChunker(StringChunker):
    def __init__(self, full_string, max_len, start_cc = 0, end_cc = 0):
        StringChunker.__init__(
            self,
            full_string,
            TIB_PATTERN,
            max_len,
            start_cc,
            end_cc
        )
