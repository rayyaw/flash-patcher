lexer grammar PatchfileLexer;

ADD             : A D D;
ADD_ASSET       : A D D '-' A S S E T;
REMOVE          : R E M O V E;
REPLACE         : R E P L A C E;
REPLACE_ALL     : R E P L A C E '-' A L L;
SET_VAR         : S E T '-' V A R;
EXPORT_VAR      : E X P O R T '-' V A R;
EXEC_PATCHER    : A P P L Y '-' P A T C H;
EXEC_PYTHON     : E X E C '-' P Y T H O N;

// file names should always start with DefineSprite or frame
// XML files should be named swf.xml
// (we need this to avoid ADD and REMOVE being matched in the filename)
FILENAME            : (D E F I N E S P R I T E | F R A M E) .+? '.as' | S W F '.xml';

BEGIN_PATCH     : B E G I N '-' P A T C H -> mode(ADD_BLOCK_MODE);
BEGIN_CONTENT   : B E G I N '-' C O N T E N T -> mode(CONTENT_MODE);

FUNCTION        : F U N C T I O N;
END             : E N D;

OPEN_BLOCK      : '(';
CLOSE_BLOCK     : ')';

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
fragment DOT        : '.';

INTEGER : NUMBER+;
DASH    : '-';
PLUS    : '+';
EQUALS  : '=';

TEXT_BLOCK  : ~( '-' | '=' | ' ' | '\r' | '\n')+;

// Stuff to ignore, like comments or whitespace
WHITESPACE  : [ \t\r\n\f]+         -> skip;
COMMENT     : '#' ~( '\r' | '\n')* -> skip;

mode ADD_BLOCK_MODE;
END_PATCH   : E N D '-' P A T C H -> mode(DEFAULT_MODE);
AS_TEXT     : .+?;

mode CONTENT_MODE;
END_CONTENT : E N D '-' C O N T E N T -> mode(DEFAULT_MODE);
CONTENT_TEXT: .+?;