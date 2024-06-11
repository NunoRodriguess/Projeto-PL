# ------------------------------------------------------------
# calclex.py
#
# tokenizer for a simple expression evaluator for
# numbers and +,-,*,/
# ------------------------------------------------------------
import ply.lex as lex
import sys
# List of token names.   This is always required
tokens = [
   'NUMBER',
   'PLUS',
   'MINUS',
   'TIMES',
   'DIVIDE',
   'EXP',
   'LPAREN',
   'RPAREN',
   'DOT',
   'DIVMOD',
   'MOD',
   'MIN',
   'MAX',
   'ABS',
   'NEGATE',
   'QUICKADDONE',
   'QUICKADDTWO',
   'QUICKSUBONE',
   'QUICKSUBTWO',
   'QUICKMULTWO',
   'QUICKDIVTWO',
   'SEMICOLON',
   'COLON',
   'ID',
   'BEGINCOMMENT',
   'WHITESPACE',
   'NEWLINE'
]

logic_operands = [
    'EQUAL',
    'NOTEQUAL',
    'GREATER',
    'LESS',
    'ZEROEQUALS',
    'ZEROLESS',
    'ZEROGREATER',
    'INVERT',
    'FALSE',
    'TRUE'
]

string_operands = [
    
    'STRING',
    'KEY',
    'SPACE',
    'SPACES',
    'CHAR',
    'CR',
    'EMIT'
]

reserved_words = [
   'DUP',
   '2DUP',
   'SWAP',
   'OVER',
   'ROT',
   'DROP',
   'IF',
   'THEN',
   'ELSE',
   'DO',
   'LOOP',
   'PLUSLOOP',
   'BEGIN',
   'UNTIL',
   'WHILE',
   'REPEAT',
   'VARIABLE',
   'I'
]

variables_operands = [
    
    'ATSIGN',
    'EXCLAMATION',
    'QUESTIONMARK'
    
]

tokens = tokens + reserved_words + logic_operands + string_operands + variables_operands

tokens = tuple(i for i in tokens)

states = (
   ('insidecomment','exclusive'),
)

def t_insidecomment_RPAREN(t):
    r'\)[ ]*'
    t.lexer.begin('INITIAL')


def t_insidecomment_ignore_BEGINCOMMENT(t):
    r'[^\n)]'
    pass

t_insidecomment_ignore = ''

# Error handling rule
def t_insidecomment_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)

# Regular expression rules for the comment state
def t_WHITESPACE(t):
    r'[ ]+'
    
def t_ATSIGN(t):
    r'\@'    
    return t

def t_EXCLAMATION(t):
    r'\!'    
    return t

def t_QUESTIONMARK(t):
    r'\?'    
    return t 
    
def t_VARIABLE(t):
    r'(?i:variable)'    
    return t

def t_DO(t):
    r'(?i:do\b)'    
    return t

def t_PLUSLOOP(t):
    r'\+(?i:loop)'    
    return t

def t_LOOP(t):
    r'(?i:loop)'    
    return t

def t_BEGIN(t):
    r'(?i:begin)'
    return t

def t_UNTIL(t):
    r'(?i:until)'
    return t

def t_WHILE(t):
    r'(?i:while)'
    return t

def t_REPEAT(t):
    r'(?i:repeat)'
    return t

def t_IF(t):
    r'(?i:if)'    
    return t

def t_ELSE(t):
    r'(?i:else)'    
    return t

def t_THEN(t):
    r'(?i:then)'    
    return t

def t_SWAP(t):
    r'(?i:swap)'    
    return t

def t_DUP(t):
    r'(?i:dup)'    
    return t

def t_2DUP(t):
    r'2(?i:dup)'
    return t

def t_OVER(t):
    r'(?i:over)' 
    return t

def t_ROT(t):
    r'(?i:rot)' 
    return t

def t_DROP(t):
    r'(?i:drop)' 
    return t

