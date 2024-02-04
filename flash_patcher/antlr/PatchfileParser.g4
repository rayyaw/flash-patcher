parser grammar PatchfileParser;

options {tokenVocab=PatchfileLexer;}

addBlockHeader          : ADD FILENAME locationToken;
addBlock                : addBlockHeader+ BEGIN_PATCH addBlockText END_PATCH;
addBlockText            : AS_TEXT+;

removeBlock             : REMOVE FILENAME locationToken DASH locationToken;

replaceNthBlockHeader   : REPLACE FILENAME locationToken;
replaceNthBlock         : replaceNthBlockHeader+ BEGIN_CONTENT replaceBlockText END_CONTENT BEGIN_PATCH addBlockText END_PATCH;

replaceAllBlockHeader   : REPLACE_ALL FILENAME;
replaceAllBlock         : replaceAllBlockHeader+ BEGIN_CONTENT replaceBlockText END_CONTENT BEGIN_PATCH addBlockText END_PATCH;
replaceBlockText        : CONTENT_TEXT+;

addAssetBlock           : ADD_ASSET local=file_name swf=file_name;

root                    : (
                            addBlock |
                            removeBlock |
                            replaceNthBlock |
                            replaceAllBlock |
                            addAssetBlock
                        )*;

locationToken           : OPEN_BLOCK? FUNCTION FUNCTION_NAME INTEGER? CLOSE_BLOCK?      # function
                        | BEGIN_CONTENT replaceBlockText END_CONTENT (PLUS INTEGER)?    # text
                        | INTEGER                                                       # lineNumber
                        | END                                                           # end
                        ;

file_name               : FUNCTION_NAME;