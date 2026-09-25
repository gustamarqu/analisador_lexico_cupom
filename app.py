"""
Interface interativa — Analisador Léxico Cupom Fiscal Eletrônico.

Demonstra explicitamente (checklist do professor):
  - widgets.Textarea  → área de entrada de texto
  - widgets.Button    → botões Analisar e Limpar
  - widgets.Output    → área de resultado
  - on_click          → conexão do evento de clique ao handler

Execute em Jupyter Notebook ou Google Colab:
    import app
    app.iniciar()
"""

from __future__ import annotations

import ipywidgets as widgets
from IPython.display import display, HTML, clear_output

from lexer import CupomLexer, TokenInfo, ErroLexico

# ---------------------------------------------------------------
# Estilos CSS
# ---------------------------------------------------------------
_CSS = """
<style>
  .cupom-titulo {
    background: linear-gradient(135deg, #1a3a5c, #2e6da4);
    color: white;
    padding: 16px 22px;
    border-radius: 8px 8px 0 0;
  }
  .cupom-titulo h2 { margin: 0 0 4px 0; font-size: 1.35em; letter-spacing: .4px; }
  .cupom-titulo p  { margin: 0; font-size: .88em; opacity: .85; }

  .resultado-sucesso {
    background: #e8f5e9; border-left: 4px solid #43a047;
    color: #2e7d32; padding: 9px 14px; border-radius: 4px;
    margin-bottom: 10px; font-weight: bold;
  }
  .resultado-erro {
    background: #ffebee; border-left: 4px solid #e53935;
    color: #c62828; padding: 9px 14px; border-radius: 4px;
    margin-bottom: 10px;
  }
  .resultado-erro pre {
    margin: 7px 0 0; font-size: .87em;
    white-space: pre-wrap; color: #b71c1c;
  }
  .resumo {
    background: #e3f2fd; border: 1px solid #90caf9;
    color: #1565c0; padding: 7px 13px; border-radius: 4px;
    margin-bottom: 12px; font-size: .91em;
  }
  .tabela-tokens {
    width: 100%; border-collapse: collapse; font-size: .88em;
  }
  .tabela-tokens th {
    background: #1a3a5c; color: white; padding: 7px 11px;
    text-align: left; font-weight: 600;
  }
  .tabela-tokens th.num { text-align: center; }
  .tabela-tokens td {
    padding: 5px 11px; border-bottom: 1px solid #e0e0e0;
    font-family: 'Consolas','Courier New',monospace;
  }
  .tabela-tokens td.num { text-align: center; }
  .tabela-tokens tr:nth-child(even) td { background: #f5f8fb; }
  .tabela-tokens tr:hover td { background: #e8f0fe; }
  .badge { display:inline-block; padding:2px 8px; border-radius:12px;
           font-size:.82em; font-weight:600; }
  .b-res  { background:#e8f5e9; color:#2e7d32; }  /* reservada */
  .b-dom  { background:#fff3e0; color:#e65100; }  /* domínio   */
  .b-lit  { background:#fce4ec; color:#880e4f; }  /* literal   */
  .b-sim  { background:#f3e5f5; color:#6a1b9a; }  /* símbolo   */
  .b-id   { background:#e3f2fd; color:#1565c0; }  /* ID        */
</style>
"""

_CATEGORIA: dict[str, str] = {
    "ITEM":"b-res","QTD":"b-res","UN":"b-res","VL":"b-res","DATA":"b-res",
    "TOTAL":"b-res","SUBTOTAL":"b-res","DESCONTO":"b-res",
    "CNPJ":"b-dom","CPF":"b-dom","DATE":"b-dom","MONEY":"b-dom",
    "STRING":"b-lit","INTEGER":"b-lit","DECIMAL":"b-lit",
    "ID":"b-id",
    "COLON":"b-sim","COMMA":"b-sim","LPAREN":"b-sim","RPAREN":"b-sim",
    "SEMICOLON":"b-sim","EQUALS":"b-sim","PERCENT":"b-sim","ASTERISK":"b-sim",
}

_EXEMPLO = """\
# Cupom de supermercado — exemplo
ITEM: "Arroz 5kg"
QTD: 2
UN: "UN"
VL: R$ 27,90
CNPJ: 12.345.678/0001-90
DATA: 28/07/2026
"""


def _esc(s: str) -> str:
    return s.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;").replace('"',"&quot;")


