grammar Stagefile;

// PARSER RULES ----
patchFile       : PATCH_FILE;
pythonFile      : PYTHON_FILE;
assetPackFile   : ASSET_PACK_FILE;
root            : (patchFile | pythonFile | assetPackFile)*;


// LEXER RULES ----
PATCH_FILE          : FILE_NAME_CHARACTER+ '.patch';
PYTHON_FILE         : FILE_NAME_CHARACTER+ '.py';
ASSET_PACK_FILE     : FILE_NAME_CHARACTER+ '.assets';
