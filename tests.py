"""
Testes automatizados — Analisador Léxico Cupom Fiscal Eletrônico.

Cobre os 5 casos obrigatórios do enunciado + testes do checklist
do professor (case-insensitive, fronteira \b, start_pos/end_pos,
%ignore, UnexpectedCharacters com linha e coluna).

Execute: python tests.py
"""

from __future__ import annotations

import sys
from lark.exceptions import UnexpectedCharacters
from lexer import CupomLexer, TokenInfo

# ============================================================
# Entradas de teste
# ============================================================

VALIDO_1 = """\
ITEM: "Arroz 5kg"
QTD: 2
UN: "UN"
VL: R$ 27,90
CNPJ: 12.345.678/0001-90
DATA: 28/07/2026
"""

VALIDO_2 = """\
ITEM: "Notebook Lenovo"
QTD: 1
UN: "UN"
VL: R$ 3.499,90
CPF: 123.456.789-09
DATA: 10/09/2026
"""

VALIDO_3 = """\
# Cupom de supermercado
ITEM: "Café 500g"
QTD: 3
UN: "UN"
VL: R$ 18,50
CNPJ: 98.765.432/0001-10
DATA: 15/09/2026
"""

INVALIDO_1 = 'ITEM: "Arroz" @ QTD: 2'
INVALIDO_2 = 'ITEM: "Notebook" QTD: 1 $ VL: R$ 2.500,00'


# ============================================================
# Infraestrutura de contagem
# ============================================================

_total = 0
_aprovados = 0


def _ok(desc: str) -> None:
    global _aprovados
    _aprovados += 1
    print(f"  [OK] {desc}")


def _falha(desc: str, motivo: str) -> None:
    print(f"  [FALHA] {desc}", file=sys.stderr)
    print(f"          {motivo}", file=sys.stderr)


def _secao(titulo: str) -> None:
    global _total
    _total += 1
    print(f"\n{'─' * 62}")
    print(f"  Caso {_total}: {titulo}")
    print(f"{'─' * 62}")


def _tipos(tokens: list[TokenInfo]) -> list[str]:
    return [t.tipo for t in tokens]


def _lexemas(tokens: list[TokenInfo]) -> list[str]:
    return [t.lexema for t in tokens]


# ============================================================
# ── CASOS OBRIGATÓRIOS DO ENUNCIADO ──────────────────────────
# ============================================================

def teste_valido_1(lexer: CupomLexer) -> None:
    _secao("Cupom com CNPJ (obrigatório válido 1)")
    tokens, erro = lexer.analisar(VALIDO_1)

    if erro:
        _falha("Caso válido 1", f"Erro inesperado: {erro.mensagem}")
        return

    tipos   = _tipos(tokens)
    lexemas = _lexemas(tokens)

    try:
        assert erro is None
        assert tipos[0]   == "ITEM"
        assert tipos[1]   == "COLON"
        assert tipos[2]   == "STRING"
        assert lexemas[2] == '"Arroz 5kg"'
        assert tipos[3]   == "QTD"
        assert tipos[5]   == "INTEGER"
        assert "MONEY"    in tipos
        assert "CNPJ"     in tipos
        assert "DATE"     in tipos
        assert "DATA"     in tipos

        im = tipos.index("MONEY")
        assert lexemas[im] == "R$ 27,90"

        ic = tipos.index("CNPJ")
        assert lexemas[ic] == "12.345.678/0001-90"

        id_ = tipos.index("DATE")
        assert lexemas[id_] == "28/07/2026"

    except AssertionError as e:
        _falha("Caso válido 1", str(e))
        return

    _ok("Caso válido 1 — CNPJ, MONEY, DATE, palavras reservadas corretos")
    _imprimir_tokens(tokens)


