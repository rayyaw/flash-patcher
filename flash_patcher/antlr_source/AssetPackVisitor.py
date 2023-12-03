# Generated from ../flash_patcher/antlr_source/AssetPack.g4 by ANTLR 4.13.1
from antlr4 import *
if "." in __name__:
    from .AssetPackParser import AssetPackParser
else:
    from AssetPackParser import AssetPackParser

# This class defines a complete generic visitor for a parse tree produced by AssetPackParser.

class AssetPackVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by AssetPackParser#addAssetBlock.
    def visitAddAssetBlock(self, ctx:AssetPackParser.AddAssetBlockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by AssetPackParser#root.
    def visitRoot(self, ctx:AssetPackParser.RootContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by AssetPackParser#file_name.
    def visitFile_name(self, ctx:AssetPackParser.File_nameContext):
        return self.visitChildren(ctx)



del AssetPackParser