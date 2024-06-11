import sys
import ply.yacc as yacc
from analex import tokens
import re

"""

GIC = <T,N,S,P>

S - Options 

Options - Expression 
        | Function 

Function -  Options COLON ID Options SEMICOLON 
           
Expression - Options Token 
           | & 
           
Token      - Operation 
           | Quickie 
           | Misk 
           | Manuver 
           | Logic 
           | Loop 
           | Condition 
           | Variables 
           | Elem 
           | Io            
           
Operation - ADD 
          | MUL 
          | DIV 
          | SUB 
          | EXP
          | MOD
          | DIVMOD

Loop | DO Options  LOOP
     | BEGIN Options UNTIL
     | BEGIN Options WHILE Options REPEAT
     | I
     | DO Options PLUSLOOP

Condition - IF Options  ELSE Options THEN
          | IF Options  THEN

Quickie - QUICKADDONE 
        | QUICKADDTWO 
        | QUICKSUBONE 
        | QUICKSUBTWO 
        | QUICKMULTWO 
        | QUICKDIVTWO 

Logic - EQUAL
      | NOTEQUAL 
      | GREATER 
      | LESS 
      | ZEROEQUALS 
      | ZEROLESS 
      | ZEROGREATER 
      | FALSE 
      | TRUE 

Misk - ABS
     | NEGATE 
     | MIN
     | MAX

Elem - NUMBER 
     | STRING 

Manuver - DUP
        | 2DUP
        | SWAP 
        | ROT
        | OVER
        | DROP

Io - DOT
   | KEY
   | CHAR
   | CR 
   | SPACE 
   | SPACES
   | EMIT
      

Variables - VARIABLE ID
          | ID EXCLAMATION
          | ID ATSIGN
          | ID QUESTIONMARK
          | ID


"""

macro = {} #key = id, value = (string,nºcall,contains?)
errors = []

def no_dash(func):
    func = re.sub('-', '',func)
    return func

def re_label(body, num, id):
    patterns = [r'(LOOPLABEL)',r'(ELSE)',r'(ENDIF)']
    for pattern in patterns:
        body = re.sub(pattern, lambda match: id + str(num) +  match.group(1), body)
    return body

def contains(func_body):
    pattern = r'\bENDIF || \bLOOPLABEL'
    
    if re.match(pattern, func_body):
        return 1
    else:
        return 0
    
def bad_loop_var(body):
    pattern = r'loopvar'
    
    if re.search(pattern,body):
        return True
    else:
        return False
    
def handle_loop_var(loop, v):
    pattern1 = r'loopvar'
    
    body = re.sub(pattern1, "pushg " + str(v), loop)
    return body
    
def p_s1(p):
    """
    S     : Options 
    """
    p[0] = ''
    if bad_loop_var(p[1]):
        parser.exito = False
        errors.append(f"\tError: Bad usage of I =>\n")
        p[0] = '\n'
    if parser.exito:
        for i in range(parser.var_counter):
            p[0] += "pushi 0\n"
        p[0] += 'START\n' + p[1] + 'STOP\n'

    return p
    

def p_options1(p):
    """
    Options     : Expression 
    """
    p[0] = p[1]
    return p

def p_options2(p):
    """
    Options     : Function 
    """
    p[0] = p[1]
    return p

def p_function1(p):
    """
    Function    : Options COLON ID Options  SEMICOLON
    """
    if macro.get(p[3]):
        parser.exito = False
        errors.append(f"\tError detected in line {p.lineno(3)}, position {p.lexpos(3)}: Function redefinition => {p[3]}\n")
    else:
        macro[p[3]] = (p[4],0,contains(p[4]))

    p[0] = p[1]
    return p

def p_expression1(p):
    """
    Expression  : Options Token 
    """
    p[0] = p[1] + p[2]
    #print(p[0], end='')
    return p

def p_expression2(p):
    """
    Expression  : 
    """
    p[0] = ''
    return p

def p_token1(p):
    """
    Token  : Operation
           | Quickie
           | Misk
           | Manuver
           | Logic
           | Loop
           | Condition
           | Variables
           | Elem
           | Io
    """
    p[0] = p[1]
    return p

def p_operations1(p):
    """        
    Operation : PLUS
    """
    p[0] = 'ADD\n'
    return p

def p_operations2(p):
    """        
    Operation : TIMES
    """
    p[0] = "MUL\n"
    return p

def p_operations3(p):
    """        
    Operation : DIVIDE
    """
    p[0] = "DIV\n"
    return p

def p_operations4(p):
    """        
    Operation : MINUS
    """
    p[0] = "SUB\n"
    return p