def teste_valido_2(lexer: CupomLexer) -> None:
    _secao("Cupom com CPF e MONEY com milhar (obrigatório válido 2)")
    tokens, erro = lexer.analisar(VALIDO_2)

    if erro:
        _falha("Caso válido 2", f"Erro inesperado: {erro.mensagem}")
        return

    tipos   = _tipos(tokens)
    lexemas = _lexemas(tokens)

    try:
        assert erro is None
        assert "CPF"   in tipos
        assert "MONEY" in tipos

        im = tipos.index("MONEY")
        assert lexemas[im] == "R$ 3.499,90", f"MONEY={lexemas[im]!r}"

        ic = tipos.index("CPF")
        assert lexemas[ic] == "123.456.789-09"

        assert "DATE" in tipos

    except AssertionError as e:
        _falha("Caso válido 2", str(e))
        return

    _ok("Caso válido 2 — CPF e MONEY com milhar reconhecidos")
    _imprimir_tokens(tokens)


def teste_valido_3(lexer: CupomLexer) -> None:
    _secao("Cupom com comentário ignorado (obrigatório válido 3)")
    tokens, erro = lexer.analisar(VALIDO_3)

    if erro:
        _falha("Caso válido 3", f"Erro inesperado: {erro.mensagem}")
        return

    tipos = _tipos(tokens)

    try:
        assert erro is None
        for tok in tokens:
            assert "supermercado" not in tok.lexema
            assert tok.lexema.strip() != "#"
        assert "ITEM"  in tipos
        assert "CNPJ"  in tipos
        assert "DATE"  in tipos
        assert "MONEY" in tipos
        assert tipos[0] == "ITEM"

        im = tipos.index("MONEY")
        assert _lexemas(tokens)[im] == "R$ 18,50"

    except AssertionError as e:
        _falha("Caso válido 3", str(e))
        return

    _ok("Caso válido 3 — comentário ignorado pelo %ignore")
    _imprimir_tokens(tokens)


def teste_invalido_1(lexer: CupomLexer) -> None:
    _secao('Caractere "@" inválido (obrigatório inválido 1)')
    tokens, erro = lexer.analisar(INVALIDO_1)

    try:
        assert erro is not None,        "Deve detectar erro léxico"
        assert erro.caractere == "@",   f"Caractere deve ser '@', obteve {erro.caractere!r}"
        assert erro.linha  >= 1,        "Linha deve ser >= 1"
        assert erro.coluna >= 1,        "Coluna deve ser >= 1"
        assert len(erro.dica) > 0

    except AssertionError as e:
        _falha("Caso inválido 1", str(e))
        return

    _ok("Caso inválido 1 detectado — '@' com linha e coluna")
    print(f"       Linha  : {erro.linha}")
    print(f"       Coluna : {erro.coluna}")
    print(f"       Char   : {erro.caractere!r}")
    print(f"       Dica   : {erro.dica}")


def teste_invalido_2(lexer: CupomLexer) -> None:
    _secao('Caractere "$" isolado (obrigatório inválido 2)')
    tokens, erro = lexer.analisar(INVALIDO_2)

    try:
        assert erro is not None,   "Deve detectar erro léxico"
        assert erro.linha  >= 1
        assert erro.coluna >= 1
        assert len(erro.dica) > 0

    except AssertionError as e:
        _falha("Caso inválido 2", str(e))
        return

    _ok("Caso inválido 2 detectado — '$' com linha e coluna")
    print(f"       Linha  : {erro.linha}")
    print(f"       Coluna : {erro.coluna}")
    print(f"       Char   : {erro.caractere!r}")
    print(f"       Dica   : {erro.dica}")


# ============================================================
# ── CHECKLIST DO PROFESSOR ────────────────────────────────────
# ============================================================

