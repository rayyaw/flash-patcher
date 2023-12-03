# Generated from ../flash_patcher/antlr_source/Stagefile.g4 by ANTLR 4.13.1
# encoding: utf-8
from antlr4 import *
from io import StringIO
import sys
if sys.version_info[1] > 5:
	from typing import TextIO
else:
	from typing.io import TextIO

def serializedATN():
    return [
        4,1,4,18,2,0,7,0,2,1,7,1,2,2,7,2,1,0,1,0,1,1,1,1,1,2,1,2,5,2,13,
        8,2,10,2,12,2,16,9,2,1,2,0,0,3,0,2,4,0,0,16,0,6,1,0,0,0,2,8,1,0,
        0,0,4,14,1,0,0,0,6,7,5,1,0,0,7,1,1,0,0,0,8,9,5,2,0,0,9,3,1,0,0,0,
        10,13,3,0,0,0,11,13,3,2,1,0,12,10,1,0,0,0,12,11,1,0,0,0,13,16,1,
        0,0,0,14,12,1,0,0,0,14,15,1,0,0,0,15,5,1,0,0,0,16,14,1,0,0,0,2,12,
        14
    ]

class StagefileParser ( Parser ):

    grammarFileName = "Stagefile.g4"

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    sharedContextCache = PredictionContextCache()

    literalNames = [  ]

    symbolicNames = [ "<INVALID>", "PATCH_FILE", "ASSET_PACK_FILE", "WHITESPACE", 
                      "COMMENT" ]

    RULE_patchFile = 0
    RULE_assetPackFile = 1
    RULE_root = 2

    ruleNames =  [ "patchFile", "assetPackFile", "root" ]

    EOF = Token.EOF
    PATCH_FILE=1
    ASSET_PACK_FILE=2
    WHITESPACE=3
    COMMENT=4

    def __init__(self, input:TokenStream, output:TextIO = sys.stdout):
        super().__init__(input, output)
        self.checkVersion("4.13.1")
        self._interp = ParserATNSimulator(self, self.atn, self.decisionsToDFA, self.sharedContextCache)
        self._predicates = None




    class PatchFileContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def PATCH_FILE(self):
            return self.getToken(StagefileParser.PATCH_FILE, 0)

        def getRuleIndex(self):
            return StagefileParser.RULE_patchFile

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterPatchFile" ):
                listener.enterPatchFile(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitPatchFile" ):
                listener.exitPatchFile(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitPatchFile" ):
                return visitor.visitPatchFile(self)
            else:
                return visitor.visitChildren(self)




    def patchFile(self):

        localctx = StagefileParser.PatchFileContext(self, self._ctx, self.state)
        self.enterRule(localctx, 0, self.RULE_patchFile)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 6
            self.match(StagefileParser.PATCH_FILE)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class AssetPackFileContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def ASSET_PACK_FILE(self):
            return self.getToken(StagefileParser.ASSET_PACK_FILE, 0)

        def getRuleIndex(self):
            return StagefileParser.RULE_assetPackFile

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterAssetPackFile" ):
                listener.enterAssetPackFile(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitAssetPackFile" ):
                listener.exitAssetPackFile(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitAssetPackFile" ):
                return visitor.visitAssetPackFile(self)
            else:
                return visitor.visitChildren(self)




    def assetPackFile(self):

        localctx = StagefileParser.AssetPackFileContext(self, self._ctx, self.state)
        self.enterRule(localctx, 2, self.RULE_assetPackFile)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 8
            self.match(StagefileParser.ASSET_PACK_FILE)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class RootContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def patchFile(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(StagefileParser.PatchFileContext)
            else:
                return self.getTypedRuleContext(StagefileParser.PatchFileContext,i)


        def assetPackFile(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(StagefileParser.AssetPackFileContext)
            else:
                return self.getTypedRuleContext(StagefileParser.AssetPackFileContext,i)


        def getRuleIndex(self):
            return StagefileParser.RULE_root

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterRoot" ):
                listener.enterRoot(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitRoot" ):
                listener.exitRoot(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitRoot" ):
                return visitor.visitRoot(self)
            else:
                return visitor.visitChildren(self)




    def root(self):

        localctx = StagefileParser.RootContext(self, self._ctx, self.state)
        self.enterRule(localctx, 4, self.RULE_root)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 14
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==1 or _la==2:
                self.state = 12
                self._errHandler.sync(self)
                token = self._input.LA(1)
                if token in [1]:
                    self.state = 10
                    self.patchFile()
                    pass
                elif token in [2]:
                    self.state = 11
                    self.assetPackFile()
                    pass
                else:
                    raise NoViableAltException(self)

                self.state = 16
                self._errHandler.sync(self)
                _la = self._input.LA(1)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx





