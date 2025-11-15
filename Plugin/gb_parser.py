import re
from typing import List, Dict, Any, Optional, Tuple

# Token types
TOKEN_VAR = 'VAR'
TOKEN_DEF = 'DEF'
TOKEN_IF = 'IF'
TOKEN_ELIF = 'ELIF'
TOKEN_ELSE = 'ELSE'
TOKEN_THEN = 'THEN'
TOKEN_END = 'END'
TOKEN_LOOP = 'LOOP'
TOKEN_TIMES = 'TIMES'
TOKEN_RETURN = 'RETURN'
TOKEN_WINDOW = 'WINDOW'
TOKEN_BUTTON = 'BUTTON'
TOKEN_INPUT = 'INPUT'
TOKEN_TEXT = 'TEXT'
TOKEN_CONTAINER = 'CONTAINER'
TOKEN_TS_WINDOWS = 'TS_WINDOWS'
TOKEN_TSDLL = 'TSDLL'
TOKEN_STRING = 'STRING'
TOKEN_NUMBER = 'NUMBER'
TOKEN_BOOLEAN = 'BOOLEAN'
TOKEN_IDENTIFIER = 'IDENTIFIER'
TOKEN_EQUALS = 'EQUALS'
TOKEN_PLUS = 'PLUS'
TOKEN_MINUS = 'MINUS'
TOKEN_MULTIPLY = 'MULTIPLY'
TOKEN_DIVIDE = 'DIVIDE'
TOKEN_LPAREN = 'LPAREN'
TOKEN_RPAREN = 'RPAREN'
TOKEN_COMMA = 'COMMA'
TOKEN_COLON = 'COLON'
TOKEN_SEMICOLON = 'SEMICOLON'
TOKEN_TITLE = 'TITLE'
TOKEN_TEXT_ARG = 'TEXT_ARG'
TOKEN_COMMENT = 'COMMENT'
TOKEN_EOF = 'EOF'

class Token:
    def __init__(self, type: str, value: str, line: int, column: int):
        self.type = type
        self.value = value
        self.line = line
        self.column = column
    
    def __str__(self):
        return f'Token({self.type}, {repr(self.value)}, line={self.line}, col={self.column})'

