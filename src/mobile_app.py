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
    page.title = "Gestão Terças FC"
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

    # --- 1. GALERIA DE CAMPEÕES (DINÂMICA) ---
    galeria_container = ft.Column()

    def carregar_galeria():
        campeoes = get_api("champions/")
        galeria_container.controls.clear()
        galeria_container.controls.append(ft.Divider())
        galeria_container.controls.append(ft.Text("GALERIA DE CAMPEÕES 🏆", weight="bold", color="yellow"))

        if not campeoes:
            galeria_container.controls.append(ft.Text("Sem registos...", italic=True, color="grey"))

        for c in campeoes:
            trofeus = "🏆" * c['titles']
            galeria_container.controls.append(ft.Row([
                ft.Text(f"{c['name']}:", weight="bold"),
                ft.Text(trofeus)
            ]))
        page.update()

    # --- 2. TABELA ---
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

    # --- 2. HISTÓRICO E REGRAS (RESTAURADO!) ---

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

    # --- 3. TESOURARIA (NOVO) ---
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
        lista_dividas.controls.append(ft.Text(f"Dívida Total da Liga: {total_divida:.2f}€", color="red"))
        page.update()

    def registar_pagamento(e):
        if not dd_pagador.value or not input_pagamento.value: return
        try:
            val = float(input_pagamento.value)
            res = requests.post(f"{API_URL}/players/pay", json={"player_id": int(dd_pagador.value), "amount": val})
            if res.status_code == 200:
                show_msg(f"Pagamento de {val}€ aceite!")
                input_pagamento.value = ""
                carregar_tesouraria()
            else: show_msg("Erro", "red")
        except: show_msg("Valor inválido", "red")

    btn_pagar = ft.ElevatedButton("Registar Pagamento 💰", on_click=registar_pagamento)

    # --- 4. ADMIN ---
    col_a = ft.Column(); col_b = ft.Column()
    dd_campeao = ft.Dropdown(label="Quem ganhou a época?")

    def carregar_admin():
        jogadores = get_api("players/")
        col_a.controls.clear(); col_b.controls.clear(); team_a_selected.clear(); team_b_selected.clear()
        dd_campeao.options.clear()
        for p in jogadores:
            cba = ft.Checkbox(label=p['name']); cba.data = p['id']; team_a_selected.append(cba); col_a.controls.append(cba)
            cbb = ft.Checkbox(label=p['name']); cbb.data = p['id']; team_b_selected.append(cbb); col_b.controls.append(cbb)
            dd_campeao.options.append(ft.dropdown.Option(p['name']))
        page.update()

    dd_res = ft.Dropdown(label="Resultado", options=[ft.dropdown.Option("TEAM_A", "Vitória A"), ft.dropdown.Option("TEAM_B", "Vitória B"), ft.dropdown.Option("DRAW", "Empate")])
    chk_x2 = ft.Checkbox(label="Pontos x2?", fill_color="yellow")

    def gravar_jogo(e):
        ids_a = [c.data for c in team_a_selected if c.value]
        ids_b = [c.data for c in team_b_selected if c.value]
        if not ids_a or not ids_b or not dd_res.value: show_msg("Falta info", "red"); return
        try:
            requests.post(f"{API_URL}/matches/", json={"date": str(datetime.date.today()), "result": dd_res.value, "team_a_players": ids_a, "team_b_players": ids_b, "is_double_points": chk_x2.value})
            show_msg("Jogo Gravado! (-3€ a cada jogador)"); carregar_tesouraria(); atualizar_tabela();
            for c in team_a_selected + team_b_selected: c.value = False
        except: show_msg("Erro", "red")

    btn_gravar = ft.ElevatedButton("Gravar Jogo (Custa 3€)", on_click=gravar_jogo)

    # Fechar Época
    def fechar_epoca(e):
        if not dd_campeao.value: show_msg("Escolhe o Campeão!", "red"); return
        if btn_close.text == "Fechar Época":
            btn_close.text = "Tens a Certeza?"; btn_close.bgcolor = "orange"; page.update()
            return
        try:
            requests.post(f"{API_URL}/season/close", json={"champion_name": dd_campeao.value, "season_name": "Época"})
            show_msg("Época Fechada! Parabéns ao Campeão!"); carregar_galeria(); atualizar_tabela()
            btn_close.text = "Fechar Época"; btn_close.bgcolor="red"
        except: show_msg("Erro", "red")

    btn_close = ft.ElevatedButton("Fechar Época", bgcolor="red", color="white", on_click=fechar_epoca)

    # Criar Jogador
    new_name = ft.TextField(label="Novo Jogador");
    def criar(e):
        if new_name.value: requests.post(f"{API_URL}/players/", json={"name": new_name.value}); show_msg("Criado!"); carregar_admin(); new_name.value=""
    btn_criar = ft.ElevatedButton("Criar", on_click=criar)

    # --- LOGIN SYSTEM ---
    pass_input = ft.TextField(label="Senha", password=True)
    def login(e):
        if pass_input.value == PASS_ADMIN:
            state["role"] = "admin"; show_msg("Bem-vindo Admin 👑"); construir_layout()
        elif pass_input.value == PASS_TESOUREIRO:
            state["role"] = "treasurer"; show_msg("Bem-vindo Tesoureiro 💰"); construir_layout()
        else: show_msg("Senha errada", "red")

    view_login = ft.Column([ft.Text("Login Terças FC", size=20), pass_input, ft.ElevatedButton("Entrar", on_click=login)], alignment="center")

    # --- LAYOUT BUILDER ---
    def construir_layout():
        page.clean()

        # Tabs base
        tabs_list = [
            ft.Tab(text="Liga", icon=ft.Icons.LEADERBOARD, content=ft.Column([ft.Text("Classificação", size=20, weight="bold"), ft.Row([tabela], scroll="always"), galeria_container], scroll="auto"))
        ]

        # Se for Tesoureiro ou Admin, vê a Tesouraria
        if state["role"] in ["admin", "treasurer"]:
            carregar_tesouraria()
            tabs_list.append(ft.Tab(text="Tesouraria", icon=ft.Icons.EURO, content=ft.Column([
                ft.Text("Gestão de Dívidas", size=20),
                ft.Row([dd_pagador, input_pagamento], alignment="center"), btn_pagar, ft.Divider(),
                lista_dividas
            ], scroll="auto")))

        # Se for Admin, vê a gestão
        if state["role"] == "admin":
            carregar_admin()
            tabs_list.append(ft.Tab(text="Admin", icon=ft.Icons.SETTINGS, content=ft.Column([
                ft.Text("Registar Jogo", weight="bold"),
                ft.Container(content=ft.Row([
                    ft.Column([ft.Text("Eq. A", color="green"), col_a]), ft.VerticalDivider(), ft.Column([ft.Text("Eq. B", color="blue"), col_b])
                ]), height=200, border=ft.border.all(1, "grey"), padding=5),
                dd_res, chk_x2, btn_gravar, ft.Divider(),
                ft.Text("Gestão", weight="bold"), ft.Row([new_name, btn_criar]), ft.Divider(),
                ft.Text("Fim de Época", color="red"), dd_campeao, btn_close
            ], scroll="auto")))

        t = ft.Tabs(selected_index=0, tabs=tabs_list, expand=True)
        page.add(t)

    # INICIO: Se não estiver logado, mostra login.
    # Mas queremos que a Tabela seja publica? Se sim, mudamos a logica.
    # Para já, mostra Login primeiro para segurança.
    page.add(view_login)

# Render deploy
app = ft.app(target=main, export_asgi_app=True)