def _html_tabela(tokens: list[TokenInfo]) -> str:
    linhas = []
    for tok in tokens:
        cls = _CATEGORIA.get(tok.tipo, "b-id")
        linhas.append(
            f"<tr>"
            f"<td><span class='badge {cls}'>{tok.tipo}</span></td>"
            f"<td>{_esc(tok.lexema)}</td>"
            f"<td class='num'>{tok.linha}</td>"
            f"<td class='num'>{tok.coluna}</td>"
            f"<td class='num'>{tok.start_pos}</td>"
            f"<td class='num'>{tok.end_pos}</td>"
            f"</tr>"
        )
    corpo = "\n".join(linhas)
    return f"""
<table class="tabela-tokens">
  <thead><tr>
    <th>TOKEN</th><th>LEXEMA</th>
    <th class="num">LINHA</th><th class="num">COLUNA</th>
    <th class="num">INÍCIO</th><th class="num">FIM</th>
  </tr></thead>
  <tbody>{corpo}</tbody>
</table>"""


def _html_sucesso(n: int) -> str:
    return (
        f"<div class='resultado-sucesso'>✓ Análise concluída com sucesso!</div>"
        f"<div class='resumo'>Total de tokens: <strong>{n}</strong>"
        f" &nbsp;|&nbsp; Erros: <strong>0</strong></div>"
    )


def _html_erro(erro: ErroLexico) -> str:
    dica = _esc(erro.dica).replace("\n", "<br>")
    return (
        f"<div class='resultado-erro'>✕ Erro léxico encontrado"
        f"<pre>Linha : {erro.linha}\nColuna: {erro.coluna}\n\n"
        f"{_esc(erro.mensagem)}\n\nDica:\n{dica}</pre></div>"
    )


def iniciar() -> None:
    """
    Inicializa a interface ipywidgets.

    Componentes (checklist do professor):
      - widgets.Textarea  → entrada de texto
      - widgets.Button    → botão Analisar (on_click)
      - widgets.Button    → botão Limpar   (on_click)
      - widgets.Output    → área de resultado
    """
    lexer = CupomLexer()

    # ── Textarea ─────────────────────────────────────────────────
    # widgets.Textarea: área de entrada de texto multilinhas
    entrada = widgets.Textarea(
        value=_EXEMPLO,
        placeholder="Digite o cupom fiscal...",
        layout=widgets.Layout(width="100%", height="175px"),
    )

    # ── Buttons ──────────────────────────────────────────────────
    # widgets.Button + on_click: evento de clique conectado ao handler
    botao_analisar = widgets.Button(
        description="🔍 Analisar",
        button_style="primary",
        layout=widgets.Layout(width="140px", height="36px"),
    )

    botao_limpar = widgets.Button(
        description="🧹 Limpar",
        layout=widgets.Layout(width="110px", height="36px"),
    )

    # ── Output ───────────────────────────────────────────────────
    # widgets.Output: contêiner que captura display() / print()
    saida = widgets.Output(
        layout=widgets.Layout(
            border="1px solid #dde3ea",
            border_radius="4px",
            padding="12px",
            min_height="60px",
        )
    )

    # ── Handlers (on_click) ──────────────────────────────────────

    def analisar_cupom(b):
        """Handler conectado via botao_analisar.on_click(analisar_cupom)."""
        texto = entrada.value
        with saida:
            clear_output(wait=True)
            if not texto.strip():
                display(HTML("<p style='color:#888;font-style:italic'>Nenhuma entrada fornecida.</p>"))
                return

            tokens, erro = lexer.analisar(texto)

            html = _CSS
            if erro:
                html += _html_erro(erro)
            else:
                html += _html_sucesso(len(tokens))
                html += _html_tabela(tokens)
            display(HTML(html))

    def limpar_cupom(b):
        """Handler conectado via botao_limpar.on_click(limpar_cupom)."""
        entrada.value = ""
        with saida:
            clear_output()

    # Conexão on_click — checklist do professor
    botao_analisar.on_click(analisar_cupom)
    botao_limpar.on_click(limpar_cupom)

    # ── Layout ───────────────────────────────────────────────────
    titulo = widgets.HTML(value=f"""
<div class="cupom-titulo">
  <h2>Analisador Léxico — Cupom Fiscal Eletrônico</h2>
  <p>Digite uma entrada de cupom para identificar seus tokens.</p>
</div>""")

    botoes = widgets.HBox(
        [botao_analisar, botao_limpar],
        layout=widgets.Layout(margin="10px 0"),
    )

    painel = widgets.VBox(
        [titulo, entrada, botoes, saida],
        layout=widgets.Layout(
            border="1px solid #b0bec5",
            border_radius="8px",
            max_width="960px",
        ),
    )

    display(HTML(_CSS))
    display(painel)


if __name__ == "__main__":
    print("Execute no Jupyter Notebook: import app; app.iniciar()")
