parser grammar PatchfileParser;

options {tokenVocab=PatchfileLexer;}

addBlockHeader      : ADD FILENAME locationToken;
addBlock            : addBlockHeader+ BEGIN_PATCH addBlockText END_PATCH;
addBlockText        : AS_TEXT+;

removeBlock         : REMOVE FILENAME locationToken DASH locationToken;

replaceNthBlock     : REPLACE FILENAME INTEGER BEGIN_CONTENT replaceBlockText END_CONTENT 
                        BEGIN_PATCH addBlockText END_PATCH;
replaceAllBlock     : REPLACE_ALL FILENAME BEGIN_CONTENT replaceBlockText END_CONTENT 
                        BEGIN_PATCH addBlockText END_PATCH;
replaceBlockText    : AS_TEXT+;

root                : (addBlock | removeBlock | replaceNthBlock | replaceAllBlock)*;

locationToken       : OPEN_BLOCK? FUNCTION FUNCTION_NAME INTEGER? CLOSE_BLOCK?  # function
                    | INTEGER                                                   # lineNumber
                    | END                                                       # end
                    ;