// These fragments are common across all Patchfiles, and are split into a separate file.
// ANTLR does not support this, so we use `cat` to merge them when compiling the grammar.
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

fragment LETTER : [A-Za-z];
fragment NUMBER : [0-9];
fragment SPACE  : ' ';
fragment SLASH  : '/'|'\\';

fragment FILE_NAME_CHARACTER : LETTER | NUMBER | SLASH | '-' | '_';

fragment INTEGER : NUMBER+;
fragment TEXT    : .*?;

// Stuff to ignore, like comments or whitespace
WHITESPACE: [ \t\r\n\f]+         -> channel(HIDDEN);
COMMENT   : '#' ~( '\r' | '\n')* -> channel(HIDDEN);