def teste_case_insensitive(lexer: CupomLexer) -> None:
    """Flag /i: ITEM, item, Item, ItEm → todos devem ser ITEM."""
    _secao("Checklist /i — case-insensitive (ITEM/item/Item/ItEm)")
    variantes = ["ITEM", "item", "Item", "ItEm"]
    for v in variantes:
        tokens, erro = lexer.analisar(v)
        try:
            assert erro is None,          f"'{v}' não deve gerar erro"
            assert len(tokens) == 1,      f"'{v}' deve gerar 1 token, obteve {len(tokens)}"
            assert tokens[0].tipo == "ITEM", f"'{v}' deve ser ITEM, obteve {tokens[0].tipo!r}"
        except AssertionError as e:
            _falha(f"case-insensitive '{v}'", str(e))
            return
    _ok("ITEM / item / Item / ItEm → todos reconhecidos como ITEM (flag /i)")


def teste_fronteira_palavra(lexer: CupomLexer) -> None:
    r"""Fronteira \b: ITEMIZADO não deve virar ITEM + algo."""
    _secao(r"Checklist \b — fronteira de palavra (ITEMIZADO → ID)")
    tokens, erro = lexer.analisar("ITEMIZADO")
    try:
        assert erro is None,          "ITEMIZADO não deve gerar erro"
        assert len(tokens) == 1,      f"ITEMIZADO deve ser 1 token, obteve {len(tokens)}"
        assert tokens[0].tipo == "ID", f"ITEMIZADO deve ser ID, obteve {tokens[0].tipo!r}"
    except AssertionError as e:
        _falha(r"fronteira \b", str(e))
        return
    _ok(r"ITEMIZADO reconhecido como ID — \b bloqueia match parcial")


def teste_date_unico(lexer: CupomLexer) -> None:
    """DATE não deve ser fragmentado em INTEGERs."""
    _secao("Checklist DATE — não fragmentado em INTEGER (prioridade .3)")
    tokens, erro = lexer.analisar("28/07/2026")
    try:
        assert erro is None
        assert len(tokens) == 1,          f"28/07/2026 deve ser 1 token, obteve {len(tokens)}: {_lexemas(tokens)}"
        assert tokens[0].tipo == "DATE",  f"Deve ser DATE, obteve {tokens[0].tipo!r}"
        assert tokens[0].lexema == "28/07/2026"
    except AssertionError as e:
        _falha("DATE fragmentado", str(e))
        return
    _ok("28/07/2026 → DATE (um único token, não vários INTEGERs)")


def teste_money_variantes(lexer: CupomLexer) -> None:
    """MONEY não deve ser fragmentado — prioridade .3."""
    _secao("Checklist MONEY — prioridade .3 evita fragmentação")
    casos = [
        ("R$ 10,00",    "R$ 10,00"),
        ("R$ 27,90",    "R$ 27,90"),
        ("R$ 1.250,50", "R$ 1.250,50"),
        ("R$ 3.499,90", "R$ 3.499,90"),
    ]
    for entrada, esperado in casos:
        tokens, erro = lexer.analisar(entrada)
        try:
            assert erro is None
            assert len(tokens) == 1,             f"'{entrada}': obteve {len(tokens)} tokens"
            assert tokens[0].tipo == "MONEY",    f"Deve ser MONEY, obteve {tokens[0].tipo!r}"
            assert tokens[0].lexema == esperado, f"Lexema: {tokens[0].lexema!r} ≠ {esperado!r}"
        except AssertionError as e:
            _falha(f"MONEY '{entrada}'", str(e))
            return
    _ok("R$ 10,00 / 27,90 / 1.250,50 / 3.499,90 → todos MONEY (1 token)")


def teste_comentario_ignorado(lexer: CupomLexer) -> None:
    """#comentário deve ser completamente ignorado (%ignore)."""
    _secao("Checklist %ignore — comentário não gera token")
    texto = '# comentário do cupom\nITEM: "Arroz"'
    tokens, erro = lexer.analisar(texto)
    try:
        assert erro is None
        for tok in tokens:
            assert "comentário" not in tok.lexema
            assert "#" not in tok.lexema
        assert tokens[0].tipo == "ITEM", f"Primeiro token deve ser ITEM, obteve {tokens[0].tipo!r}"
    except AssertionError as e:
        _falha("%ignore comentário", str(e))
        return
    _ok("# comentário ignorado — não aparece na lista de tokens")


