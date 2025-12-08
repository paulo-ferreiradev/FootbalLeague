import flet as ft
import requests
import datetime
import threading
import time

# --- CONFIG ---
API_URL = "https://tercas-fc-api.onrender.com" # CONFIRMA O TEU LINK!

# PASSWORDS
PASS_ADMIN = "1234"
PASS_TESOUREIRO = "money"

def main(page: ft.Page):
    page.title = "Terças FC"
    page.theme_mode = ft.ThemeMode.DARK
    page.scroll = ft.ScrollMode.AUTO
    page.padding = 10

    # Estado
    state = {"role": None} # 'admin', 'treasurer', None
    team_a_selected = []
    team_b_selected = []

    # --- HELPERS ---
    def show_msg(txt, color="green"):
        page.snack_bar = ft.SnackBar(content=ft.Text(txt), bgcolor=color)
        page.snack_bar.open = True
        page.update()

    def get_api(path):
        try:
            r = requests.get(f"{API_URL}/{path}")
            return r.json() if r.status_code == 200 else []
        except: return []

    # --- 1. TABELA ---
    tabela = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Pos")),
            ft.DataColumn(ft.Text("Nome")),
            ft.DataColumn(ft.Text("P"), numeric=True),
            ft.DataColumn(ft.Text("J"), numeric=True),
            ft.DataColumn(ft.Text("V"), numeric=True),
            ft.DataColumn(ft.Text("E"), numeric=True),
            ft.DataColumn(ft.Text("D"), numeric=True),
        ], rows=[], column_spacing=5
    )

    def atualizar_tabela():
        dados = get_api("table/")
        tabela.rows.clear()
        for i, p in enumerate(dados):
            tabela.rows.append(ft.DataRow(cells=[
                ft.DataCell(ft.Text(str(i+1))),
                ft.DataCell(ft.Text(p['name'], weight="bold", size=13)),
                ft.DataCell(ft.Text(str(p['points']), color="yellow", weight="bold")),
                ft.DataCell(ft.Text(str(p['games_played']))),
                ft.DataCell(ft.Text(str(p['wins']), color="green")),
                ft.DataCell(ft.Text(str(p['draws']), color="blue")),
                ft.DataCell(ft.Text(str(p['losses']), color="red")),
            ]))
        page.update()

    # Auto-Update Loop
    def loop_update():
        while True:
            time.sleep(15)
            try: atualizar_tabela()
            except: pass
    threading.Thread(target=loop_update, daemon=True).start()

    # --- 2. HISTÓRICO E REGRAS ---

    # Esta é a parte dinâmica (Novos campeões vindos da Base de Dados)
    novos_campeoes_container = ft.Column()

    def carregar_novos_campeoes():
        campeoes = get_api("champions/")
        novos_campeoes_container.controls.clear()
        if campeoes:
            novos_campeoes_container.controls.append(ft.Text("NOVOS CAMPEÕES (App):", weight="bold", size=12, color="green"))
            for c in campeoes:
                trofeus = "🏆" * c['titles']
                novos_campeoes_container.controls.append(
                    ft.Row([ft.Text(f"{c['name'].upper()} =", weight="bold"), ft.Text(trofeus)], spacing=5)
                )
        page.update()

    # Esta é a parte ESTÁTICA (O texto exato da imagem que pediste)
    historico_estatico = ft.Column([
        ft.Divider(),
        ft.Text("TÍTULOS DE CAMPEÃO (Pavilhão Sécil & Pavilhão Escola Luisa Todi):", weight="bold", size=12),
        ft.Row([ft.Text("RAFAEL =", weight="bold"), ft.Text("🏆")], spacing=5),
        ft.Row([ft.Text("RENATO =", weight="bold"), ft.Text("🏆")], spacing=5),
        ft.Row([ft.Text("RUI =", weight="bold"), ft.Text("🏆")], spacing=5),
        ft.Row([ft.Text("ABDUL =", weight="bold"), ft.Text("🏆")], spacing=5),
        ft.Row([ft.Text("NUNO TAVARES =", weight="bold"), ft.Text("🏆🏆")], spacing=5),
        ft.Row([ft.Text("CASCA =", weight="bold"), ft.Text("🏆🏆")], spacing=5),
        ft.Row([ft.Text("JOÃO SILVA =", weight="bold"), ft.Text("🏆🏆")], spacing=5),
        ft.Row([ft.Text("JOÃO GALOPIM =", weight="bold"), ft.Text("🏆")], spacing=5),

        # Aqui entram os novos que fores adicionando pela App
        novos_campeoes_container
    ], spacing=2)

    regras_texto = ft.Column([
        ft.Divider(),
        ft.Text("VITÓRIA = 3 PONTOS"),
        ft.Text("EMPATE = 2 PONTOS"),
        ft.Text("DERROTA = 1 PONTO"),
        ft.Container(height=10),
        ft.Text("* PENALIZAÇÃO DE -3 PONTOS POR FALTA DE COMPARÊNCIA", size=12),
        ft.Text("1º CRITÉRIO DE DESEMPATE: MAIOR NUMERO DE JOGOS REALIZADOS", size=12, weight="bold"),
        ft.Text("SEMANALMENTE AS EQUIPAS SÃO ESCOLHIDAS PELO 1º E 2º CLASSIFICADOS", size=12),
        ft.Text("SÓ ENTRA NA TABELA QUEM TIVER PELO MENOS 50% DO TOTAL JOGOS REALIZADOS", size=12),

        historico_estatico
    ], spacing=5)

    # --- 3. TESOURARIA ---
    lista_dividas = ft.Column()
    input_pagamento = ft.TextField(label="Valor (€)", width=100, keyboard_type=ft.KeyboardType.NUMBER)
    dd_pagador = ft.Dropdown(label="Quem pagou?", expand=True)

    def carregar_tesouraria():
        jogadores = get_api("players/all") # Pega todos
        lista_dividas.controls.clear()
        dd_pagador.options.clear()

        total_divida = 0
        for p in jogadores:
            # Dropdown
            dd_pagador.options.append(ft.dropdown.Option(key=str(p['id']), text=p['name']))

            # Lista Visual
            cor = "red" if p['balance'] < 0 else "green"
            texto_saldo = f"{p['balance']:.2f}€"
            if p['balance'] < 0: total_divida += p['balance']

            lista_dividas.controls.append(
                ft.Row([
                    ft.Text(p['name'], weight="bold"),
                    ft.Text(texto_saldo, color=cor, weight="bold")
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
            )

        lista_dividas.controls.append(ft.Divider())
        lista_dividas.controls.append(ft.Text(f"Dívida Total da Liga: {total_divida:.2f}€", color="