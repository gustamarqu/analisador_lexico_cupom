"""
Analisador Léxico — Cupom Fiscal Eletrônico
Módulo principal de tokenização utilizando a biblioteca Lark.

Conceitos demonstrados:
  - Uso de Lark.lex() para percorrer tokens
  - Acesso a t.line, t.column, t.start_pos, t.end_pos
  - Captura específica de UnexpectedCharacters (erro léxico)
  - Diferenciação entre erro léxico e regra de negócio
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from lark import Lark, Token
from lark.exceptions import UnexpectedCharacters, UnexpectedToken


# ---------------------------------------------------------------
# Mapeamento: nome interno do terminal → nome exibido ao usuário
# ---------------------------------------------------------------
NOMES_TOKENS: dict[str, str] = {
    "KW_ITEM":     "ITEM",
    "KW_QTD":      "QTD",
    "KW_UN":       "UN",
    "KW_VL":       "VL",
    "KW_DATA":     "DATA",
    "KW_TOTAL":    "TOTAL",
    "KW_SUBTOTAL": "SUBTOTAL",
    "KW_DESCONTO": "DESCONTO",
    "CNPJ":        "CNPJ",
    "CPF":         "CPF",
    "DATE":        "DATE",
    "MONEY":       "MONEY",
    "STRING":      "STRING",
    "DECIMAL":     "DECIMAL",
    "INTEGER":     "INTEGER",
    "ID":          "ID",
    "COLON":       "COLON",
    "COMMA":       "COMMA",
    "LPAREN":      "LPAREN",
    "RPAREN":      "RPAREN",
    "SEMICOLON":   "SEMICOLON",
    "EQUALS":      "EQUALS",
    "PERCENT":     "PERCENT",
    "ASTERISK":    "ASTERISK",
}

# Dicas específicas por caractere inválido (erro léxico)
_DICAS_ERRO: dict[str, str] = {
    "@": (
        'O símbolo "@" não é válido em cupons fiscais.\n'
        "Verifique se não há endereços de e-mail no texto."
    ),
    "$": (
        "Para valores monetários use o formato: R$ 27,90\n"
        'O símbolo "$" sozinho não é reconhecido.'
    ),
    "&": 'O símbolo "&" não é válido. Use a palavra "e" para conectar itens.',
    "!": 'O símbolo "!" não é esperado em cupons fiscais.',
    "?": 'O símbolo "?" não é esperado em cupons fiscais.',
    "\\": 'A barra invertida "\\" não é válida em cupons fiscais.',
    "^": 'O símbolo "^" não é válido em cupons fiscais.',
    "~": 'O símbolo "~" não é válido em cupons fiscais.',
    "`": 'O acento grave "`" não é válido em cupons fiscais.',
    "{": "Chaves não são válidas. Use parênteses () para agrupar informações.",
    "}": "Chaves não são válidas. Use parênteses () para agrupar informações.",
    "[": "Colchetes não são válidos. Use parênteses () para agrupar informações.",
    "]": "Colchetes não são válidos. Use parênteses () para agrupar informações.",
}

_DICA_PADRAO = (
    "Verifique se o cupom contém apenas caracteres válidos.\n"
    'Permitidos: letras, números, aspas ("), dois-pontos (:), vírgula (,),\n'
    "ponto (.), barra (/), parênteses e valores monetários no formato R$ X,XX."
)


@dataclass
class TokenInfo:
    """
    Representa um token reconhecido pelo analisador.

    Atributos (obtidos diretamente do objeto Token do Lark):
      tipo      → categoria do token  (ex: ITEM, MONEY, CNPJ)
      lexema    → texto exato na entrada (ex: "item", "R$ 27,90")
      linha     → t.line    — número da linha (base 1)
      coluna    → t.column  — número da coluna (base 1)
      start_pos → t.start_pos — posição inicial no texto (base 0)
      end_pos   → t.end_pos   — posição final no texto (base 0)
    """
    tipo:      str
    lexema:    str
    linha:     int
    coluna:    int
    start_pos: int
    end_pos:   int

    def __repr__(self) -> str:
        return (
            f"TokenInfo(tipo={self.tipo!r}, lexema={self.lexema!r}, "
            f"linha={self.linha}, coluna={self.coluna}, "
            f"start_pos={self.start_pos}, end_pos={self.end_pos})"
        )


@dataclass
class ErroLexico:
    """
    Representa um erro léxico (UnexpectedCharacters do Lark).

    DIFERENÇA ENTRE ERRO LÉXICO E REGRA DE NEGÓCIO:
      Erro léxico: o caractere/sequência não pertence a nenhum padrão
                   definido na gramática. Ex: "@", "$" isolado.
                   Capturado por UnexpectedCharacters.

      Regra de negócio: o token é lexicamente válido, mas o valor
                        viola uma restrição do domínio.
                        Ex: QTD negativa, CNPJ matematicamente inválido.
                        NÃO é responsabilidade do analisador léxico.
    """
    linha:     int
    coluna:    int
    caractere: str
    mensagem:  str
    dica:      str


class CupomLexer:
    """
    Analisador léxico para Cupom Fiscal Eletrônico.

    Usa a biblioteca Lark com a gramática em grammar.lark.
    A tokenização é feita via Lark.lex(), que retorna objetos Token
    contendo type, line, column, start_pos e end_pos.
    """

    def __init__(self) -> None:
        grammar_path = Path(__file__).parent / "grammar.lark"
        grammar_text = grammar_path.read_text(encoding="utf-8")
        # parser='earley' + lexer='basic' para uso como lexer puro
        self._lark = Lark(grammar_text, parser="earley", lexer="basic")

    # ------------------------------------------------------------------
    # API pública
    # ------------------------------------------------------------------

    def analisar(self, texto: str) -> tuple[list[TokenInfo], Optional[ErroLexico]]:
        """
        Analisa o texto e retorna a lista de tokens ou um erro léxico.

        Returns:
            (tokens, None)       — análise bem-sucedida
            ([], ErroLexico)     — caractere não reconhecido na entrada
        """
        try:
            tokens = self._tokenizar(texto)
            return tokens, None
        except UnexpectedCharacters as exc:
            # Captura específica de UnexpectedCharacters (erro léxico).
            # Usa exc.line e exc.column para localizar o erro.
            return [], self._formatar_erro_inesperado(exc, texto)
        except UnexpectedToken as exc:
            return [], ErroLexico(
                linha=getattr(exc.token, "line", 1) or 1,
                coluna=getattr(exc.token, "column", 1) or 1,
                caractere=str(exc.token),
                mensagem=f"Token inesperado: {exc.token!r}",
                dica=_DICA_PADRAO,
            )
        except Exception as exc:  # noqa: BLE001
            return [], ErroLexico(
                linha=1,
                coluna=1,
                caractere="?",
                mensagem=f"Erro inesperado: {exc}",
                dica="Verifique se o texto de entrada está no formato correto.",
            )

    def formatar_erro_texto(self, erro: ErroLexico) -> str:
        """Formata um ErroLexico como texto legível para o terminal."""
        sep = "─" * 52
        return (
            f"{sep}\n"
            f"  ERRO LÉXICO\n"
            f"{sep}\n"
            f"  Linha :  {erro.linha}\n"
            f"  Coluna:  {erro.coluna}\n"
            f"\n"
            f"  {erro.mensagem}\n"
            f"\n"
            f"  Dica:\n"
            f"  {erro.dica}\n"
            f"{sep}"
        )

    # ------------------------------------------------------------------
    # Métodos internos
    # ------------------------------------------------------------------

    def _tokenizar(self, texto: str) -> list[TokenInfo]:
        """
        Percorre os tokens do Lark e extrai:
          t.type, t.line, t.column, t.start_pos, t.end_pos
        """
        resultado: list[TokenInfo] = []
        for t in self._lark.lex(texto):
            resultado.append(self._converter_token(t))
        return resultado

    def _converter_token(self, t: Token) -> TokenInfo:
        """
        Converte Token do Lark para TokenInfo, extraindo
        explicitamente: t.line, t.column, t.start_pos, t.end_pos
        """
        tipo = NOMES_TOKENS.get(t.type, t.type)

        # t.start_pos: posição do primeiro caractere no texto (base 0)
        # t.end_pos:   posição após o último caractere (base 0)
        start = t.start_pos if t.start_pos is not None else 0
        end   = t.end_pos   if t.end_pos   is not None else start + len(t)

        return TokenInfo(
            tipo=tipo,
            lexema=str(t),
            linha=t.line   or 1,
            coluna=t.column or 1,
            start_pos=start,
            end_pos=end,
        )

    def _formatar_erro_inesperado(
        self, exc: UnexpectedCharacters, texto: str
    ) -> ErroLexico:
        """
        Cria ErroLexico a partir de UnexpectedCharacters.
        Usa exc.line e exc.column para localizar o problema.
        """
        linha  = exc.line
        coluna = exc.column

        # Extrai o caractere problemático usando linha e coluna
        linhas = texto.splitlines()
        if 1 <= linha <= len(linhas):
            linha_texto = linhas[linha - 1]
            caractere = linha_texto[coluna - 1] if coluna <= len(linha_texto) else "?"
        else:
            caractere = "?"

        dica = _DICAS_ERRO.get(caractere, _DICA_PADRAO)
        mensagem = f"Caractere inesperado: {caractere!r}"

        return ErroLexico(
            linha=linha,
            coluna=coluna,
            caractere=caractere,
            mensagem=mensagem,
            dica=dica,
        )
