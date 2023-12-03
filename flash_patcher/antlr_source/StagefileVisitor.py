# Generated from ../flash_patcher/antlr_source/Stagefile.g4 by ANTLR 4.13.1
from antlr4 import *
if "." in __name__:
    from .StagefileParser import StagefileParser
else:
    from StagefileParser import StagefileParser

# This class defines a complete generic visitor for a parse tree produced by StagefileParser.

class StagefileVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by StagefileParser#patchFile.
    def visitPatchFile(self, ctx:StagefileParser.PatchFileContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by StagefileParser#assetPackFile.
    def visitAssetPackFile(self, ctx:StagefileParser.AssetPackFileContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by StagefileParser#root.
    def visitRoot(self, ctx:StagefileParser.RootContext):
        return self.visitChildren(ctx)



del StagefileParser