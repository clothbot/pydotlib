# A Python based Liberty (dotlib) file lexer

import ply.lex as lex

reserved = {
    'library' : 'LIBRARY',
    'define' : 'DEFINE',
    'define_group' : 'DEFINE_GROUP',
    'cell' : 'CELL',
    'pin' : 'PIN',
    'bus' : 'BUS',
    'direction' : 'DIRECTION',
    'input' : 'IO_DIR',
    'output' : 'IO_DIR',
    'function' : 'FUNCTION',
    'ff' : 'FF',
    'latch' : 'LATCH',
    'statetable' : 'STATETABLE',
    'clocked_on' : 'CLOCKED_ON',
    'next_state' : 'NEXT_STATE',
    'enable' : 'ENABLE',
    'data_in' : 'DATA_IN',
    'clear' : 'CLEAR',
    'preset' : 'PRESET',
    'clear_preset_var1' : 'CLEAR_PRESET_VAR1',
    'clear_preset_var2' : 'CLEAR_PRESET_VAR2',
    'table' : 'TABLE',
}

tokens = [
    'PLUS', 'MINUS', 'MULT', 'DIV', 'EQ',
    'COMMA', 'SEMI', 'COLON',
    'LPAR', 'RPAR', 'LCURLY', 'RCURLY',
	'LSQR', 'RSQR',
    'NUM', 'STR', 'ID',
] + list(reserved.values())

def create_lexer():

    t_PLUS = r'\+'
    t_MINUS = r'-'
    t_MULT = r'\*'
    t_DIV = r'/'
    t_COMMA = r','
    t_SEMI = r';[ \t;]*'
    t_LPAR = r'\('
    t_RPAR = r'\)'
    t_LSQR = r'\['
    t_RSQR = r'\]'
    t_EQ = r'\='
    t_LCURLY = r'\{'
    t_RCURLY = r'\}[ \t]*;?'
    t_COLON = r'[ \t]?:'
    t_NUM = r'[-+]?([0-9]+\.?[0-9]*([Ee][-+]?[0-9]+)?|[0-9]*\.[0-9]*([Ee][-+]?[0-9]+)?)'

    def t_STR(t):
        r'"[^"]*"'
        t.value = t.value[1:-1]
        return t

    def t_ID(t):
        r'[a-zA-Z_][\w$]*[\']?|\\[\S]'
        t.type = reserved.get(t.value, 'ID')  # check for reserved words
        return t

    t_ignore = " \t\r"

    def t_ignore_COMMENT(t):
        r'/\*([^*]|\*+[^/*])*\*+/'
        pass

    # Define a rule to track line numbers (\n tokens otherwise discarded)
    def t_newline(t):
        r'\n+|\\\n+'
        t.lexer.lineno += len(t.value)

    # Error handling rule
    def t_error(t):
        print "Illegal character '", t.value[0], "' at", t.lexer.lineno
        t.lexer.skip(1)

    return lex.lex()


# A Python PLY based Liberty (dotlib) file parser

import ply.yacc as yacc

def create_parser():

	def p_library(t):
		'library : LIBRARY LPAR ID RPAR LCURLY attributes RCURLY'
		lib={}
		lib[t[1]]={}
		lib[t[1]][t[3]]=t[6]
		t[0] = lib
	
	def p_attributes(t):
		'attributes : attribute attributes'
		attrl=[]
		attrl.append(t[1])
		attrl.extend(t[2])
		t[0] = attrl

	def p_attributes_e(t):
		'attributes :'
		t[0] = []
	
	def p_attribute(t):
		'''attribute : simple_attribute
			| complex_attribute
			| named_attribute'''
		t[0] = t[1]
	
	def p_simple_attribute(t):
		'simple_attribute : ID COLON arg'
		attr={}
		attr[t[1]]=t[3]
		t[0] = attr
	
	def p_complex_attribute(t):
		'complex_attribute : ID LPAR arg args RPAR group_or_not'
		attr={}
		attr[t[1]]={}
		if t[3] != None:
			args=[t[3]]
			if t[4] != None:
				args.extend(t[4])
			attr[t[1]]['args']=args
		if t[6] != None:
			attr[t[1]]['children']=t[6]
		t[0] = attr
	
	def p_named_attribute_cell(t):
		'named_attribute : CELL LPAR ID RPAR LCURLY attributes RCURLY'
		attr={}
		attr['cell']={}
		attr['cell'][t[3]]=t[6]
		t[0] = attr

	def p_named_attribute_define(t):
		'named_attribute : DEFINE LPAR arg COMMA arg COMMA arg RPAR SEMI'
		attr={}
		attr['define']={}
		attr['define']['attribute_name']=t[3]
		attr['define']['group_name']=t[5]
		attr['define']['attribute_type']=t[7]
		t[0]=attr

	def p_named_attribute_bus(t):
		'named_attribute : BUS LPAR ID RPAR LCURLY attributes RCURLY'
		attr={}
		attr['bus']={}
		attr['bus']['name']=t[3]
		attr['bus']['children']=t[6]
		t[0] = attr

	def p_named_attribute_pin(t):
		'named_attribute : PIN LPAR pin_id RPAR LCURLY attributes RCURLY'
		attr={}
		attr['pin']={}
		pin_name=t[3][0]
		attr['pin']['name']=pin_name
		if len(t[3])>1 :
			pin_index=t[3][1]
			attr['pin']['index']=t[3][1]
		attr['pin']['children']=t[6]
		t[0] = attr

	def p_pin_id(t):
		'''pin_id : ID LSQR NUM RSQR
				| ID'''
		if len(t) > 2 :
			pin_name=[t[1],t[3]]
		else :
			pin_name=[t[1]]
		t[0]=pin_name

	def p_named_attribute_direction(t):
		'''named_attribute : DIRECTION COLON IO_DIR
						   | DIRECTION COLON IO_DIR SEMI'''
		t[0]={t[1] : t[3]}

	def p_arg(t):
		'''arg : argl
			| argl SEMI'''
		t[0] = t[1]
	
	def p_argl(t):
		'''argl : STR
			| NUM
			| ID
			| rhs_token'''
		t[0] = t[1]
	
	def p_rhs_token(t):
		'''rhs_token : FF
			| CLEAR
			| PRESET'''
		t[0] = t[1]
	
	def p_arg_e(t):
		'arg :'
		t[0] = None
	
	def p_args(t):
		'args : COMMA arg args'
		tl=[t[2]]
		if t[3] != None :
			tl.extend(t[3])
		t[0] = tl
	
	def p_args_e(t):
		'args :'
		t[0] = None

	def p_group_or_not_not(t):
		'group_or_not : SEMI'
		t[0] = None
	
	def p_group_or_not_group(t):
		'group_or_not : LCURLY attributes RCURLY'
		t[0] = t[2]


	def p_error(t):
		print "Syntax error at", t.value, "type", t.type, "on line", t.lexer.lineno
		import pdb; pdb.set_trace()
		yacc.errok()

	return yacc.yacc(tabmodule='pydotlib_parsetab')

# Encapsulation of lexer/parser pair
class PLYPair:
	def __init__(self, l=None, p=None):
		self.lexer = l
		self.parser = p
		self.result = None

	def set_lexer(self, l):
		self.lexer = l

	def set_parser(self, p):
		self.parser = p

	def parse_file(self, fname):
		f = open(fname, 'r')
		a = f.read()
		f.close()
		return self.parse(a)

	def parse(self, text):
		self.result = self.parser.parse(text, lexer=self.lexer)
		return self.result


