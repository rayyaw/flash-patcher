grammar AssetPack;

// PARSER RULES ----
addAssetBlock: ADD_ASSET local=FILE_NAME swf=FILE_NAME;

// LEXER RULES ----
FILE_NAME   : FILE_NAME_CHARACTER+;
ADD_ASSET   : A D D '-' A S S E T;