class Lexer:
    def __init__(self, text: str):
        self.text = text
        self.pos = 0
        self.line = 1
        self.column = 1
        self.current_char = self.text[self.pos] if self.pos < len(self.text) else None
    
    def error(self, message: str = None):
        if message is None:
            message = f"Invalid character: '{self.current_char}'"
        raise SyntaxError(f"Error at line {self.line}, column {self.column}: {message}")
    
    def advance(self):
        self.pos += 1
        self.column += 1
        if self.pos < len(self.text):
            self.current_char = self.text[self.pos]
            if self.current_char == '\n':
                self.line += 1
                self.column = 1
        else:
            self.current_char = None
    
    def skip_whitespace(self):
        while self.current_char is not None and self.current_char.isspace():
            self.advance()
    
    def skip_comment(self):
        if self.current_char == '/' and self.pos + 1 < len(self.text) and self.text[self.pos + 1] == '/':
            while self.current_char is not None and self.current_char != '\n':
                self.advance()
            return True
        return False
    
    def number(self):
        result = ''
        while self.current_char is not None and (self.current_char.isdigit() or self.current_char == '.'):
            result += self.current_char
            self.advance()
        
        try:
            if '.' in result:
                return float(result)
            else:
                return int(result)
        except ValueError:
            self.error(f"Invalid number format: {result}")
    
    def string(self):
        result = ''
        if self.current_char == '"':
            self.advance()  # Skip the opening quote
            while self.current_char is not None and self.current_char != '"':
                if self.current_char == '\\':
                    self.advance()  # Skip the escape character
                    if self.current_char == '"':
                        result += '"'
                    elif self.current_char == '\\':
                        result += '\\'
                    else:
                        result += '\\' + self.current_char
                else:
                    result += self.current_char
                self.advance()
            
            if self.current_char == '"':
                self.advance()  # Skip the closing quote
                return result
            else:
                self.error("Unterminated string")
    
    def title_text_format(self):
        # Handle title'value' or text'value' format
        prefix = ''
        if self.current_char == 't':
            self.advance()
            if self.current_char == 'i':
                self.advance()
                if self.current_char == 't':
                    self.advance()
                    if self.current_char == 'l':
                        self.advance()
                        if self.current_char == 'e':
                            self.advance()
                            prefix = 'text'
                elif self.current_char == 't':
                    self.advance()
                    if self.current_char == 'l':
                        self.advance()
                        prefix = 'title'
        
        if prefix and self.current_char == "'":
            token_type = TOKEN_TITLE if prefix == 'title' else TOKEN_TEXT_ARG
            self.advance()  # Skip the quote
            value = ''
            while self.current_char is not None and self.current_char != "'":
                value += self.current_char
                self.advance()
            if self.current_char == "'":
                self.advance()  # Skip the closing quote
                return token_type, value
            else:
                self.error(f"Unterminated {prefix} string")
        
        # If we didn't match title'value' or text'value', put the characters back
        self.pos -= len(prefix)
        self.column -= len(prefix)
        self.current_char = self.text[self.pos] if self.pos < len(self.text) else None
        return None
    
    def identifier(self):
        result = ''
        while self.current_char is not None and (self.current_char.isalnum() or self.current_char == '_'):
            result += self.current_char
            self.advance()
        
        # Check for keywords
        keywords = {
            'var': TOKEN_VAR,
            'def': TOKEN_DEF,
            'if': TOKEN_IF,
            'elif': TOKEN_ELIF,
            'else': TOKEN_ELSE,
            'then': TOKEN_THEN,
            'end': TOKEN_END,
            'loop': TOKEN_LOOP,
            'times': TOKEN_TIMES,
            'return': TOKEN_RETURN,
            'window': TOKEN_WINDOW,
            'button': TOKEN_BUTTON,
            'input': TOKEN_INPUT,
            'text': TOKEN_TEXT,
            'container': TOKEN_CONTAINER,
            'true': TOKEN_BOOLEAN,
            'false': TOKEN_BOOLEAN,
        }
        
        # Check for special functions
        if result == 'ts' and self.current_char == '.':
            self.advance()  # Skip the dot
            func_name = ''
            while self.current_char is not None and (self.current_char.isalnum() or self.current_char == '_'):
                func_name += self.current_char
                self.advance()
            if func_name == 'windows':
                return TOKEN_TS_WINDOWS
            # If not a recognized function, put the characters back
            self.pos -= len(func_name) + 1  # +1 for the dot
            self.column -= len(func_name) + 1
            self.current_char = self.text[self.pos] if self.pos < len(self.text) else None
        
        if result == 'tsdll':
            return TOKEN_TSDLL
        
        return keywords.get(result, TOKEN_IDENTIFIER), result
    
    def get_next_token(self):
        while self.current_char is not None:
            if self.skip_comment():
                self.skip_whitespace()
                continue
                
            if self.current_char.isspace():
                self.skip_whitespace()
                continue
            
            # Check for title'value' or text'value' format
            title_text_result = self.title_text_format()
            if title_text_result:
                token_type, value = title_text_result
                return Token(token_type, value, self.line, self.column - len(value) - 2)  # -2 for quotes
            
            if self.current_char.isalpha() or self.current_char == '_':
                token_type, value = self.identifier()
                return Token(token_type, value, self.line, self.column - len(value))
            
            if self.current_char.isdigit() or self.current_char == '.':
                value = self.number()
                return Token(TOKEN_NUMBER, value, self.line, self.column - len(str(value)))
            
            if self.current_char == '"':
                value = self.string()
                return Token(TOKEN_STRING, value, self.line, self.column - len(value) - 2)  # -2 for quotes
            
            if self.current_char == '=':
                self.advance()
                return Token(TOKEN_EQUALS, '=', self.line, self.column - 1)
            
            if self.current_char == '+':
                self.advance()
                return Token(TOKEN_PLUS, '+', self.line, self.column - 1)
            
            if self.current_char == '-':
                self.advance()
                return Token(TOKEN_MINUS, '-', self.line, self.column - 1)
            
            if self.current_char == '*':
                self.advance()
                return Token(TOKEN_MULTIPLY, '*', self.line, self.column - 1)
            
            if self.current_char == '/':
                self.advance()
                return Token(TOKEN_DIVIDE, '/', self.line, self.column - 1)
            
            if self.current_char == '(':
                self.advance()
                return Token(TOKEN_LPAREN, '(', self.line, self.column - 1)
            
            if self.current_char == ')':
                self.advance()
                return Token(TOKEN_RPAREN, ')', self.line, self.column - 1)
            
            if self.current_char == ',':
                self.advance()
                return Token(TOKEN_COMMA, ',', self.line, self.column - 1)
            
            if self.current_char == ':':
                self.advance()
                return Token(TOKEN_COLON, ':', self.line, self.column - 1)
            
            if self.current_char == ';':
                self.advance()
                return Token(TOKEN_SEMICOLON, ';', self.line, self.column - 1)
            
            self.error()
        
        return Token(TOKEN_EOF, None, self.line, self.column)