def p_operations5(p):
    """        
    Operation : EXP
    """
    v = parser.var_counter
    parser.var_counter += 2

    p[0] =  "storeg " + str(v) + "\nDUP 1\nstoreg" + (str(v+1)) + "\nLOOPLABEL" + str(parser.loop_label) + ":\npushg "+ str(v+1) + "\nMUL\npushg  " + str(v) + "\npushi 1\nSUB\nDUP 1\nstoreg " + str(v) + "\npushi 1\nEQUAL\njz LOOPLABEL" + str(parser.loop_label) + "\n"
    parser.loop_label += 1
    
    return p

def p_operations6(p):
    """
    Operation : MOD 
    """
    p[0] = "MOD\n"
    return p

def p_operations7(p):
    """
    Operation : DIVMOD 
    """
    v = parser.var_counter
    parser.var_counter += 1
    
    p[0] = "pushsp\nLOAD -1\npushsp\nLOAD -1\nMOD\nstoreg " + str(v) + "\nSWAP\npushg " + str(v) + "\nSWAP\nstoreg " + str(v) + "\nSWAP\npushg " + str(v) + "\nSWAP\nDIV\n"
    return p
    
def p_loop1(p):
    """
    Loop        : DO Options LOOP 
    """
    v = parser.var_counter
    parser.var_counter += 2
    
    loop = "storeg " + str(v+1) + "\n" + "storeg " + str(v) + "\n" + "LOOPLABEL" + str(parser.loop_label) + ":\n" + p[2] + "pushg "+ str(v+1) + "\npushi 1\nADD\nDUP 1\nstoreg " + str(v+1) + "\npushg " + str(v) + "\nSUPEQ\njz LOOPLABEL" + str(parser.loop_label) + "\n"

    p[0] =  handle_loop_var(loop, v+1)
    parser.loop_label += 1
    return p

def p_loop2(p):
    """
    Loop        : BEGIN Options UNTIL 
    """

    p[0] = "LOOPLABEL" + str(parser.loop_label) + ":\n" + p[2] + "jz LOOPLABEL" + str(parser.loop_label) + "\n"
    parser.loop_label += 1
    return p

def p_loop3(p):
    """
    Loop        : BEGIN Options WHILE Options REPEAT 
    """
    p[0] = "LOOPLABEL" + str(parser.loop_label) + ":\n" + p[2] + "pushi 0\nEQUAL\nNOT\njz LOOPLABEL" + str(parser.loop_label + 1) + "\n" + p[4] + "jump LOOPLABEL" + str(parser.loop_label) + "\nLOOPLABEL" + str(parser.loop_label + 1) + ":\n"
    parser.loop_label += 2
    return p

def p_loop4(p):
    """
    Loop    : I
    """

    p[0] = "loopvar\n"
    return p

def p_loop5(p):
    """
    Loop        : DO Options PLUSLOOP 
    """
    v = parser.var_counter
    parser.var_counter += 2
    
    loop = "storeg " + str(v+1) + "\n" + "storeg " + str(v) + "\n" + "LOOPLABEL" + str(parser.loop_label) + ":\n" + p[2] + "pushg "+ str(v+1) + "\nADD\nDUP 1\nstoreg " + str(v+1) + "\npushg " + str(v) + "\nSUPEQ\njz LOOPLABEL" + str(parser.loop_label) + "\n"

    p[0] =  handle_loop_var(loop, v+1)
    parser.loop_label += 1
    return p

def p_condition1(p):
    """
    Condition   : IF Options ELSE Options THEN 
    """
    c = parser.if_counter
    parser.if_counter += 1

    p[0] = "jz " + "ELSE" + str(c) + "\n" + p[2] + "jump ENDIF" + str(c) + "\n" + "ELSE" + str(c) + ":\n" + p[4] + "ENDIF" + str(c) + ":\n"
    return p

def p_condition2(p):
    """
    Condition   : IF Options THEN 
    """
    c = parser.if_counter
    parser.if_counter += 1

    p[0] = "jz " + "ENDIF" + str(c) + "\n" + p[2] + "ENDIF" + str(c) + ":\n"
    return p

def p_quickie1(p):
    """
    Quickie     : QUICKADDONE 
    """
    p[0] = "pushi 1\nADD\n"
    return p

def p_quickie2(p):
    """
    Quickie     : QUICKADDTWO 
    """
    p[0] = "pushi 2\nADD\n"
    return p

def p_quickie3(p):
    """
    Quickie     : QUICKSUBONE 
    """
    p[0] = "pushi 1\nSUB\n"
    return p

def p_quickie4(p):
    """
    Quickie     : QUICKSUBTWO 
    """
    p[0] = "pushi 2\nSUB\n"
    return p

def p_quickie5(p):
    """
    Quickie     : QUICKMULTWO 
    """
    p[0] = "pushi 2\nMUL\n"
    return p

def p_quickie6(p):
    """
    Quickie     : QUICKDIVTWO 
    """
    p[0] = "pushi 2\nDIV\n"
    return p

def p_logic1(p):
    """
    Logic       : EQUAL 
    """
    p[0] = "EQUAL\n"
    return p

def p_logic2(p):
    """
    Logic       : NOTEQUAL 
    """
    p[0] = "EQUAL\nNOT\n"
    return p

def p_logic3(p):
    """
    Logic       : GREATER 
    """
    p[0] = "SUP\n"
    return p

def p_logic4(p):
    """
    Logic       : LESS 
    """
    p[0] = "INF\n"
    return p

def p_logic5(p):
    """
    Logic       : ZEROEQUALS 
    """
    p[0] = "pushi 0\nEQUAL\n"
    return p

def p_logic6(p):
    """
    Logic       : ZEROLESS 
    """
    p[0] = "puchi 0\nINF\n"
    return p

def p_logic7(p):
    """
    Logic       : ZEROGREATER 
    """
    p[0] = "pushi 0\nSUP\n"
    return p

def p_logic8(p):
    """
    Logic       : FALSE
    """
    p[0] = "pushi 0\n"
    return p

def p_logic9(p):
    """ 
    Logic       : TRUE
    """
    p[0] = "pushi 1\n"
    return p

def p_misk1(p):
    """
    Misk        : ABS
    """
    c = parser.if_counter
    parser.if_counter += 1

    p[0] = "DUP 1\npushi 0\nINF\njz " + "ENDIF" + str(c) + "\npushi -1\nMUL\nENDIF" + str(c) + ":\n"
    return p

def p_misk2(p):
    """
    Misk        : NEGATE
    """
    p[0] = "pushi -1\nMUL\n"
    return p

def p_misk3(p):
    """
    Misk        : MIN
    """
    c = parser.if_counter
    parser.if_counter += 1

    p[0] = "pushsp\nLOAD -1\npushsp\nLOAD -1\nINF\njz " + "ELSE" + str(c) + "\nPOP 1\njump ENDIF" + str(c) + "\n" + "ELSE" + str(c) + ":\nSWAP\nPOP 1\nENDIF" + str(c) + ":\n"
    return p

def p_misk4(p):
    """
    Misk        : MAX
    """
    c = parser.if_counter
    parser.if_counter += 1

    p[0] = "pushsp\nLOAD -1\npushsp\nLOAD -1\nSUP\njz " + "ELSE" + str(c) + "\nPOP 1\njump ENDIF" + str(c) + "\n" + "ELSE" + str(c) + ":\nSWAP\nPOP 1\nENDIF" + str(c) + ":\n"
    return p

def p_manuver1(p):
    """
    Manuver      : DUP 
    """
    p[0] = "DUP 1\n"
    return p

def p_manuver2(p):
    """
    Manuver      : 2DUP 
    """
    p[0] = "pushsp\nLOAD -1\npushsp\nLOAD -1\n"
    return p

def p_manuver3(p):
    """
    Manuver      : SWAP 
    """
    p[0] = "SWAP\n"
    return p

def p_manuver4(p):
    """
    Manuver      : ROT 
    """
    
    v = parser.var_counter
    parser.var_counter += 1
    
    p[0] = "storeg " + str(v) + "\nSWAP\npushg " + str(v) + "\nSWAP\n"
    return p

def p_manuver5(p):
    """
    Manuver      : OVER 
    """
    p[0] = "pushsp\nload -1\n"
    return p

def p_manuver6(p):
    """
    Manuver      : DROP 
    """
    p[0] = "POP 1\n"
    return p


def p_variables1(p):
    """
    Variables    : VARIABLE ID 
    """
    if p[2] in parser.symbol_table:
        parser.exito = False
        errors.append(f"\tError detected in line {p.lineno(2)}, position {p.lexpos(2)}: Duplicate ID => {p[2]}\n")
        p[0] = '\n'
    else:
        print(p[2])
        parser.symbol_table[p[2]] = (parser.var_counter,1)
        parser.var_counter += 1
        p[0] = ""
    return p


