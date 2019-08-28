from pathlib import Path


class Serialize(object):
    """
    This class is used when serializing the .opf into anything else (Markdown, TEI, etc.).

    It is relatively abstract and needs to be inherited by a class doing an actual serialization.

    Note that currently we suppose that we're only adding characters, never removing any. This can
    change in the future but let's start simple.

    To use it, instantiate a concrete class with the path of the opf file, and call apply_layers() then get_result()
    """
    def __init__(self, opfpath, layers = None):
        self.opfpath = Path(opfpath)
        self.baselayer = self.__read_base_layer()
        """
        The charstoapply is an important piece of the puzzle here. Basically applying the changes to the string directly is a
        bad idea for several reasons:
          - changing a big string with each annotation is costly
          - the application can be complex as character coordinate keep changing all the time

        So instead of just changing the string, we fill an object with all the characters we're going to add, then
        apply all the changes at once. This simplifies the code, the logic and is more efficient.

        The object has the following structure:

        {
            charcoord: (["string to apply before"],["string to apply after"])
        }

        So for example:
          - there is an annotation that goes from character 10 to character 15
          - the serialization you want to make is to add "<title>" before and "</title>" after the title
          - the charstoapply object will be:

        {
            10: ([], ["<title>"]),
            15: (["</title>"], [])
        }
        """
        self.charstoapply = {}
        # layer lists the layers to be applied, in the order of which they should be applied
        # by convention, when it is None, all layers are applied in alphabetical order (?)
        self.layers = layers

    def __read_base_layer(self):
        """
        reads opfpath/base.txt and returns its content
        """
        return (self.opfpath/'base.txt').read_text()

    def apply_layer(self, layerid):
        """
        This reads the file opfpath/layers/layerid.yml and applies all the annotations it contains, in the order in which they appear.
        I think it can be implemented in this class by just calling self.apply_annotation on each annotation of the file.
        """
        pass

    def apply_layers(self):
        """
        This applies all the layers recorded in self.layers. If self.layers is none, it reads all the layers from the layer directory.
        """
        pass

    def add_chars(self, cc, frombefore, charstoadd):
        """
        This records some characters to add at a character coordinate (cc), either frombefore (from the left) or after. before is a boolean.
        """
        if cc not in self.charstoapply:
            self.charstoapply[cc] = ([],[])
        if frombefore: # if from the left, layers should be applied in reverse order
            self.charstoapply[cc][0].insert(0, charstoadd)
        else:
            self.charstoapply[cc][1].append(charstoadd)

    #@serialize.abstractmethod
    def apply_annotation(self, annotation):
        """
        This applies the annotation given as argument. The annotation must contain at least a type
        """
        raise NotImplementedError("The Serialize class doesn't provide any serialization, please use a subclass such ass SerializeMd")

    def get_result(self):
        """
        returns a string which is the base layer where the changes recorded in self.charstoapply have been applied. 

        The algorithm should be something like:
        """
        res = "" 
        # don't actually do naive string concatenations
        # see https://waymoot.org/home/python_string/ where method 5 is good
        i = 0
        for c in self.baselayer:
            if i in self.charstoapply:
                apply = self.charstoapply[i]
                for s in apply[0]:
                    res += s
                res += c
                for s in apply[1]:
                    res += s
            else:
                res += c 
            i += 1
        return res