grammar Patchfile;

// PARSER RULES ----
addBlockHeader    : ADD FILENAME FILE_ADD_TOKEN;
addBlock           : add_block_header+ BEGIN_PATCH AS_TEXT END_PATCH;

removeBlock        : REMOVE FILENAME NUMBER_RANGE;

// LEXER RULES ----
ADD             : A D D;
REMOVE          : R E M O V E;

END             : E N D;

FILENAME        : (FILE_NAME_CHARACTER | SPACE)+ '.as';

BEGIN_PATCH     : B E G I N '-' P A T C H;
END_PATCH       : E N D '-' P A T C H;

NUMBER_RANGE    : INTEGER '-' INTEGER;
FILE_ADD_TOKEN  : INTEGER | END;
