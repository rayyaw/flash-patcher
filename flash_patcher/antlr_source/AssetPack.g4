grammar AssetPack;

// PARSER RULES ----
addAssetBlock   : ADD_ASSET local=file_name swf=file_name;
root            : (addAssetBlock)*;

file_name       : FILE_NAME;

// LEXER RULES ----
ADD_ASSET   : A D D '-' A S S E T;
FILE_NAME   : (FILE_NAME_CHARACTER_NO_SPACE+);
fragment A : [aA];
fragment B : [bB];
fragment C : [cC];
fragment D : [dD];
fragment E : [eE];
fragment F : [fF];
fragment G : [gG];
fragment H : [hH];
fragment I : [iI];
fragment J : [jJ];
fragment K : [kK];
fragment L : [lL];
fragment M : [mM];
fragment N : [nN];
fragment O : [oO];
fragment P : [pP];
fragment Q : [qQ];
fragment R : [rR];
fragment S : [sS];
fragment T : [tT];
fragment U : [uU];
fragment V : [vV];
fragment W : [wW];
fragment X : [xX];
fragment Y : [yY];
fragment Z : [zZ];

fragment LETTER     : [A-Za-z];
fragment NUMBER     : [0-9];
fragment SPACE      : ' ';
fragment SLASH      : '/' | '\\';
fragment DASH       : '-' | '_';
fragment DOT        : '.';

fragment FILE_NAME_CHARACTER          : LETTER | NUMBER | SPACE | SLASH | DASH | DOT;
fragment FILE_NAME_CHARACTER_NO_SPACE : LETTER | NUMBER | SLASH | DASH | DOT;

// Stuff to ignore, like comments or whitespace
WHITESPACE  : [ \t\r\n\f]+         -> skip;
COMMENT     : '#' ~( '\r' | '\n')* -> skip;