# AST node classes
class AST:
    pass

class VarDeclaration(AST):
    def __init__(self, name: str, value: AST):
        self.name = name
        self.value = value

class DefDeclaration(AST):
    def __init__(self, name: str, value: AST):
        self.name = name
        self.value = value

class FunctionDef(AST):
    def __init__(self, name: str, params: List[str], body: List[AST]):
        self.name = name
        self.params = params
        self.body = body

class ReturnStatement(AST):
    def __init__(self, value: AST):
        self.value = value

class IfStatement(AST):
    def __init__(self, condition: AST, body: List[AST], elif_clauses: List[Tuple[AST, List[AST]]], else_body: List[AST]):
        self.condition = condition
        self.body = body
        self.elif_clauses = elif_clauses
        self.else_body = else_body

class LoopStatement(AST):
    def __init__(self, condition: AST, body: List[AST], is_times_loop: bool = False, times: Optional[AST] = None):
        self.condition = condition
        self.body = body
        self.is_times_loop = is_times_loop
        self.times = times

class BinaryOperation(AST):
    def __init__(self, left: AST, op: str, right: AST):
        self.left = left
        self.op = op
        self.right = right

class UnaryOperation(AST):
    def __init__(self, op: str, expr: AST):
        self.op = op
        self.expr = expr

class Number(AST):
    def __init__(self, value: float):
        self.value = value

class String(AST):
    def __init__(self, value: str):
        self.value = value

class Boolean(AST):
    def __init__(self, value: bool):
        self.value = value

class Identifier(AST):
    def __init__(self, name: str):
        self.name = name

class FunctionCall(AST):
    def __init__(self, name: str, args: List[AST]):
        self.name = name
        self.args = args

class TSWindowsCall(AST):
    def __init__(self, title: str, text: str):
        self.title = title
        self.text = text

class TSDLLCall(AST):
    def __init__(self, dll_name: str, function_name: str, args: List[AST]):
        self.dll_name = dll_name
        self.function_name = function_name
        self.args = args

class Window(AST):
    def __init__(self, title: str, width: AST, height: AST, children: List[AST]):
        self.title = title
        self.width = width
        self.height = height
        self.children = children

class Button(AST):
    def __init__(self, text: str, event_handler: List[AST]):
        self.text = text
        self.event_handler = event_handler

class Input(AST):
    def __init__(self, name: str, default_value: str):
        self.name = name
        self.default_value = default_value

class TextElement(AST):
    def __init__(self, text: str):
        self.text = text

class Container(AST):
    def __init__(self, children: List[AST]):
        self.children = children

