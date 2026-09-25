# Analisador Léxico com Lark
## Cupom Fiscal Eletrônico

**Autores:**
- Isaac Takebayashi
- Gustavo Marques
- Harry Daniel
- Wellington Junior

Projeto acadêmico de Compiladores — implementação de um **analisador léxico** para o domínio de Cupom Fiscal Eletrônico, utilizando Python e a biblioteca [Lark](https://github.com/lark-parser/lark).

---

## 1. Objetivo

Construir um **analisador léxico** capaz de receber um texto simulando um cupom fiscal e transformá-lo em uma sequência de tokens identificados com tipo, lexema, linha, coluna, posição inicial e posição final. O projeto demonstra os conceitos fundamentais de análise léxica:

- Token, Lexema e Padrão
- Tokens por string literal e por expressão regular
- Palavras reservadas case-insensitive com fronteira de palavra
- Prioridade de tokens para resolver conflitos
- `%ignore` para comentários e espaços
- `UnexpectedCharacters` para erros léxicos com linha e coluna
- `start_pos` e `end_pos` para localização de tokens
- Interface interativa com `Textarea`, `Button`, `Output` e `on_click`
- Diferença entre erro léxico e regra de negócio

---

## 2. Token, Lexema e Padrão

Estes são os três conceitos fundamentais de qualquer analisador léxico:

### TOKEN
É a **categoria** ou **classificação** que o analisador atribui a um trecho do texto. O token é um nome simbólico — não é o texto em si.

Exemplo:
```
ITEM   MONEY   CNPJ   INTEGER   COLON
```

### LEXEMA
É o **texto exatamente encontrado na entrada** que foi reconhecido como pertencente a um token. É a instância concreta do token.

Exemplos:
```
"ITEM"         →  lexema do token ITEM
"R$ 27,90"     →  lexema do token MONEY
"28/07/2026"   →  lexema do token DATE
"2"            →  lexema do token INTEGER
```

### PADRÃO
É a **regra / expressão regular** usada para reconhecer o lexema. É a definição do token na gramática.

Exemplos do projeto:
```
Token ITEM  → padrão: /ITEM\b/i          (string reservada, case-insensitive)
Token MONEY → padrão: /R\$\s*\d{1,3}(?:\.\d{3})*,\d{2}/
Token CNPJ  → padrão: /\d{2}\.\d{3}\.\d{3}\/\d{4}-\d{2}/
Token COLON → padrão: ":"                (string literal, não regex)
```

### Tabela resumo

| TOKEN | LEXEMA (exemplo) | PADRÃO |
|---|---|---|
| ITEM | `ITEM` | `/ITEM\b/i` |
| MONEY | `R$ 27,90` | `/R\$\s*\d{1,3}(?:\.\d{3})*,\d{2}/` |
| CNPJ | `12.345.678/0001-90` | `/\d{2}\.\d{3}\.\d{3}\/\d{4}-\d{2}/` |
| DATE | `28/07/2026` | `/\d{2}\/\d{2}\/\d{4}/` |
| COLON | `:` | `":"` (literal) |
| INTEGER | `2` | `/\d+/` |

---

## 3. Tecnologias Utilizadas

| Tecnologia | Versão | Uso |
|---|---|---|
| Python | 3.10+ | Linguagem principal |
| Lark | ≥ 1.1.0 | Motor do analisador léxico |
| ipywidgets | ≥ 8.0.0 | Interface interativa |
| JupyterLab | ≥ 4.0.0 | Ambiente de execução da interface |

---

## 4. Requisitos

- Python 3.10, 3.11 ou 3.12
- pip

---

## 5. Instalação

```bash
cd analisador_lexico_cupom
pip install -r requirements.txt
```

---

## 6. Como Executar

### Testes automatizados (terminal)
```bash
python tests.py
```

### Interface interativa (Jupyter)
```bash
jupyter lab
```
No notebook:
```python
import app
app.iniciar()
```

### Uso direto em Python
```python
from lexer import CupomLexer

lexer = CupomLexer()
tokens, erro = lexer.analisar('ITEM: "Arroz 5kg" QTD: 2 VL: R$ 27,90')

if erro:
    print(lexer.formatar_erro_texto(erro))
else:
    for tok in tokens:
        print(f"{tok.tipo:<12} {tok.lexema!r:<20} L{tok.linha}:C{tok.coluna} [{tok.start_pos}:{tok.end_pos}]")
```

---

## 7. Estrutura do Projeto

```
analisador_lexico_cupom/
├── grammar.lark          ← Gramática com todos os tokens
├── lexer.py              ← CupomLexer: tokenização e erros
├── app.py                ← Interface ipywidgets
├── tests.py              ← 15 casos de teste automatizados
├── requirements.txt
├── README.md
└── exemplos/
    ├── valido_01.txt … valido_03.txt
    └── invalido_01.txt … invalido_02.txt
```

---

## 8. Tabela de Tokens

| Token | Categoria | Tipo de definição | Regex / Literal | Prioridade | Exemplo |
|---|---|---|---|---|---|
| ITEM | Palavra reservada | Regex + flag /i + \b | `/ITEM\b/i` | .2 | `ITEM`, `item`, `ItEm` |
| QTD | Palavra reservada | Regex + flag /i + \b | `/QTD\b/i` | .2 | `QTD`, `qtd` |
| UN | Palavra reservada | Regex + flag /i + \b | `/UN\b/i` | .2 | `UN`, `un` |
| VL | Palavra reservada | Regex + flag /i + \b | `/VL\b/i` | .2 | `VL`, `vl` |
| DATA | Palavra reservada | Regex + flag /i + \b | `/DATA\b/i` | .2 | `DATA`, `data` |
| TOTAL | Palavra reservada | Regex + flag /i + \b | `/TOTAL\b/i` | .2 | `TOTAL` |
| SUBTOTAL | Palavra reservada | Regex + flag /i + \b | `/SUBTOTAL\b/i` | .2 | `SUBTOTAL` |
| DESCONTO | Palavra reservada | Regex + flag /i + \b | `/DESCONTO\b/i` | .2 | `DESCONTO` |
| CNPJ | Token de domínio | Expressão regular | `/\d{2}\.\d{3}\.\d{3}\/\d{4}-\d{2}/` | .3 | `12.345.678/0001-90` |
| CPF | Token de domínio | Expressão regular | `/\d{3}\.\d{3}\.\d{3}-\d{2}/` | .3 | `123.456.789-09` |
| DATE | Token de domínio | Expressão regular | `/\d{2}\/\d{2}\/\d{4}/` | .3 | `28/07/2026` |
| MONEY | Token de domínio | Expressão regular | `/R\$\s*\d{1,3}(?:\.\d{3})*,\d{2}/` | .3 | `R$ 27,90` |
| STRING | Literal | Expressão regular | `/"[^"]*"/` | padrão | `"Arroz 5kg"` |
| DECIMAL | Literal numérico | Expressão regular | `/\d+\.\d+/` | .1 | `10.50` |
| INTEGER | Literal numérico | Expressão regular | `/\d+/` | padrão | `2` |
| ID | Identificador | Expressão regular | `/[A-Za-z_][A-Za-z0-9_]*/` | .0 (padrão) | `produto` |
| COLON | Símbolo | **String literal** | `":"` | — | `:` |
| COMMA | Símbolo | **String literal** | `","` | — | `,` |
| LPAREN | Símbolo | **String literal** | `"("` | — | `(` |
| RPAREN | Símbolo | **String literal** | `")"` | — | `)` |
| SEMICOLON | Símbolo | **String literal** | `";"` | — | `;` |
| EQUALS | Símbolo | **String literal** | `"="` | — | `=` |
| PERCENT | Símbolo | **String literal** | `"%"` | — | `%` |
| ASTERISK | Símbolo | **String literal** | `"*"` | — | `*` |

**Total: 24 tipos de token.**

---

## 9. Token por String Literal vs Token por Regex

O Lark permite definir tokens de duas formas:

### String Literal
O token é reconhecido quando o texto é **exatamente** aquele caractere.
Não usa expressão regular.

```lark
COLON: ":"     ← token COLON = exatamente o caractere ":"
COMMA: ","
LPAREN: "("
```

### Expressão Regular
O token é reconhecido quando o texto **casa com o padrão**.

```lark
INTEGER: /\d+/              ← qualquer sequência de dígitos
CNPJ.3: /\d{2}\.\d{3}.../ ← padrão específico de CNPJ
ITEM.2: /ITEM\b/i          ← palavra ITEM, case-insensitive, com fronteira
```

A diferença é clara no código: símbolos usam aspas duplas `"..."`;
padrões variáveis usam barras `/regex/`.

---

## 10. Palavras Reservadas

### Flag `/i` — case-insensitive

A flag `/i` após a regex torna o reconhecimento **insensível a maiúsculas/minúsculas**.

```lark
KW_ITEM.2: /ITEM\b/i
```

O Lark converte internamente `/ITEM\b/i` para `(?i:ITEM\b)`, que é uma flag
**localizada no grupo** — compatível com Python 3.6+. Aceita:

| Entrada | Token reconhecido |
|---|---|
| `ITEM` | ITEM |
| `item` | ITEM |
| `Item` | ITEM |
| `ItEm` | ITEM |

### Fronteira `\b` — word boundary

`\b` é uma **asserção de fronteira de palavra**. Ela não consome caracteres —
apenas verifica se a posição atual está entre um caractere de palavra (`\w`)
e um não-palavra (ou início/fim do texto).

```lark
KW_ITEM.2: /ITEM\b/i
```

Com `\b`, o padrão exige que após `ITEM` **não haja** `[A-Za-z0-9_]`.

Resultados:
```
ITEM      →  ITEM   (após "M" vem fim de string: fronteira OK)
ITEM:     →  ITEM   (após "M" vem ":": não é palavra, fronteira OK)
ITEM 2    →  ITEM   (após "M" vem " ": não é palavra, fronteira OK)
ITEMIZADO →  ID     (após "M" vem "I": é palavra, \b falha → cai no ID)
```

---

## 11. Conflito de Prioridade

### Conflito 1: Palavras Reservadas × ID

**Problema:**
O token `ID` tem o padrão `/[A-Za-z_][A-Za-z0-9_]*/`, que casaria com `ITEM`,
`QTD`, `DATA` — reconhecendo-os como identificadores genéricos.

**Solução:**
As palavras reservadas recebem prioridade `.2`. O `ID` usa a prioridade padrão `.0`.

```lark
KW_ITEM.2: /ITEM\b/i    ← prioridade 2
ID:        /[A-Za-z_][A-Za-z0-9_]*/  ← prioridade 0 (padrão)
```

> "Quando duas regras podem reconhecer o mesmo trecho, a prioridade maior
> permite que a palavra reservada seja escolhida em vez do identificador genérico."

**Resultado:**
```
ITEM    → ITEM   (prioridade .2 vence sobre ID .0)
produto → ID     (não é palavra reservada)
```

### Conflito 2: DATE × INTEGER

**Problema:** `28/07/2026` contém dígitos que poderiam ser tokenizados como `INTEGER`.

**Solução:** `DATE.3` tem prioridade maior que `INTEGER` (padrão .0).
```
28/07/2026 → DATE  (um único token)
```

### Conflito 3: MONEY × Tokens genéricos

**Problema:** `R$ 27,90` poderia virar `ID(R)` + erro(`$`) + fragmentos.

**Solução:** `MONEY.3` tem a maior prioridade e sua regex captura o valor inteiro.
```
R$ 27,90 → MONEY  (um único token)
```

### Conflito 4: DECIMAL × INTEGER

**Problema:** `10.50` poderia ser tokenizado como `INTEGER(10)` + `.50`.

**Solução:** `DECIMAL.1` tem prioridade maior que `INTEGER` (padrão .0).
```
10.50 → DECIMAL  (um único token)
```

---

## 12. `%ignore` — Comentários e Espaços

### Espaços

```lark
%import common.WS
%ignore WS
```

`common.WS` é o terminal de espaço em branco da biblioteca Lark (`/\s+/`).
O `%ignore WS` descarta espaços, tabulações e quebras de linha entre tokens.
Eles **não aparecem na tabela de tokens**.

### Comentários

```lark
%ignore /#[^\n]*/
```

Qualquer texto iniciado por `#` até o fim da linha é descartado.

**Exemplo:**
```
# comentário do cupom
ITEM: "Arroz"   # outro comentário
```
Tokens gerados: `ITEM  COLON  STRING` — os comentários somem.

---

## 13. `UnexpectedCharacters` — Erros Léxicos

Quando o analisador encontra um caractere não reconhecido, o Lark lança
`UnexpectedCharacters`. O `CupomLexer` captura essa exceção **especificamente**:

```python
try:
    tokens = self._tokenizar(texto)
    return tokens, None
except UnexpectedCharacters as exc:
    # usa exc.line e exc.column para localizar o problema
    return [], self._formatar_erro_inesperado(exc, texto)
```

**Saída de erro:**
```
────────────────────────────────────────────────────
  ERRO LÉXICO
────────────────────────────────────────────────────
  Linha :  1
  Coluna:  15

  Caractere inesperado: '@'

  Dica:
  O símbolo "@" não é válido em cupons fiscais.
  Verifique se não há endereços de e-mail no texto.
────────────────────────────────────────────────────
```

---

## 14. `t.line`, `t.column`, `t.start_pos`, `t.end_pos`

O `CupomLexer` extrai **todos os quatro atributos** de cada token do Lark:

```python
def _converter_token(self, t: Token) -> TokenInfo:
    return TokenInfo(
        tipo=NOMES_TOKENS.get(t.type, t.type),
        lexema=str(t),
        linha=t.line,        # número da linha (base 1)
        coluna=t.column,     # número da coluna (base 1)
        start_pos=t.start_pos,  # posição inicial no texto (base 0)
        end_pos=t.end_pos,      # posição final no texto (base 0)
    )
```

**Exemplo para `ITEM: "Arroz"`:**
```
TOKEN   LEXEMA     LINHA  COL  START  END
ITEM    'ITEM'       1     1     0     4
COLON   ':'          1     5     4     5
STRING  '"Arroz"'    1     7     6    13
```

A interface exibe as colunas `INÍCIO` (start_pos) e `FIM` (end_pos).

---

## 15. Erro Léxico × Regra de Negócio

Esta é uma distinção fundamental em compiladores:

### Erro Léxico
O caractere ou sequência **não pertence a nenhum padrão** definido na gramática.
Detectado por `UnexpectedCharacters` do Lark.

```
ITEM: "Arroz" @ QTD: 2
                ↑ erro léxico: '@' não é um token válido
```

### Regra de Negócio
O token é **lexicamente válido**, mas o valor viola uma restrição do domínio.

```
QTD: -5           → '-' gera erro léxico (não é token)
QTD: 9999         → lexicamente válido (INTEGER); valor alto é regra de negócio
VL: R$ 99.999,99  → lexicamente válido (MONEY); limite de valor é regra de negócio
CNPJ inválido     → lexicamente válido (padrão numérico correto); validação
                    matemática do CNPJ é regra de negócio
```

> "O analisador léxico verifica se a sequência de caracteres pertence aos padrões
> definidos. Validações como quantidade positiva, valor mínimo, CNPJ válido
> matematicamente ou existência do produto na base de dados pertencem à camada
> de regras de negócio — não ao lexer."

---

## 16. Interface (app.py)

Implementa os componentes exigidos pelo checklist:

```python
# widgets.Textarea — área de entrada de texto
entrada = widgets.Textarea(...)

# widgets.Button — botão com on_click
botao_analisar = widgets.Button(description="🔍 Analisar", ...)
botao_limpar   = widgets.Button(description="🧹 Limpar", ...)

# widgets.Output — área de resultado
saida = widgets.Output(...)

# on_click — conexão do evento ao handler
botao_analisar.on_click(analisar_cupom)
botao_limpar.on_click(limpar_cupom)
```

A tabela de tokens exibe: `TOKEN | LEXEMA | LINHA | COLUNA | INÍCIO | FIM`.

---

## 17. Casos de Teste

### Válidos

**Caso 1 — Cupom com CNPJ:**
```
ITEM: "Arroz 5kg" / QTD: 2 / VL: R$ 27,90 / CNPJ: 12.345.678/0001-90 / DATA: 28/07/2026
```

**Caso 2 — CPF e valor com milhar:**
```
ITEM: "Notebook Lenovo" / QTD: 1 / VL: R$ 3.499,90 / CPF: 123.456.789-09 / DATA: 10/09/2026
```

**Caso 3 — Comentário ignorado:**
```
# Cupom de supermercado
ITEM: "Café 500g" / VL: R$ 18,50 / CNPJ: 98.765.432/0001-10
```

### Inválidos

**Caso 4:** `ITEM: "Arroz" @ QTD: 2` → detecta `@` na L1:C15

**Caso 5:** `ITEM: "Notebook" QTD: 1 $ VL: R$ 2.500,00` → detecta `$` isolado

---

## 18. Diário de Ambiguidade

### Ambiguidade 1: Palavras Reservadas × ID
Sem prioridade, `ITEM` seria `ID`. Resolvido com `KW_ITEM.2`.

### Ambiguidade 2: DATE × INTEGER
Sem prioridade, `28/07/2026` se fragmentaria. Resolvido com `DATE.3`.

### Ambiguidade 3: MONEY × Tokens genéricos
Sem prioridade, `R$ 3.499,90` se fragmentaria. Resolvido com `MONEY.3`.

### Ambiguidade 4: DECIMAL × INTEGER
Sem prioridade, `10.50` viraria `INTEGER(10)`. Resolvido com `DECIMAL.1`.

### Ambiguidade 5: DATA (reservada) × DATE (literal)
`DATA` = rótulo do campo (palavra reservada).
`28/07/2026` = valor da data (DATE literal).
Padrões distintos — não conflitam entre si.

---

## 19. Checklist de Autoavaliação

| Item | Implementado | Onde |
|---|---|---|
| Token, Lexema e Padrão documentados | **SIM** | README seção 2 |
| Token por string literal | **SIM** | `grammar.lark` — `COLON: ":"` etc. |
| Token por expressão regular | **SIM** | `grammar.lark` — CNPJ, CPF, DATE, MONEY, ID... |
| `%import common.WS` + `%ignore WS` | **SIM** | `grammar.lark` (final) |
| `%ignore /#[^\n]*/` (comentários) | **SIM** | `grammar.lark` (final) |
| Prioridade `TOKEN.2` explícita | **SIM** | `grammar.lark` — `KW_ITEM.2`, `KW_QTD.2`... |
| Fronteira `\b` | **SIM** | `grammar.lark` — `/ITEM\b/i` |
| Flag `/i` (case-insensitive) | **SIM** | `grammar.lark` — `/ITEM\b/i` |
| `UnexpectedCharacters` capturado | **SIM** | `lexer.py` — `except UnexpectedCharacters` |
| `exc.line` e `exc.column` no erro | **SIM** | `lexer.py` — `_formatar_erro_inesperado()` |
| `t.start_pos` e `t.end_pos` | **SIM** | `lexer.py` — `_converter_token()` |
| `widgets.Textarea` | **SIM** | `app.py` — `entrada = widgets.Textarea(...)` |
| `widgets.Button` | **SIM** | `app.py` — `botao_analisar = widgets.Button(...)` |
| `widgets.Output` | **SIM** | `app.py` — `saida = widgets.Output(...)` |
| `on_click` | **SIM** | `app.py` — `botao_analisar.on_click(analisar_cupom)` |
| Erro léxico × regra de negócio | **SIM** | README seção 15 + `lexer.py` docstring |

---

## 20. Conclusão

O projeto implementou um analisador léxico completo para Cupom Fiscal Eletrônico com Lark, demonstrando todos os conceitos fundamentais: tokens por literal e por regex, palavras reservadas com `/i` e `\b`, prioridade `.N` para resolver conflitos, `%ignore` para espaços e comentários, `UnexpectedCharacters` com linha/coluna, e `start_pos`/`end_pos` para localização precisa de tokens.
