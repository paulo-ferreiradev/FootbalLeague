import flet as ft
import requests
import datetime
import threading
import time

# =============================================================================
# CONFIGURATION
# =============================================================================
API_URL = "https://tercas-fc-api.onrender.com"

# Role Access Credentials
ADMIN_PASSWORD = "1234"
TREASURER_PASSWORD = "money"

# =============================================================================
# MAIN APPLICATION
# =============================================================================
def main(page: ft.Page):
    # --- Page Settings ---
    page.title = "Terças FC"
    page.theme_mode = ft.ThemeMode.DARK
    page.scroll = ft.ScrollMode.AUTO
    page.padding = 10

    # --- App State ---
    state = {
        "role": None  # Options: 'admin', 'treasurer', or None
    }

    # Global lists for selection
    team_a_checkboxes = []
    team_b_checkboxes = []

    # =========================================================================
    # HELPER FUNCTIONS
    # =========================================================================
    def show_toast(message: str, color: str = "green"):
        """Displays a snackbar message."""
        page.snack_bar = ft.SnackBar(content=ft.Text(message), bgcolor=color)
        page.snack_bar.open = True
        page.update()

    def fetch_api(endpoint: str):
        """Safe API GET request handler."""
        try:
            response = requests.get(f"{API_URL}/{endpoint}")
            return response.json() if response.status_code == 200 else []
        except Exception:
            return []

    # =========================================================================
    # UI: LEADERBOARD & HISTORY
    # =========================================================================

    # 1. Leaderboard Table
    leaderboard_table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Pos")),
            ft.DataColumn(ft.Text("Nome")),
            ft.DataColumn(ft.Text("P"), numeric=True),
            ft.DataColumn(ft.Text("J"), numeric=True),
            ft.DataColumn(ft.Text("V"), numeric=True),
            ft.DataColumn(ft.Text("E"), numeric=True),
            ft.DataColumn(ft.Text("D"), numeric=True),
        ],
        rows=[],
        column_spacing=5
    )

    def refresh_leaderboard():
        """Fetches data and populates the table."""
        data = fetch_api("table/")
        leaderboard_table.rows.clear()

        for i, player in enumerate(data):
            leaderboard_table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(i + 1))),
                        ft.DataCell(ft.Text(player['name'], weight="bold", size=13)),
                        # FIX: Used strings for colors instead of ft.colors objects
                        ft.DataCell(ft.Text(str(player['points']), color="yellow", weight="bold")),
                        ft.DataCell(ft.Text(str(player['games_played']))),
                        ft.DataCell(ft.Text(str(player['wins']), color="green")),
                        ft.DataCell(ft.Text(str(player['draws']), color="blue")),
                        ft.DataCell(ft.Text(str(player['losses']), color="red")),
                    ]
                )
            )
        page.update()

    # Background Auto-Update Thread
    def auto_update_loop():
        while True:
            time.sleep(15)
            try:
                refresh_leaderboard()
            except:
                pass

    threading.Thread(target=auto_update_loop, daemon=True).start()

    # 2. History and Rules (Static + Dynamic)

    # Dynamic container for new champions
    dynamic_champions_view = ft.Column()

    def refresh_new_champions():
        champions = fetch_api("champions/")
        dynamic_champions_view.controls.clear()

        if champions:
            dynamic_champions_view.controls.append(
                ft.Text("NOVOS CAMPEÕES (App):", weight="bold", size=12, color="green")
            )
            for c in champions:
                trophies = "🏆" * c['titles']
                dynamic_champions_view.controls.append(
                    ft.Row(
                        [ft.Text(f"{c['name'].upper()} =", weight="bold"), ft.Text(trophies)],
                        spacing=5
                    )
                )
        page.update()

    # Static History (Hardcoded as requested)
    static_history_view = ft.Column([
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

        # Append dynamic section here
        dynamic_champions_view
    ], spacing=2)

    # Rules Section
    rules_view = ft.Column([
        ft.Divider(),
        ft.Text("VITÓRIA = 3 PONTOS"),
        ft.Text("EMPATE = 2 PONTOS"),
        ft.Text("DERROTA = 1 PONTO"),
        ft.Container(height=10),
        ft.Text("* PENALIZAÇÃO DE -3 PONTOS POR FALTA DE COMPARÊNCIA", size=12),
        ft.Text("1º CRITÉRIO DE DESEMPATE: MAIOR NUMERO DE JOGOS REALIZADOS", size=12, weight="bold"),
        ft.Text("SEMANALMENTE AS EQUIPAS SÃO ESCOLHIDAS PELO 1º E 2º CLASSIFICADOS", size=12),
        ft.Text("SÓ ENTRA NA TABELA QUEM TIVER PELO MENOS 50% DO TOTAL JOGOS REALIZADOS", size=12),

        static_history_view
    ], spacing=5)

    # =========================================================================
    # UI: TREASURY
    # =========================================================================
    debt_list_view = ft.Column()
    payment_input = ft.TextField(label="Valor (€)", width=100, keyboard_type=ft.KeyboardType.NUMBER)
    payer_dropdown = ft.Dropdown(label="Quem pagou?", expand=True)

    def refresh_treasury():
        players = fetch_api("players/all")

        debt_list_view.controls.clear()
        payer_dropdown.options.clear()
        total_debt = 0.0

        for p in players:
            # Dropdown population
            payer_dropdown.options.append(ft.dropdown.Option(key=str(p['id']), text=p['name']))

            # Visual List
            # FIX: Used string colors
            color = "red" if p['balance'] < 0 else "green"
            balance_text = f"{p['balance']:.2f}€"

            if p['balance'] < 0:
                total_debt += p['balance']

            debt_list_view.controls.append(
                ft.Row([
                    ft.Text(p['name'], weight="bold"),
                    ft.Text(balance_text, color=color, weight="bold")
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
            )

        debt_list_view.controls.append(ft.Divider())
        debt_list_view.controls.append(
            ft.Text(f"Dívida Total da Liga: {total_divida:.2f}€" if 'total_divida' in locals() else f"Total: {total_debt:.2f}€", color="red")
        )
        page.update()

    def submit_payment(e):
        if not payer_dropdown.value or not payment_input.value:
            return
        try:
            amount = float(payment_input.value)
            res = requests.post(f"{API_URL}/players/pay", json={"player_id": int(payer_dropdown.value), "amount": amount})
            if res.status_code == 200:
                show_toast(f"Pagamento de {amount}€ aceite!")
                payment_input.value = ""
                refresh_treasury()
            else:
                show_toast("Erro ao processar", "red")
        except:
            show_toast("Valor inválido", "red")

    btn_submit_payment = ft.ElevatedButton("Registar Pagamento 💰", on_click=submit_payment)

    # =========================================================================
    # UI: ADMIN
    # =========================================================================
    col_team_a = ft.Column()
    col_team_b = ft.Column()
    champion_dropdown = ft.Dropdown(label="Quem ganhou a época?")

    def refresh_admin_data():
        players = fetch_api("players/")

        col_team_a.controls.clear()
        col_team_b.controls.clear()
        team_a_checkboxes.clear()
        team_b_checkboxes.clear()
        champion_dropdown.options.clear()

        for p in players:
            # Checkboxes
            cb_a = ft.Checkbox(label=p['name'], value=False)
            cb_a.data = p['id']
            team_a_checkboxes.append(cb_a)
            col_team_a.controls.append(cb_a)

            cb_b = ft.Checkbox(label=p['name'], value=False)
            cb_b.data = p['id']
            team_b_checkboxes.append(cb_b)
            col_team_b.controls.append(cb_b)

            # Champion Dropdown
            champion_dropdown.options.append(ft.dropdown.Option(p['name']))

        page.update()

    result_dropdown = ft.Dropdown(
        label="Resultado",
        options=[
            ft.dropdown.Option("TEAM_A", "Vitória A"),
            ft.dropdown.Option("TEAM_B", "Vitória B"),
            ft.dropdown.Option("DRAW", "Empate")
        ]
    )

    # FIX: String color
    double_points_chk = ft.Checkbox(label="Pontos x2?", fill_color="yellow")

    def submit_game(e):
        ids_a = [c.data for c in team_a_checkboxes if c.value]
        ids_b = [c.data for c in team_b_checkboxes if c.value]

        if not ids_a or not ids_b or not result_dropdown.value:
            show_toast("Falta informação", "red")
            return

        try:
            payload = {
                "date": str(datetime.date.today()),
                "result": result_dropdown.value,
                "team_a_players": ids_a,
                "team_b_players": ids_b,
                "is_double_points": double_points_chk.value
            }
            requests.post(f"{API_URL}/matches/", json=payload)

            show_toast("Jogo Gravado! (-3€ a cada jogador)")
            refresh_treasury()
            refresh_leaderboard()

            # Reset inputs
            for c in team_a_checkboxes + team_b_checkboxes:
                c.value = False

        except:
            show_toast("Erro de conexão", "red")

    btn_save_game = ft.ElevatedButton("Gravar Jogo (Custa 3€)", on_click=submit_game)

    # Close Season Logic
    def close_season(e):
        if not champion_dropdown.value:
            show_toast("Escolhe o Campeão!", "red")
            return

        # Confirmation step
        if btn_close_season.text == "Fechar Época":
            btn_close_season.text = "Tens a Certeza?"
            btn_close_season.bgcolor = "orange" # FIX: String color
            page.update()
            return

        try:
            requests.post(
                f"{API_URL}/season/close",
                json={"champion_name": champion_dropdown.value, "season_name": "Época"}
            )
            show_toast("Época Fechada! Parabéns ao Campeão!")
            refresh_new_champions()
            refresh_leaderboard()

            # Reset button
            btn_close_season.text = "Fechar Época"
            btn_close_season.bgcolor = "red" # FIX: String color

        except:
            show_toast("Erro no servidor", "red")

    btn_close_season = ft.ElevatedButton("Fechar Época", bgcolor="red", color="white", on_click=close_season)

    # Create Player Logic
    new_player_input = ft.TextField(label="Novo Jogador")

    def create_player(e):
        if new_player_input.value:
            requests.post(f"{API_URL}/players/", json={"name": new_player_input.value})
            show_toast("Criado!")
            refresh_admin_data()
            new_player_input.value = ""

    btn_create_player = ft.ElevatedButton("Criar", on_click=create_player)

    # =========================================================================
    # LOGIN SYSTEM
    # =========================================================================
    password_input = ft.TextField(label="Senha", password=True)

    def handle_login(e):
        if password_input.value == ADMIN_PASSWORD:
            state["role"] = "admin"
            show_toast("Bem-vindo Admin 👑")
            build_layout()
        elif password_input.value == TREASURER_PASSWORD:
            state["role"] = "treasurer"
            show_toast("Bem-vindo Tesoureiro 💰")
            build_layout()
        else:
            show_toast("Senha errada", "red")

    login_view = ft.Column(
        [
            ft.Text("Área Restrita", size=20),
            password_input,
            ft.ElevatedButton("Entrar", on_click=handle_login),
            ft.TextButton("Voltar à Tabela", on_click=lambda e: build_layout())
        ],
        alignment=ft.MainAxisAlignment.CENTER
    )

    def navigate_to_login(e):
        page.clean()
        page.add(login_view)

    # =========================================================================
    # LAYOUT BUILDER
    # =========================================================================
    def build_layout():
        page.clean()

        # 1. Top Bar
        page.appbar = ft.AppBar(
            title=ft.Text("Terças FC"),
            center_title=False,
            bgcolor="surface_variant", # FIX: String color
            actions=[
                ft.IconButton(ft.Icons.PERSON, on_click=navigate_to_login, tooltip="Login Admin")
            ]
        )

        # 2. Define Tabs
        # Tab 1: Public League (Always visible)
        tabs_list = [
            ft.Tab(
                text="Liga",
                icon=ft.Icons.LEADERBOARD,
                content=ft.Column(
                    [
                        ft.Text("Classificação", size=20, weight="bold"),
                        ft.Row([leaderboard_table], scroll="always"),
                        rules_view
                    ],
                    scroll="auto"
                )
            )
        ]

        # Tab 2: Treasury (Admin/Treasurer)
        if state["role"] in ["admin", "treasurer"]:
            refresh_treasury()
            tabs_list.append(
                ft.Tab(
                    text="Tesouraria",
                    icon=ft.Icons.EURO,
                    content=ft.Column(
                        [
                            ft.Text("Gestão de Dívidas", size=20),
                            ft.Row([payer_dropdown, payment_input], alignment="center"),
                            btn_submit_payment,
                            ft.Divider(),
                            debt_list_view
                        ],
                        scroll="auto"
                    )
                )
            )

        # Tab 3: Admin (Admin only)
        if state["role"] == "admin":
            refresh_admin_data()
            tabs_list.append(
                ft.Tab(
                    text="Admin",
                    icon=ft.Icons.SETTINGS,
                    content=ft.Column(
                        [
                            ft.Text("Registar Jogo", weight="bold"),
                            ft.Container(
                                content=ft.Row(
                                    [
                                        ft.Column([ft.Text("Eq. A", color="green"), col_team_a]),
                                        ft.VerticalDivider(),
                                        ft.Column([ft.Text("Eq. B", color="blue"), col_team_b])
                                    ]
                                ),
                                height=200,
                                border=ft.border.all(1, "grey"),
                                padding=5
                            ),
                            result_dropdown,
                            double_points_chk,
                            btn_save_game,
                            ft.Divider(),

                            ft.Text("Gestão", weight="bold"),
                            ft.Row([new_player_input, btn_create_player]),
                            ft.Divider(),

                            ft.Text("Fim de Época", color="red"),
                            champion_dropdown,
                            btn_close_season
                        ],
                        scroll="auto"
                    )
                )
            )

        # 3. Add Tabs to Page
        t = ft.Tabs(selected_index=0, tabs=tabs_list, expand=True)
        page.add(t)

    # --- Start ---
    refresh_leaderboard()
    refresh_new_champions()
    build_layout()

# =============================================================================
# EXPOSE APP FOR RENDER (ASGI)
# =============================================================================
app = ft.app(target=main, export_asgi_app=True)