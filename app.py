from flask import Flask, request, render_template
import re

app = Flask(__name__)

# Analizador Léxico
def lexical_analysis(code):
    tokens = []
    errors = []
    token_specification = [
        ('CLASS', r'\bclass\b'),
        ('PUBLIC', r'\bpublic\b'),
        ('STATIC', r'\bstatic\b'),
        ('VOID', r'\bvoid\b'),
        ('MAIN', r'\bmain\b'),
        ('STRING', r'\bString\b'),
        ('FOR', r'\bfor\b'),
        ('INT', r'\bint\b'),
        ('PRINTLN', r'\bSystem\.out\.println\b'),
        ('NUMBER', r'\b\d+\b'),
        ('ID', r'\b[a-zA-Z_]\w*\b'),
        ('OP', r'[+\-*/]'),
        ('RELOP', r'[<>]=?|==|!='),
        ('ASSIGN', r'='),
        ('END', r';'),
        ('LPAREN', r'\('),
        ('RPAREN', r'\)'),
        ('LBRACE', r'{'),
        ('RBRACE', r'}'),
        ('LBRACKET', r'\['),  # Agregar corchete izquierdo
        ('RBRACKET', r'\]'),  # Agregar corchete derecho
        ('STRING_LITERAL', r'"(?:\\.|[^"\\])*"'),
        ('SKIP', r'[ \t\r\n]+'),  # Saltar espacios, tabs y nuevas líneas
        ('MISMATCH', r'.')  # Cualquier otro carácter
    ]
    tok_regex = '|'.join('(?P<%s>%s)' % pair for pair in token_specification)
    line_num = 1
    line_start = 0

    for mo in re.finditer(tok_regex, code):
        kind = mo.lastgroup
        value = mo.group()
        column = mo.start() - line_start
        if kind == 'NUMBER':
            value = int(value)
        elif kind == 'SKIP':
            if '\n' in value:
                line_num += value.count('\n')
                line_start = mo.end()
            continue
        elif kind == 'MISMATCH':
            errors.append(f'Error léxico: {value!r} inesperado en la línea {line_num}, columna {column}')
            continue

        tokens.append((kind, value, line_num, column))

    return tokens, errors

# Analizador Sintáctico
def syntax_analysis(tokens):
    errors = []
    balance = 0

    for i, token in enumerate(tokens):
        if token[0] == 'CLASS':
            if i == 0 or tokens[i - 1][0] != 'PUBLIC':
                errors.append(f'Error sintáctico: Se esperaba "public" antes de "class" en la línea {token[2]}, columna {token[3]}')
        if token[0] == 'LBRACE':
            balance += 1
        elif token[0] == 'RBRACE':
            balance -= 1
        if balance < 0:
            errors.append(f'Error sintáctico: Llave de cierre inesperada en la línea {token[2]}, columna {token[3]}')
            balance = 0

    if balance > 0:
        errors.append('Error sintáctico: Falta(n) llave(s) de cierre')

    return errors

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        code = request.form['code']
        tokens, lex_errors = lexical_analysis(code)
        syn_errors = syntax_analysis(tokens)
        errors = lex_errors + syn_errors
        return render_template('index.html', tokens=tokens, errors=errors, code=code)
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