class Parser:
    def __init__(self, lexer: Lexer):
        self.lexer = lexer
        self.current_token = self.lexer.get_next_token()
    
    def error(self, message: str = None):
        if message is None:
            message = f"Syntax error at {self.current_token}"
        raise SyntaxError(message)
    
    def eat(self, token_type: str):
        if self.current_token.type == token_type:
            self.current_token = self.lexer.get_next_token()
        else:
            self.error(f"Expected {token_type}, got {self.current_token.type}")
    
    def factor(self):
        token = self.current_token
        
        if token.type == TOKEN_NUMBER:
            self.eat(TOKEN_NUMBER)
            return Number(token.value)
        
        if token.type == TOKEN_STRING:
            self.eat(TOKEN_STRING)
            return String(token.value)
        
        if token.type == TOKEN_BOOLEAN:
            self.eat(TOKEN_BOOLEAN)
            return Boolean(token.value == 'true')
        
        if token.type == TOKEN_IDENTIFIER:
            self.eat(TOKEN_IDENTIFIER)
            
            # Check if it's a function call
            if self.current_token.type == TOKEN_LPAREN:
                self.eat(TOKEN_LPAREN)
                args = []
                if self.current_token.type != TOKEN_RPAREN:
                    args.append(self.expr())
                    while self.current_token.type == TOKEN_COMMA:
                        self.eat(TOKEN_COMMA)
                        args.append(self.expr())
                self.eat(TOKEN_RPAREN)
                return FunctionCall(token.value, args)
            
            return Identifier(token.value)
        
        if token.type == TOKEN_LPAREN:
            self.eat(TOKEN_LPAREN)
            node = self.expr()
            self.eat(TOKEN_RPAREN)
            return node
        
        if token.type == TOKEN_PLUS or token.type == TOKEN_MINUS:
            op = token.type
            self.eat(op)
            return UnaryOperation(op, self.factor())
        
        self.error()
    
    def term(self):
        node = self.factor()
        
        while self.current_token.type in (TOKEN_MULTIPLY, TOKEN_DIVIDE):
            token = self.current_token
            if token.type == TOKEN_MULTIPLY:
                self.eat(TOKEN_MULTIPLY)
            elif token.type == TOKEN_DIVIDE:
                self.eat(TOKEN_DIVIDE)
            
            node = BinaryOperation(left=node, op=token.type, right=self.factor())
        
        return node
    
    def expr(self):
        node = self.term()
        
        while self.current_token.type in (TOKEN_PLUS, TOKEN_MINUS):
            token = self.current_token
            if token.type == TOKEN_PLUS:
                self.eat(TOKEN_PLUS)
            elif token.type == TOKEN_MINUS:
                self.eat(TOKEN_MINUS)
            
            node = BinaryOperation(left=node, op=token.type, right=self.term())
        
        return node
    
    def var_declaration(self):
        self.eat(TOKEN_VAR)
        var_name = self.current_token.value
        self.eat(TOKEN_IDENTIFIER)
        self.eat(TOKEN_EQUALS)
        expr = self.expr()
        return VarDeclaration(var_name, expr)
    
    def def_declaration(self):
        self.eat(TOKEN_DEF)
        
        # Check if it's a function definition
        if self.current_token.type == TOKEN_IDENTIFIER and self.lexer.text[self.lexer.pos:self.lexer.pos+1] == '(':
            func_name = self.current_token.value
            self.eat(TOKEN_IDENTIFIER)
            self.eat(TOKEN_LPAREN)
            params = []
            if self.current_token.type != TOKEN_RPAREN:
                params.append(self.current_token.value)
                self.eat(TOKEN_IDENTIFIER)
                while self.current_token.type == TOKEN_COMMA:
                    self.eat(TOKEN_COMMA)
                    params.append(self.current_token.value)
                    self.eat(TOKEN_IDENTIFIER)
            self.eat(TOKEN_RPAREN)
            
            # Parse function body
            body = []
            while self.current_token.type != TOKEN_END:
                body.append(self.statement())
            self.eat(TOKEN_END)
            
            return FunctionDef(func_name, params, body)
        
        # Otherwise it's a simple definition
        def_name = self.current_token.value
        self.eat(TOKEN_IDENTIFIER)
        self.eat(TOKEN_EQUALS)
        expr = self.expr()
        return DefDeclaration(def_name, expr)
    
    def return_statement(self):
        self.eat(TOKEN_RETURN)
        expr = self.expr()
        return ReturnStatement(expr)
    
    def if_statement(self):
        self.eat(TOKEN_IF)
        condition = self.expr()
        self.eat(TOKEN_THEN)
        
        # Parse if body
        if_body = []
        while self.current_token.type not in (TOKEN_ELIF, TOKEN_ELSE, TOKEN_END):
            if_body.append(self.statement())
        
        # Parse elif clauses
        elif_clauses = []
        while self.current_token.type == TOKEN_ELIF:
            self.eat(TOKEN_ELIF)
            elif_condition = self.expr()
            self.eat(TOKEN_THEN)
            
            elif_body = []
            while self.current_token.type not in (TOKEN_ELIF, TOKEN_ELSE, TOKEN_END):
                elif_body.append(self.statement())
            
            elif_clauses.append((elif_condition, elif_body))
        
        # Parse else body
        else_body = []
        if self.current_token.type == TOKEN_ELSE:
            self.eat(TOKEN_ELSE)
            while self.current_token.type != TOKEN_END:
                else_body.append(self.statement())
        
        self.eat(TOKEN_END)
        
        return IfStatement(condition, if_body, elif_clauses, else_body)
    
    def loop_statement(self):
        self.eat(TOKEN_LOOP)
        
        # Check if it's a times loop
        if self.current_token.type == TOKEN_TIMES:
            self.eat(TOKEN_TIMES)
            times = self.expr()
            self.eat(TOKEN_THEN)
            
            body = []
            while self.current_token.type != TOKEN_END:
                body.append(self.statement())
            self.eat(TOKEN_END)
            
            return LoopStatement(None, body, is_times_loop=True, times=times)
        
        # Otherwise it's a condition loop
        condition = self.expr()
        self.eat(TOKEN_THEN)
        
        body = []
        while self.current_token.type != TOKEN_END:
            body.append(self.statement())
        self.eat(TOKEN_END)
        
        return LoopStatement(condition, body)
    
    def ts_windows_call(self):
        self.eat(TOKEN_TS_WINDOWS)
        self.eat(TOKEN_LPAREN)
        
        # Parse title parameter
        if self.current_token.type != TOKEN_TITLE:
            self.error("Expected title parameter in ts.windows call")
        title = self.current_token.value
        self.eat(TOKEN_TITLE)
        
        # Parse comma
        self.eat(TOKEN_COMMA)
        
        # Parse text parameter
        if self.current_token.type != TOKEN_TEXT_ARG:
            self.error("Expected text parameter in ts.windows call")
        text_content = self.current_token.value
        self.eat(TOKEN_TEXT_ARG)
        
        self.eat(TOKEN_RPAREN)
        
        return TSWindowsCall(title, text_content)
    
    def tsdll_call(self):
        self.eat(TOKEN_TSDLL)
        self.eat(TOKEN_LPAREN)
        
        # Parse DLL name
        if self.current_token.type != TOKEN_STRING:
            self.error("Expected DLL name as string")
        dll_name = self.current_token.value
        self.eat(TOKEN_STRING)
        self.eat(TOKEN_COMMA)
        
        # Parse function name
        if self.current_token.type != TOKEN_STRING:
            self.error("Expected function name as string")
        function_name = self.current_token.value
        self.eat(TOKEN_STRING)
        
        # Parse arguments
        args = []
        while self.current_token.type != TOKEN_RPAREN:
            self.eat(TOKEN_COMMA)
            args.append(self.expr())
        
        self.eat(TOKEN_RPAREN)
        
        return TSDLLCall(dll_name, function_name, args)
    
    def gui_element(self):
        if self.current_token.type == TOKEN_WINDOW:
            return self.window_element()
        elif self.current_token.type == TOKEN_BUTTON:
            return self.button_element()
        elif self.current_token.type == TOKEN_INPUT:
            return self.input_element()
        elif self.current_token.type == TOKEN_TEXT:
            return self.text_element()
        elif self.current_token.type == TOKEN_CONTAINER:
            return self.container_element()
        
        self.error("Expected GUI element")
    
    def window_element(self):
        self.eat(TOKEN_WINDOW)
        
        if self.current_token.type != TOKEN_STRING:
            self.error("Expected window title as string")
        title = self.current_token.value
        self.eat(TOKEN_STRING)
        
        width = self.expr()
        height = self.expr()
        
        # Parse child elements
        children = []
        while self.current_token.type != TOKEN_END:
            children.append(self.gui_element())
        
        self.eat(TOKEN_END)
        
        return Window(title, width, height, children)
    
    def button_element(self):
        self.eat(TOKEN_BUTTON)
        
        if self.current_token.type != TOKEN_STRING:
            self.error("Expected button text as string")
        text = self.current_token.value
        self.eat(TOKEN_STRING)
        
        # Parse event handler name (optional)
        event_handler = []
        if self.current_token.type == TOKEN_IDENTIFIER:
            self.eat(TOKEN_IDENTIFIER)
            
            # Parse event handler body
            while self.current_token.type != TOKEN_END:
                event_handler.append(self.statement())
            
            self.eat(TOKEN_END)
        
        return Button(text, event_handler)
    
    def input_element(self):
        self.eat(TOKEN_INPUT)
        
        if self.current_token.type != TOKEN_STRING:
            self.error("Expected input name as string")
        name = self.current_token.value
        self.eat(TOKEN_STRING)
        
        if self.current_token.type != TOKEN_STRING:
            self.error("Expected default value as string")
        default_value = self.current_token.value
        self.eat(TOKEN_STRING)
        
        return Input(name, default_value)
    
    def text_element(self):
        self.eat(TOKEN_TEXT)
        
        if self.current_token.type != TOKEN_STRING:
            self.error("Expected text content as string")
        text_content = self.current_token.value
        self.eat(TOKEN_STRING)
        
        return TextElement(text_content)
    
    def container_element(self):
        self.eat(TOKEN_CONTAINER)
        
        # Parse child elements
        children = []
        while self.current_token.type != TOKEN_END:
            children.append(self.gui_element())
        
        self.eat(TOKEN_END)
        
        return Container(children)
    
    def statement(self):
        if self.current_token.type == TOKEN_VAR:
            return self.var_declaration()
        elif self.current_token.type == TOKEN_DEF:
            return self.def_declaration()
        elif self.current_token.type == TOKEN_IF:
            return self.if_statement()
        elif self.current_token.type == TOKEN_LOOP:
            return self.loop_statement()
        elif self.current_token.type == TOKEN_RETURN:
            return self.return_statement()
        elif self.current_token.type == TOKEN_TS_WINDOWS:
            return self.ts_windows_call()
        elif self.current_token.type == TOKEN_TSDLL:
            return self.tsdll_call()
        elif self.current_token.type in (TOKEN_WINDOW, TOKEN_BUTTON, TOKEN_INPUT, TOKEN_TEXT, TOKEN_CONTAINER):
            return self.gui_element()
        else:
            # It might be a function call or expression
            return self.expr()
    
    def parse(self):
        program = []
        while self.current_token.type != TOKEN_EOF:
            program.append(self.statement())
        return program

