# Generated from ../flash_patcher/antlr_source/PatchfileParser.g4 by ANTLR 4.13.1
from antlr4 import *
if "." in __name__:
    from .PatchfileParser import PatchfileParser
else:
    from PatchfileParser import PatchfileParser

# This class defines a complete listener for a parse tree produced by PatchfileParser.
class PatchfileParserListener(ParseTreeListener):

    # Enter a parse tree produced by PatchfileParser#addBlockHeader.
    def enterAddBlockHeader(self, ctx:PatchfileParser.AddBlockHeaderContext):
        pass

    # Exit a parse tree produced by PatchfileParser#addBlockHeader.
    def exitAddBlockHeader(self, ctx:PatchfileParser.AddBlockHeaderContext):
        pass


    # Enter a parse tree produced by PatchfileParser#addBlock.
    def enterAddBlock(self, ctx:PatchfileParser.AddBlockContext):
        pass

    # Exit a parse tree produced by PatchfileParser#addBlock.
    def exitAddBlock(self, ctx:PatchfileParser.AddBlockContext):
        pass


    # Enter a parse tree produced by PatchfileParser#addBlockText.
    def enterAddBlockText(self, ctx:PatchfileParser.AddBlockTextContext):
        pass

    # Exit a parse tree produced by PatchfileParser#addBlockText.
    def exitAddBlockText(self, ctx:PatchfileParser.AddBlockTextContext):
        pass


    # Enter a parse tree produced by PatchfileParser#removeBlock.
    def enterRemoveBlock(self, ctx:PatchfileParser.RemoveBlockContext):
        pass

    # Exit a parse tree produced by PatchfileParser#removeBlock.
    def exitRemoveBlock(self, ctx:PatchfileParser.RemoveBlockContext):
        pass


    # Enter a parse tree produced by PatchfileParser#root.
    def enterRoot(self, ctx:PatchfileParser.RootContext):
        pass

    # Exit a parse tree produced by PatchfileParser#root.
    def exitRoot(self, ctx:PatchfileParser.RootContext):
        pass



del PatchfileParser