def p_variables2(p):
    """
    Variables    : ID EXCLAMATION 
    """
    if p[1] not in parser.symbol_table:
        parser.exito = False
        errors.append(f"\tError detected in line {p.lineno(1)}, position {p.lexpos(1)}: Unknown ID => {p[1]}\n")
        p[0] = '\n'
    else:
        pos,t = parser.symbol_table[p[1]]
        p[0] = "storeg " + str(pos) + "\n"
    return p
    

def p_variables3(p):
    """
    Variables    : ID ATSIGN 
    """
    if p[1] not in parser.symbol_table:
        parser.exito = False
        errors.append(f"\tError detected in line {p.lineno(1)}, position {p.lexpos(1)}: Unknown ID => {p[1]}\n")
        p[0] = '\n'
    else:
        pos,t = parser.symbol_table[p[1]]
        p[0] = "pushg " + str(pos) + "\n"
    
    return p

def p_variables4(p):
    """
    Variables    : ID QUESTIONMARK 
    """
    if p[1] not in parser.symbol_table:
        parser.exito = False
        errors.append(f"\tError detected in line {p.lineno(1)}, position {p.lexpos(1)}: Unknown ID => {p[1]}\n")
        p[0] = '\n'
    else:
        pos,t = parser.symbol_table[p[1]]
        p[0] = "pushg " + str(pos) + "\n" + "writei\n"
        
    
    return p

def p_variables5(p):
    """
    Variables    : ID 
    """

    if macro.get(p[1]):
        m1, m2, m3 = macro[p[1]]
        m2 += 1
        if m2 == 1 or m3:
            m1_new = re_label(m1, m2, no_dash(p[1]))
        macro[p[1]] = (m1, m2, m3)
        p[0] = m1_new
    else:
        parser.exito = False
        parser.detected_error = 1
        errors.append(f"\tError detected in line {p.lineno(1)}, position {p.lexpos(1)}: Unknown ID => {p[1]}\n")
        p[0] = '\n'
    return p

def p_io1(p):
    """
    Io           : DOT
    """
    p[0] = "writei\n"
    return p

def p_io2(p):
    """
    Io           : KEY
    """
    p[0] = "READ\nCHRCODE\n"
    return p

def p_io3(p):
    """
    Io           : CHAR
    """
    p[0] = f'pushs"{p[1]}"\nCHRCODE\n'
    return p

def p_io4(p):
    """
    Io           : CR
    """
    p[0] = "WRITELN\n"
    return p

def p_io5(p):
    """
    Io           : SPACE
    """
    p[0] = 'pushs" "\nwrites\n'
    return p

def p_io6(p):
    """
    Io           : SPACES
    """
    v = parser.var_counter
    parser.var_counter += 1
    space = 'pushs" "\nwrites\n'
    p[0] =  "pushi 0\nSUB\n" + "storeg " + str(v) + "\n" + "LOOPLABEL" + str(parser.loop_label) + ":\n" + space + "pushg "+ str(v) + "\npushi 1\nSUB\nDUP 1\nstoreg " + str(v) + "\npushi 0\nEQUAL\njz LOOPLABEL" + str(parser.loop_label) + "\n"
    parser.loop_label += 1
    return p

def p_io7(p):
    """
    Io           : EMIT
    """
    p[0] = "WRITECHR\n"
    return p
    

def p_elem1(p):
    """
    Elem         : NUMBER
    """
    p[0] = "pushi " + str(p[1]) + "\n"
    return p

def p_elem2(p):
    """
    Elem         : STRING
    """
    p[0] = "pushs" + '"' + p[1] + '"\n' + "writes\n"
    return p

def p_error(p):
    parser.exito = False
    errors.append(f"\tSyntactic error detected => Bad use of reserved words\n")

        
parser = yacc.yacc()
parser.exito = True
parser.if_counter = 1
parser.var_counter = 0
parser.loop_label = 0
parser.symbol_table = {} # id qual pointer tamanho
parser.called_func = {} # id de função - número atual de label utilizada
       
def main():
    if len(sys.argv) > 1:
        print("Uso: python analsyn.py")
        sys.exit(1)

    data = ''
    for line in sys.stdin:
        data += line

    result = parser.parse(data)
    if parser.exito:
        print("Parsing successful.")
        with open("target_file.txt", 'w') as target_file:
            target_file.write(result)
            print(f"Result written to target_file.txt")
    else: 
        print("Parsing unsuccessful.")
        with open("error_file.txt", 'w') as error_file:
            out = f"{len(errors)} ERROR(S) FOUND:\n\n"
            for error in errors:
                out += error
            error_file.write(out)
            print(f"Result written to error_file.txt")

if __name__ == "__main__":
    main()