parser grammar PatchfileParser;

options {tokenVocab=PatchfileLexer;}

addBlockHeader      : ADD FILENAME locationToken;
addBlock            : addBlockHeader+ BEGIN_PATCH addBlockText END_PATCH;
addBlockText        : AS_TEXT+;

removeBlock         : REMOVE FILENAME locationToken DASH locationToken;

root                : (addBlock | removeBlock)*;

locationToken       : FUNCTION FUNCTION_NAME INTEGER?   # function
                    | INTEGER                           # lineNumber
                    | END                               # end
                    ;