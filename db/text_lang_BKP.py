from lark import Lark, Transformer

class TextLang:
    def __init__(self):
        self.parser = Lark(r"""
            start: (latex | RAW_STRING)*        
            latex: "$$" content "$$" | "$" content "$"
            content: text_string | bracketing | operation | variable | integer_const
            operation: binary | unary
            binary: commutative | noncommutative
            unary: "-" content
            commutative: add_sub | addition
            addition: content "+" content
            add_sub: content "+"|"-" content
            noncommutative: concat | multiply | fraction
            concat: content content
            multiply: content multiply_op content
            multiply_op: CDOT | TIMES | ASTERISK
            fraction: fraction_op "{" content "}" "{" content "}"
            fraction_op: "\dfrac" | "\frac"
            bracketing: parenth | curly_braces | sq_bracket
            parenth: LPAREN content RPAREN
            sq_bracket: "[" content "]"
            curly_braces: "\\{" content "\\}"
            text_string: text_commands "{" text_content "}"
            text_commands: "\\textbf" | "\\text" 
            variable: (styled_var | var_content) prime_ticks?
            styled_var: (mathfrak | mathscr) LBRACE var_content prime_ticks? RBRACE
            var_content: GREEK_LETTER | LATIN_LETTER
            prime_ticks: PRIME+
            text_content: (NAME | "-")+
            integer_const: INT
            mathscr: "\\mathscr"
            mathfrak: "\\mathfrak"
            RAW_STRING: /[^\$]+/
            PRIME: /'/
            LATIN_LETTER: /[a-zA-Z]/
            GREEK_LETTER: /\\alpha|\\beta|\\gamma|\\delta/
            LBRACE: /{/
            RBRACE: /}/
            LPAREN: /\(/
            RPAREN: /\)/
            CDOT: /\\cdot/
            TIMES: /\\times/
            ASTERISK: /\*/
            %import common.INT
            %import python.NAME
            %import common.WS
            %ignore WS
        """, parser='lalr')
        
        
class SetOfAllVariables(Transformer):
    LATIN_LETTER = str
    var_content = ''.join
    
    def __init__(self, variables: set, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._variables:set = variables
        
    @property
    def set_of_variables(self) -> set:
        return self._variables
    
    def variable(self, tree):
        print('Variable: ', tree)
        var = tree[0]
        self._variables.add(var)
        return var
    
        
class SyntacticStandardForm(Transformer):
    INT = int
    LATIN_LETTER = str
    PRIME = str
    ASTERISK = str
    CDOT = str
    TIMES = str
    variable = ''.join
    var_content = ''.join
    styled_var = ''.join
    addition = '+'.join
    commutative = ''.join
    binary = ''.join
    operation = ''.join
    noncommutative = ''.join
    multiply = ''.join
    content = ''.join
    multiply_op = ''.join
    parenth = ''.join
    content = ''.join
    bracketing = ''.join
    concat = ''.join
    
    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)
        self.prime_tick_count = 0
         
    def start(self, tree):
        return tree[0]
    
    def mathscr(self, tree):
        return r"\mathscr"
    
    def mathfrak(self, tree):
        return r"\mathfrak"
    
    def variable(self, tree):
        tree = ''.join(tree) + "'" * self.prime_tick_count
        self.prime_tick_count = 0
        return tree

    def latex(self, tree):
        return tree
    
    def prime_ticks(self, tree):
        self.prime_tick_count += len(tree)
        return ''    
    
    
if __name__ == '__main__':
    language = TextLang()
    #xformer = SyntacticStandardForm()
    variables = set()
    xformer = SetOfAllVariables(variables)
    
    while True:
        i = input("(╯‵□′)╯︵┻━┻ ")
        tree = language.parser.parse(i)
        print('Tree: ', tree)
        result = xformer.transform(tree)
        print('Result: ', result)
        print('Variables: ', variables)
   
    #language = TextLang()
    #xformer = SyntacticStandardForm()
    
    #while True:
        #i = input("(╯‵□′)╯︵┻━┻ ")
        #tree = language.parser.parse(i)
        #print('Tree: ', tree)
        #result = xformer.transform(tree)
        #print('Result: ', result)
