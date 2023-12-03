# Generated from ../flash_patcher/antlr_source/PatchfileParser.g4 by ANTLR 4.13.1
from antlr4 import *
if "." in __name__:
    from .PatchfileParser import PatchfileParser
else:
    from PatchfileParser import PatchfileParser

# This class defines a complete generic visitor for a parse tree produced by PatchfileParser.

class PatchfileParserVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by PatchfileParser#addBlockHeader.
    def visitAddBlockHeader(self, ctx:PatchfileParser.AddBlockHeaderContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PatchfileParser#addBlock.
    def visitAddBlock(self, ctx:PatchfileParser.AddBlockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PatchfileParser#addBlockText.
    def visitAddBlockText(self, ctx:PatchfileParser.AddBlockTextContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PatchfileParser#removeBlock.
    def visitRemoveBlock(self, ctx:PatchfileParser.RemoveBlockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PatchfileParser#root.
    def visitRoot(self, ctx:PatchfileParser.RootContext):
        return self.visitChildren(ctx)



del PatchfileParser