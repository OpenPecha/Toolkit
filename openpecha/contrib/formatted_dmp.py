import re
import urllib

from diff_match_patch import diff_match_patch


class Format:
    def __init__(self):
        pass

    def apply_patch(self, patch, mode=None):
        if mode == "CM":
            return self.cm_format(patch)
        else:  # default mode. same as DMP natively does.
            return self.default_format(patch)

    @staticmethod
    def default_format(patch):
        op, data = patch
        if op == -1:
            return ""
        elif op == 1:
            return data
        elif op == 0:
            return data
        else:
            raise ValueError("wrong patch operation value")

    @staticmethod
    def cm_format(patch):
        """
        Formats individual patches in CM.
        As the formatting is applied one patch at a time, substitutions can't be
        calculated at this stage. it has to be generated once all patches have been applied
        (see self.cm_substitutions() )
        """
        op, data = patch
        if op == -1:
            return "{--" + data + "--}"
        elif op == 1:
            return "{++" + data + "++}"
        elif op == 0:
            return data
        else:
            raise ValueError("wrong patch operation value")

    @staticmethod
    def cm_substitutions(string):
        """
        merges all sequences of deletion+insertion into a substitution
        ( {-- xx--}{++ yy++} ==> {~~xx~>yy~~} )
        """
        if "--}{++" in string:
            return re.sub(
                r"{-- ([^{}\-+]+)--}{\+\+ ([^{}\-+]+)\+\+}", r"{~~\1~>\2~~}", string
            )
        else:
            return string


class FormattedDMP(diff_match_patch):
    def __init__(self):
        super().__init__()
        self.formatting = Format()

    def patch_apply(self, patches, text, mode=None):
        """Merge a set of patches onto the text.  Return a patched text, as well
        as a list of true/false values indicating which patches were applied.

        Args:
          patches: Array of Patch objects.
          text: Old text.
          mode: formatting mode (see Format class)

        Returns:
          Two element Array, containing the new text and an array of boolean values.
        """
        if not patches:
            return (text, [])

        # Deep copy the patches so that no changes are made to originals.
        patches = self.patch_deepCopy(patches)

        nullPadding = self.patch_addPadding(patches)
        text = nullPadding + text + nullPadding
        self.patch_splitMax(patches)

        # delta keeps track of the offset between the expected and actual location
        # of the previous patch.  If there are patches expected at positions 10 and
        # 20, but the first patch was found at 12, delta is 2 and the second patch
        # has an effective expected position of 22.
        delta = 0
        results = []
        for patch in patches:
            expected_loc = patch.start2 + delta
            text1 = self.diff_text1(patch.diffs)
            end_loc = -1
            if len(text1) > self.Match_MaxBits:
                # patch_splitMax will only provide an oversized pattern in the case of
                # a monster delete.
                start_loc = self.match_main(
                    text, text1[: self.Match_MaxBits], expected_loc
                )
                if start_loc != -1:
                    end_loc = self.match_main(
                        text,
                        text1[-self.Match_MaxBits :],
                        expected_loc + len(text1) - self.Match_MaxBits,
                    )
                    if end_loc == -1 or start_loc >= end_loc:
                        # Can't find valid trailing context.  Drop this patch.
                        start_loc = -1
            else:
                start_loc = self.match_main(text, text1, expected_loc)
            if start_loc == -1:
                # No match found.  :(
                results.append(False)
                # Subtract the delta for this failed patch from subsequent patches.
                delta -= patch.length2 - patch.length1
            else:
                # Found a match.  :)
                results.append(True)
                delta = start_loc - expected_loc
                if end_loc == -1:
                    text2 = text[start_loc : start_loc + len(text1)]
                else:
                    text2 = text[start_loc : end_loc + self.Match_MaxBits]
                if text1 == text2:
                    # Perfect match, just shove the replacement text in.
                    text = (
                        text[:start_loc]
                        + self.diff_text2(patch.diffs, mode)
                        + text[start_loc + len(text1) :]
                    )
                else:
                    # Imperfect match.
                    # Run a diff to get a framework of equivalent indices.
                    diffs = self.diff_main(text1, text2, False)
                    if (
                        len(text1) > self.Match_MaxBits
                        and self.diff_levenshtein(diffs) / float(len(text1))
                        > self.Patch_DeleteThreshold
                    ):
                        # The end points match, but the content is unacceptably bad.
                        results[-1] = False
                    else:
                        self.diff_cleanupSemanticLossless(diffs)
                        index1 = 0
                        for (op, data) in patch.diffs:
                            if op != self.DIFF_EQUAL:
                                index2 = self.diff_xIndex(diffs, index1)
                            if op == self.DIFF_INSERT:  # Insertion
                                text = (
                                    text[: start_loc + index2]
                                    + self.formatting.apply_patch((op, data), mode)
                                    + text[start_loc + index2 :]
                                )
                            elif op == self.DIFF_DELETE:  # Deletion
                                text = (
                                    text[: start_loc + index2]
                                    + self.formatting.apply_patch((op, data), mode)
                                    + text[
                                        start_loc
                                        + self.diff_xIndex(diffs, index1 + len(data)) :
                                    ]
                                )
                            if op != self.DIFF_DELETE:
                                index1 += len(data)
        # Strip the padding off.
        text = text[len(nullPadding) : -len(nullPadding)]
        if mode == "CM":
            text = self.formatting.cm_substitutions(text)
        return (text, results)

    def diff_text2(self, diffs, mode=None):
        """Compute and return the destination text (all equalities and insertions).

        Args:
          diffs: Array of diff tuples.
          mode: formatting mode. See Format class

        Returns:
          Destination text.
        """
        text = []
        for d in diffs:
            text.append(self.formatting.apply_patch(d, mode))
        return "".join(text)

    def format_patch(self, patch):
        """
        presents the given patch in a Critic Markup format
        :return: string
        """
        out = [str(patch).split("\n")[0] + "\n"]
        for p in patch.diffs:
            out.append(self.formatting.apply_patch(p, "CM"))
        return "".join(out)

    @staticmethod
    def decode_patch(patch):
        """
        decodes the content of a patch that diff-match-patch had encoded in %XX format.
        :param patch: the str repr of a patch_obj containing data encoded with urllib
        :type patch: str
        :return: the patch with readable content. \n are encoded to %0A to retain the patch's format
        :rtype: str
        """
        lines = patch.rstrip("\n").split("\n")
        out = []
        for line in lines:
            if not line.startswith("@"):
                line = line[0] + urllib.parse.unquote(line[1:]).replace("\n", "%0A")
            out.append(line)
        return "\n".join(out)


if __name__ == "__main__":
    orig = "zabcde"
    edited = "abbdey"

    dmp = FormattedDMP()
    patches = dmp.patch_make(orig, edited)

    applied = dmp.patch_apply(patches, orig)
    edit = dmp.patch_apply(patches, orig, mode="CM")

    print("orig:", orig)
    print("edited:", applied)
    print("edited == applied:", edited == applied[0])
    print("critic markup:", edit)