def parse_gb_code(code: str) -> List[AST]:
    """
    Parse GB language code into an AST.
    """
    lexer = Lexer(code)
    parser = Parser(lexer)
    return parser.parse()

def validate_gb_code(code: str) -> Tuple[bool, List[str]]:
    """
    Validate GB language code and return any errors.
    """
    errors = []
    try:
        parse_gb_code(code)
        return True, errors
    except SyntaxError as e:
        errors.append(str(e))
        return False, errors

# Example usage
if __name__ == "__main__":
    # Example GB code
    example_code = '''
    // Variable declarations
    var age = 25
    var name = "John"
    var isStudent = true
    
    // Definitions
    def PI = 3.14159
    
    // Function definition
    def add(a, b)
        return a + b
    end
    
    // If statement
    if age > 18 then
        var status = "Adult"
    else
        var status = "Minor"
    end
    
    // Loop
    loop i = 0; i < 10; i = i + 1 then
        // Do something
    end
    
    // Windows API call
    ts.windows(title'Greeting', text'Hello, World!')
    
    // GUI window
    window "My Application" 800 600
        text "Welcome to GB Language"
        button "Click Me" onClick
            ts.windows(title'Button Clicked', text'You clicked the button!')
        end
        input "Username" ""
    end
    '''
    
    try:
        # Parse the example code
        ast = parse_gb_code(example_code)
        print("Parsing successful!")
        # You would typically process the AST here
    except Exception as e:
        print(f"Parsing error: {e}")