grammar Stagefile;

// PARSER RULES ----
validFile: PATCH_FILE | ASSET_PACK_FILE;

// LEXER RULES ----
PATCH_FILE          : FILE_NAME_CHARACTER+ '.patch';
ASSET_PACK_FILE     : FILE_NAME_CHARACTER+ '.assets';
