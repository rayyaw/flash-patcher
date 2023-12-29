parser grammar PatchfileParser;

options {tokenVocab=PatchfileLexer;}

addBlockHeader      : ADD FILENAME locationToken;
addBlock            : addBlockHeader+ BEGIN_PATCH addBlockText END_PATCH;
addBlockText        : AS_TEXT+;

removeBlock         : REMOVE FILENAME locationToken DASH locationToken;

root                : (addBlock | removeBlock)*;

locationToken       : OPEN_BLOCK? FUNCTION FUNCTION_NAME INTEGER? CLOSE_BLOCK?  # function
                    | INTEGER                                                   # lineNumber
                    | END                                                       # end
                    ;