def teste_string_literal_vs_regex(lexer: CupomLexer) -> None:
    """COLON e COMMA são definidos por string literal (não regex)."""
    _secao("Checklist STRING LITERAL — COLON ':' e COMMA ','")
    tokens, erro = lexer.analisar("ITEM: produto, outro")
    try:
        assert erro is None
        tipos = _tipos(tokens)
        assert "COLON" in tipos,  "COLON deve estar presente"
        assert "COMMA" in tipos,  "COMMA deve estar presente"
    except AssertionError as e:
        _falha("string literal", str(e))
        return
    _ok("COLON ':' e COMMA ',' reconhecidos via string literal")


def teste_unexpectedcharacters(lexer: CupomLexer) -> None:
    """UnexpectedCharacters capturado corretamente com linha e coluna."""
    _secao("Checklist UnexpectedCharacters — linha e coluna do erro")
    # Linha 2, caractere @ após alguns chars
    texto = 'ITEM: "Produto"\n@ QTD: 1'
    tokens, erro = lexer.analisar(texto)
    try:
        assert erro is not None,         "Deve detectar erro léxico"
        assert erro.linha == 2,          f"Linha deve ser 2, obteve {erro.linha}"
        assert erro.coluna == 1,         f"Coluna deve ser 1, obteve {erro.coluna}"
        assert erro.caractere == "@",    f"Char deve ser '@', obteve {erro.caractere!r}"
    except AssertionError as e:
        _falha("UnexpectedCharacters linha/coluna", str(e))
        return
    _ok(f"UnexpectedCharacters: linha={erro.linha} coluna={erro.coluna} char={erro.caractere!r}")


def teste_start_end_pos(lexer: CupomLexer) -> None:
    """t.start_pos e t.end_pos devem ser populados corretamente."""
    _secao("Checklist start_pos / end_pos — posições no texto")
    texto = 'ITEM: "Arroz"'
    tokens, erro = lexer.analisar(texto)
    try:
        assert erro is None

        # ITEM começa na posição 0, tem 4 chars → end=4
        item_tok = tokens[0]
        assert item_tok.tipo == "ITEM"
        assert item_tok.start_pos == 0,  f"start_pos de ITEM: {item_tok.start_pos}"
        assert item_tok.end_pos   == 4,  f"end_pos de ITEM: {item_tok.end_pos}"

        # COLON está na posição 4
        colon_tok = tokens[1]
        assert colon_tok.tipo == "COLON"
        assert colon_tok.start_pos == 4, f"start_pos de COLON: {colon_tok.start_pos}"
        assert colon_tok.end_pos   == 5, f"end_pos de COLON: {colon_tok.end_pos}"

        # STRING '"Arroz"' começa na posição 6 (após espaço)
        str_tok = tokens[2]
        assert str_tok.tipo == "STRING"
        assert str_tok.start_pos == 6,   f"start_pos de STRING: {str_tok.start_pos}"
        assert str_tok.end_pos   == 13,  f"end_pos de STRING: {str_tok.end_pos}"

    except AssertionError as e:
        _falha("start_pos/end_pos", str(e))
        return

    _ok("t.start_pos e t.end_pos corretos para ITEM, COLON e STRING")
    print()
    print(f"       {'TOKEN':<12} {'LEXEMA':<15} {'LINHA':>5} {'COL':>4} {'START':>6} {'END':>5}")
    print(f"       {'─'*12} {'─'*15} {'─'*5} {'─'*4} {'─'*6} {'─'*5}")
    for tok in tokens:
        print(
            f"       {tok.tipo:<12} {tok.lexema:<15} "
            f"{tok.linha:>5} {tok.coluna:>4} {tok.start_pos:>6} {tok.end_pos:>5}"
        )


