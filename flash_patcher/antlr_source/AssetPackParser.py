# Generated from ../flash_patcher/antlr_source/AssetPack.g4 by ANTLR 4.13.1
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
        4,1,4,19,2,0,7,0,2,1,7,1,2,2,7,2,1,0,1,0,1,0,1,0,1,1,5,1,12,8,1,
        10,1,12,1,15,9,1,1,2,1,2,1,2,0,0,3,0,2,4,0,0,16,0,6,1,0,0,0,2,13,
        1,0,0,0,4,16,1,0,0,0,6,7,5,1,0,0,7,8,3,4,2,0,8,9,3,4,2,0,9,1,1,0,
        0,0,10,12,3,0,0,0,11,10,1,0,0,0,12,15,1,0,0,0,13,11,1,0,0,0,13,14,
        1,0,0,0,14,3,1,0,0,0,15,13,1,0,0,0,16,17,5,2,0,0,17,5,1,0,0,0,1,
        13
    ]

class AssetPackParser ( Parser ):

    grammarFileName = "AssetPack.g4"

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    sharedContextCache = PredictionContextCache()

    literalNames = [  ]

    symbolicNames = [ "<INVALID>", "ADD_ASSET", "FILE_NAME", "WHITESPACE", 
                      "COMMENT" ]

    RULE_addAssetBlock = 0
    RULE_root = 1
    RULE_file_name = 2

    ruleNames =  [ "addAssetBlock", "root", "file_name" ]

    EOF = Token.EOF
    ADD_ASSET=1
    FILE_NAME=2
    WHITESPACE=3
    COMMENT=4

    def __init__(self, input:TokenStream, output:TextIO = sys.stdout):
        super().__init__(input, output)
        self.checkVersion("4.13.1")
        self._interp = ParserATNSimulator(self, self.atn, self.decisionsToDFA, self.sharedContextCache)
        self._predicates = None




    class AddAssetBlockContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser
            self.local = None # File_nameContext
            self.swf = None # File_nameContext

        def ADD_ASSET(self):
            return self.getToken(AssetPackParser.ADD_ASSET, 0)

        def file_name(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(AssetPackParser.File_nameContext)
            else:
                return self.getTypedRuleContext(AssetPackParser.File_nameContext,i)


        def getRuleIndex(self):
            return AssetPackParser.RULE_addAssetBlock

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterAddAssetBlock" ):
                listener.enterAddAssetBlock(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitAddAssetBlock" ):
                listener.exitAddAssetBlock(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitAddAssetBlock" ):
                return visitor.visitAddAssetBlock(self)
            else:
                return visitor.visitChildren(self)




    def addAssetBlock(self):

        localctx = AssetPackParser.AddAssetBlockContext(self, self._ctx, self.state)
        self.enterRule(localctx, 0, self.RULE_addAssetBlock)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 6
            self.match(AssetPackParser.ADD_ASSET)
            self.state = 7
            localctx.local = self.file_name()
            self.state = 8
            localctx.swf = self.file_name()
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

        def addAssetBlock(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(AssetPackParser.AddAssetBlockContext)
            else:
                return self.getTypedRuleContext(AssetPackParser.AddAssetBlockContext,i)


        def getRuleIndex(self):
            return AssetPackParser.RULE_root

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

        localctx = AssetPackParser.RootContext(self, self._ctx, self.state)
        self.enterRule(localctx, 2, self.RULE_root)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 13
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==1:
                self.state = 10
                self.addAssetBlock()
                self.state = 15
                self._errHandler.sync(self)
                _la = self._input.LA(1)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class File_nameContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def FILE_NAME(self):
            return self.getToken(AssetPackParser.FILE_NAME, 0)

        def getRuleIndex(self):
            return AssetPackParser.RULE_file_name

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterFile_name" ):
                listener.enterFile_name(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitFile_name" ):
                listener.exitFile_name(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitFile_name" ):
                return visitor.visitFile_name(self)
            else:
                return visitor.visitChildren(self)




    def file_name(self):

        localctx = AssetPackParser.File_nameContext(self, self._ctx, self.state)
        self.enterRule(localctx, 4, self.RULE_file_name)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 16
            self.match(AssetPackParser.FILE_NAME)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx





