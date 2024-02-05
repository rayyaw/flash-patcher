grammar Stagefile;

// PARSER RULES ----
patchFile       : PATCH_FILE;
pythonFile      : PYTHON_FILE;
root            : (patchFile | pythonFile)*;


// LEXER RULES ----
PATCH_FILE          : FILE_NAME_CHARACTER+ ('.patch' | '.assets');
PYTHON_FILE         : FILE_NAME_CHARACTER+ '.py';