def teste_data_vs_date(lexer: CupomLexer) -> None:
    """DATA (palavra reservada) ≠ DATE (literal de data)."""
    _secao("Checklist DATA (reservada) vs DATE (literal)")
    t_data, _ = lexer.analisar("DATA")
    t_date, _ = lexer.analisar("28/07/2026")
    try:
        assert t_data[0].tipo == "DATA",       f"'DATA' deve ser DATA, obteve {t_data[0].tipo!r}"
        assert t_date[0].tipo == "DATE",       f"'28/07/2026' deve ser DATE, obteve {t_date[0].tipo!r}"
        assert t_date[0].lexema == "28/07/2026"
    except AssertionError as e:
        _falha("DATA vs DATE", str(e))
        return
    _ok("DATA → palavra reservada  |  28/07/2026 → DATE literal")


def teste_erro_lexico_vs_negocio(lexer: CupomLexer) -> None:
    """
    Regra de negócio NÃO deve ser tratada como erro léxico.
    QTD: -5 → '-' é um símbolo não reconhecido (erro léxico),
    mas QTD com valor negativo é questão de regra de negócio.
    """
    _secao("Checklist Erro Léxico × Regra de Negócio")
    # Valores lexicamente válidos — não há erro léxico
    entradas_validas = [
        'QTD: 9999',          # quantidade grande — válida lexicamente
        'VL: R$ 99.999,99',   # valor alto — válido lexicamente
    ]
    for entrada in entradas_validas:
        tokens, erro = lexer.analisar(entrada)
        try:
            assert erro is None, f"'{entrada}' não deve gerar erro léxico: {erro}"
        except AssertionError as e:
            _falha("Erro léxico × negócio", str(e))
            return
    _ok("QTD: 9999 e VL: R$ 99.999,99 → válidos lexicamente (regra de negócio não é papel do lexer)")


# ============================================================
# Impressão auxiliar de tokens
# ============================================================

def _imprimir_tokens(tokens: list[TokenInfo]) -> None:
    print(f"\n       {'TIPO':<12} {'LEXEMA':<22} {'L':>3} {'C':>3} {'INI':>5} {'FIM':>5}")
    print(f"       {'─'*12} {'─'*22} {'─'*3} {'─'*3} {'─'*5} {'─'*5}")
    for tok in tokens:
        print(
            f"       {tok.tipo:<12} {tok.lexema!r:<22} "
            f"{tok.linha:>3} {tok.coluna:>3} "
            f"{tok.start_pos:>5} {tok.end_pos:>5}"
        )


# ============================================================
# Runner principal
# ============================================================

def main() -> None:
    print()
    print("=" * 62)
    print("  ANALISADOR LÉXICO — CUPOM FISCAL ELETRÔNICO")
    print("  Suite de Testes Automatizados")
    print("=" * 62)

    lexer = CupomLexer()

    # Casos obrigatórios do enunciado
    teste_valido_1(lexer)
    teste_valido_2(lexer)
    teste_valido_3(lexer)
    teste_invalido_1(lexer)
    teste_invalido_2(lexer)

    # Checklist do professor
    teste_case_insensitive(lexer)
    teste_fronteira_palavra(lexer)
    teste_date_unico(lexer)
    teste_money_variantes(lexer)
    teste_comentario_ignorado(lexer)
    teste_string_literal_vs_regex(lexer)
    teste_unexpectedcharacters(lexer)
    teste_start_end_pos(lexer)
    teste_data_vs_date(lexer)
    teste_erro_lexico_vs_negocio(lexer)

    print()
    print("=" * 62)
    print("  TESTES FINALIZADOS")
    print(f"  {_total} casos executados")
    print(f"  {_aprovados} resultados esperados" if _aprovados == _total else f"  {_aprovados}/{_total} aprovados")
    if _aprovados < _total:
        print(f"  {_total - _aprovados} FALHA(S) — verifique stderr")
    print("=" * 62)

    sys.exit(0 if _aprovados == _total else 1)


if __name__ == "__main__":
    main()
