parser grammar PatchfileParser;

options {tokenVocab=PatchfileLexer;}

addBlockHeader          : ADD source=file_name locationToken;
addBlock                : addBlockHeader+ BEGIN_PATCH addBlockText END_PATCH;
addBlockText            : AS_TEXT+;

addAssetBlock           : ADD_ASSET local=file_name swf=file_name;

removeBlock             : REMOVE source=file_name locationToken DASH locationToken;

replaceNthBlockHeader   : REPLACE source=file_name locationToken;
replaceNthBlock         : replaceNthBlockHeader+ BEGIN_CONTENT replaceBlockText END_CONTENT BEGIN_PATCH addBlockText END_PATCH;

replaceAllBlockHeader   : REPLACE_ALL source=file_name;
replaceAllBlock         : replaceAllBlockHeader+ BEGIN_CONTENT replaceBlockText END_CONTENT BEGIN_PATCH addBlockText END_PATCH;
replaceBlockText        : CONTENT_TEXT+;

varValue                : TEXT_BLOCK | QUOTED_TEXT | INTEGER;
setVarBlock             : SET_VAR var_name=TEXT_BLOCK EQUALS varValue;
exportVarBlock          : EXPORT_VAR var_name=TEXT_BLOCK EQUALS varValue;

execPatcherBlock        : EXEC_PATCHER file_name;
execPythonBlock         : EXEC_PYTHON file_name;

root                    : (
                            addBlock            |
                            addAssetBlock       |
                            removeBlock         |
                            replaceNthBlock     |
                            replaceAllBlock     |

                            setVarBlock         |
                            exportVarBlock      |

                            execPatcherBlock    |
                            execPythonBlock     
                        )*;

locationToken           : OPEN_BLOCK? FUNCTION TEXT_BLOCK INTEGER? CLOSE_BLOCK?      # function
                        | BEGIN_CONTENT replaceBlockText END_CONTENT (PLUS INTEGER)?    # text
                        | INTEGER                                                       # lineNumber
                        | END                                                           # end
                        ;

file_name               : TEXT_BLOCK | QUOTED_TEXT;
