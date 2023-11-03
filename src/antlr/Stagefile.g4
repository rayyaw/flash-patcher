grammar Stagefile;

// PARSER RULES ----
patchFile       : PATCH_FILE;
assetPackFile   : ASSET_PACK_FILE;
root            : (patchFile | assetPackFile)*;


// LEXER RULES ----
PATCH_FILE          : FILE_NAME_CHARACTER+ '.patch';
ASSET_PACK_FILE     : FILE_NAME_CHARACTER+ '.assets';
