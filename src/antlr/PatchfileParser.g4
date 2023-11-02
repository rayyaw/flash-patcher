parser grammar PatchfileParser;

options {tokenVocab=PatchfileLexer;}

addBlockHeader     : ADD FILENAME FILE_ADD_TOKEN;
addBlock           : addBlockHeader+ BEGIN_PATCH addBlockText END_PATCH;
addBlockText       : AS_TEXT+;

removeBlock        : REMOVE FILENAME NUMBER_RANGE;

root               : (addBlock | removeBlock)*;