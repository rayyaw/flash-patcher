# Generated from ../flash_patcher/antlr_source/Stagefile.g4 by ANTLR 4.13.1
from antlr4 import *
if "." in __name__:
    from .StagefileParser import StagefileParser
else:
    from StagefileParser import StagefileParser

# This class defines a complete listener for a parse tree produced by StagefileParser.
class StagefileListener(ParseTreeListener):

    # Enter a parse tree produced by StagefileParser#patchFile.
    def enterPatchFile(self, ctx:StagefileParser.PatchFileContext):
        pass

    # Exit a parse tree produced by StagefileParser#patchFile.
    def exitPatchFile(self, ctx:StagefileParser.PatchFileContext):
        pass


    # Enter a parse tree produced by StagefileParser#assetPackFile.
    def enterAssetPackFile(self, ctx:StagefileParser.AssetPackFileContext):
        pass

    # Exit a parse tree produced by StagefileParser#assetPackFile.
    def exitAssetPackFile(self, ctx:StagefileParser.AssetPackFileContext):
        pass


    # Enter a parse tree produced by StagefileParser#root.
    def enterRoot(self, ctx:StagefileParser.RootContext):
        pass

    # Exit a parse tree produced by StagefileParser#root.
    def exitRoot(self, ctx:StagefileParser.RootContext):
        pass



del StagefileParser