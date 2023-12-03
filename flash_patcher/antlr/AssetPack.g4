grammar AssetPack;

// PARSER RULES ----
addAssetBlock   : ADD_ASSET local=file_name swf=file_name;
root            : (addAssetBlock)*;

file_name       : FILE_NAME;

// LEXER RULES ----
ADD_ASSET   : A D D '-' A S S E T;
FILE_NAME   : (FILE_NAME_CHARACTER_NO_SPACE+);
