grammar AssetPack;

// PARSER RULES ----
addAssetBlock   : ADD_ASSET local=FILE_NAME swf=FILE_NAME;
root            : (addAssetBlock)*;

// LEXER RULES ----
FILE_NAME   : FILE_NAME_CHARACTER+;
ADD_ASSET   : A D D '-' A S S E T;

// FIXME - Move this to a common lexer section
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

fragment FILE_NAME_CHARACTER : LETTER | NUMBER | SPACE | SLASH | DASH;