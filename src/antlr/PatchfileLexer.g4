lexer grammar PatchfileLexer;

ADD             : A D D;
REMOVE          : R E M O V E;

// file names should always start with DefineSprite or frame
// XML files should be named swf.xml
// (we need this to avoid ADD and REMOVE being matched in the filename)
FILENAME        : (D E F I N E S P R I T E | F R A M E) .+? '.as' | S W F '.xml';

BEGIN_PATCH     : B E G I N '-' P A T C H -> mode(ADD_BLOCK_MODE);
NUMBER_RANGE    : INTEGER '-' INTEGER;
FILE_ADD_TOKEN  : INTEGER | E N D;

// We cannot use the common.g4 file, since modes don't play nice with it
// (This is also why Patchfile needs a separate lexer file)
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
fragment SLASH      : '/'|'\\';

INTEGER : NUMBER+;

// Stuff to ignore, like comments or whitespace
WHITESPACE  : [ \t\r\n\f]+         -> skip;
COMMENT     : '#' ~( '\r' | '\n')* -> skip;

mode ADD_BLOCK_MODE;
END_PATCH   : E N D '-' P A T C H -> mode(DEFAULT_MODE);
AS_TEXT     : .+?;