def t_MIN(t):
    r'(?i:min)'    
    return t

def t_MAX(t):
    r'(?i:max)'    
    return t

def t_ABS(t):
    r'(?i:abs)'    
    return t

def t_NEGATE(t):
    r'(?i:negate)'    
    return t

# Palavras reservadas ficam em cima desta linha

def t_QUICKADDONE(t):
    r'1\+'    
    return t

def t_QUICKADDTWO(t):
    r'2\+'    
    return t

def t_QUICKSUBONE(t):
    r'1\-'    
    return t

def t_QUICKSUBTWO(t):
    r'2\-'    
    return t

def t_QUICKMULTWO(t):
    r'2\*'    
    return t

def t_QUICKDIVTWO(t):
    r'2\/'    
    return t

# Quickies em cima

def t_KEY(t):
    r'(?i:key)'    
    return t

def t_CHAR(t):
    r'(?i:char\s+\S+)'  
    t.value = t.value.split()[1][0]
    return t

def t_EMIT(t):
    r'(?i:emit)'    
    return t

def t_SPACES(t):
    r'(?i:spaces)'    
    return t

def t_SPACE(t):
    r'(?i:space)'    
    return t

def t_CR(t):
    r'(?i:cr)'    
    return t

def t_STRING(t):
    r'\."[ ][^"]*"'
    t.value = t.value.strip('."')
    t.value = t.value.strip(' ')
    return t
    

# String definiton em cima

def t_EQUAL(t):
    r'\='
    return t
def t_NOTEQUAL(t):
    r'\<\>'
    return t

def t_LESS(t):
    r'\<'
    return t

def t_GREATER(t):
    r'\>'
    return t

def t_ZEROEQUALS(t):
    r'\0\='
    return t

def t_ZEROLESS(t):
    r'\0\<'
    return t

def t_ZEROGREATER(t):
    r'\0\>'
    return t

def t_INVERT(t):
    r'(?i:invert)'
    return t

def t_TRUE(t):
    r'(?i:true)'
    return t

def t_FALSE(t):
    r'(?i:false)'
    return t
 
# Condições em cima

def t_DOT(t):
    r'\.'    
    return t

def t_NUMBER(t):
    r'[+\-]?\d+'
    t.value = int(t.value)    
    return t

def t_LPAREN(t):
    r'\( '
    t.lexer.begin('insidecomment')  
    
def t_SEMICOLON(t):
    r'\;'    
    return t

def t_COLON(t):
    r'\:'    
    return t

def t_PLUS(t):
    r'\+'
    return t

def t_MINUS(t):
    r'\-'    
    return t

def t_TIMES(t):
    r'\*'    
    return t

def t_DIVMOD(t):
    r'(?i:\/mod)'
    return t

def t_MOD(t):
    r'(?i:mod)'    
    return t

def t_DIVIDE(t):
    r'\/'    
    return t

def t_EXP(t):
    r'(?i:exp)'    
    return t

def t_I(t):
    r'(?i:i\b)'    
    return t 

def t_ID(t):
    r'[a-zA-Z_.(),{}+\-*\/][a-zA-Z_.(),{}1-9+\-*\/:;?]*'   
    return t 

def t_BEGINCOMMENT(t):
    r'\\.*' 

# Define a rule so we can track line numbers
def t_NEWLINE(t):
    r'\n+'
    t.lexer.lineno += len(t.value)


    
# A string containing ignored characters (spaces and tabs)
t_ignore  = '\t\r'

def t_error(t):
    line_number = t.lexer.lineno 
    illegal_char = t.value[0]
    print(f"Illegal character '{illegal_char}' at line {line_number}")
    exit(1)


lexer = lex.lex()

"""
for line in sys.stdin:
    #line = line.strip()
    lexer.input(line)
    for tok in lexer:
        print(tok)
        #print(tok.type, tok.value, tok.lineno, tok.lexpos)
    print("")
"""