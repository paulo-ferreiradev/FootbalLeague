import flet as ft
import requests
import datetime
import threading
import time

# =============================================================================
# CONFIGURATION
# =============================================================================
# Production API URL (Render)
API_URL = "https://tercas-fc-api.onrender.com"

# Access Credentials (Role-based)
# In a large scale production environment, consider using Environment Variables.
ADMIN_PASSWORD = "1234"
TREASURER_PASSWORD = "money"

# =============================================================================
# MAIN APPLICATION
# =============================================================================
def main(page: ft.Page):
    # --- Page Configuration ---
    page.title = "Terças FC"
    page.theme_mode = ft.ThemeMode.DARK
    page.scroll = ft.ScrollMode.AUTO
    page.padding = 10

    # --- Application State ---
    state = {
        "role": None,  # Can be 'admin', 'treasurer', or None (Public)
    }

    # Global references for team selection
    team_a_checkboxes = []
    team_b_checkboxes = []

    # =========================================================================
    # HELPER FUNCTIONS
    # =========================================================================
    def show_toast(message: str, color: str = "green"):
        """Displays a temporary snackbar message to the user."""
        page.snack_bar = ft.SnackBar(
            content=ft.Text(message),
            bgcolor=color
        )
        page.snack_bar.open = True
        page.update()

    def fetch_api(endpoint: str):
        """Safe wrapper for API GET requests."""
        try:
            response = requests.get(f"{API_URL}/{endpoint}")
            return response.json() if response.status_code == 200 else []
        except Exception as e:
            print(f"API Error: {e}")
            return []

    # =========================================================================
    # UI COMPONENT: LEADERBOARD TAB
    # =========================================================================

    # 1. Main Data Table
    leaderboard_table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Pos")),
            ft.DataColumn(ft.Text("Nome")),
            ft.DataColumn(ft.Text("P"), numeric=True, tooltip="Points"),
            ft.DataColumn(ft.Text("J"), numeric=True, tooltip="Games"),
            ft.DataColumn(ft.Text("V"), numeric=True, tooltip="Wins"),
            ft.DataColumn(ft.Text("E"), numeric=True, tooltip="Draws"),
            ft.DataColumn(ft.Text("D"), numeric=True, tooltip="Losses"),
        ],
        rows=[],
        column_spacing=5
    )

    def refresh_leaderboard():
        """Fetches table data and redraws the rows."""
        data = fetch_api("table/")
        leaderboard_table.rows.clear()

        for i, player in enumerate(data):
            leaderboard_table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(i + 1))),
                        ft.DataCell(ft.Text(player['name'], weight=ft.FontWeight.BOLD, size=13)),
                        ft.DataCell(ft.Text(str(player['points']), color=ft.colors.YELLOW, weight=ft.FontWeight.BOLD)),
                        ft.DataCell(ft.Text(str(player['games_played']))),
                        ft.DataCell(ft.Text(str(player['wins']), color=ft.colors.GREEN)),
                        ft.DataCell(ft.Text(str(player['draws']), color=ft.colors.BLUE)),
                        ft.DataCell(ft.Text(str(player['losses']), color=ft.colors.RED)),
                    ]
                )
            )
        page.update()

    # Background Thread for Auto-Update (Every 15 seconds)
    def auto_update_loop():
        while True:
            time.sleep(15)
            try:
                refresh_leaderboard()
            except Exception:
                pass

    # Start the daemon thread
    threading.Thread(target=auto_update_loop, daemon=True).start()

    # 2. History & Rules Section

    # Dynamic Container for new champions added via App
    dynamic_champions_container = ft.Column()

    def refresh_dynamic_champions():
        """Fetches champions from DB and displays them."""
        champions = fetch_api("champions/")
        dynamic_champions_container.controls.clear()

        if champions:
            dynamic_champions_container.controls.append(
                ft.Text("NOVOS CAMPEÕES (App):", weight=ft.FontWeight.BOLD, size=12, color=ft.colors.GREEN)
            )
            for c in champions:
                trophies = "🏆" * c['titles']
                dynamic_champions_container.controls.append(
                    ft.Row(
                        [
                            ft.Text(f"{c['name'].upper()} =", weight=ft.FontWeight.BOLD),
                            ft.Text(trophies)
                        ],
                        spacing=5
                    )
                )
        page.update()

    # Static History Container (Hardcoded legacy data)
    static_history_view = ft.Column(
        controls=[
            ft.Divider(),
            ft.Text("TÍTULOS DE CAMPEÃO (Pavilhão Sécil & Pavilhão Escola Luisa Todi):", weight=ft.FontWeight.BOLD, size=12),
            ft.Row([ft.Text("RAFAEL =", weight=ft.FontWeight.BOLD), ft.Text("🏆")], spacing=5),
            ft.Row([ft.Text("RENATO =", weight=ft.FontWeight.BOLD), ft.Text("🏆")], spacing=5),
            ft.Row([ft.Text("RUI =", weight=ft.FontWeight.BOLD), ft.Text("🏆")], spacing=5),
            ft.Row([ft.Text("ABDUL =", weight=ft.FontWeight.BOLD), ft.Text("🏆")], spacing=5),
            ft.Row([ft.Text("NUNO TAVARES =", weight=ft.FontWeight.BOLD), ft.Text("🏆🏆")], spacing=5),
            ft.Row([ft.Text("CASCA =", weight=ft.FontWeight.BOLD), ft.Text("🏆🏆")], spacing=5),
            ft.Row([ft.Text("JOÃO SILVA =", weight=ft.FontWeight.BOLD), ft.Text("🏆🏆")], spacing=5),
            ft.Row([ft.Text("JOÃO GALOPIM =", weight=ft.FontWeight.BOLD), ft.Text("🏆")], spacing=5),

            # Append dynamic champions below static ones
            dynamic_champions_container
        ],
        spacing=2
    )

    rules_view = ft.Column(
        controls=[
            ft.Divider(),
            ft.Text("VITÓRIA = 3 PONTOS"),
            ft.Text("EMPATE = 2 PONTOS"),
            ft.Text("DERROTA = 1 PONTO"),
            ft.Container(height=10),
            ft.Text("* PENALIZAÇÃO DE -3 PONTOS POR FALTA DE COMPARÊNCIA", size=12),
            ft.Text("1º CRITÉRIO DE DESEMPATE: MAIOR NUMERO DE JOGOS REALIZADOS", size=12, weight=ft.FontWeight.BOLD),
            ft.Text("SEMANALMENTE AS EQUIPAS SÃO ESCOLHIDAS PELO 1º E 2º CLASSIFICADOS", size=12),
            ft.Text("SÓ ENTRA NA TABELA QUEM TIVER PELO MENOS 50% DO TOTAL JOGOS REALIZADOS", size=12),

            static_history_view
        ],
        spacing=5
    )

    # =========================================================================
    # UI COMPONENT: TREASURY TAB
    # =========================================================================
    debt_list_view = ft.Column()
    payment_amount_input = ft.TextField(label="Valor (€)", width=100, keyboard_type=ft.KeyboardType.NUMBER)
    payer_dropdown = ft.Dropdown(label="Quem pagou?", expand=True)

    def refresh_treasury_data():
        """Fetches all players and calculates balances."""
        players = fetch_api("players/all")

        debt_list_view.controls.clear()
        payer_dropdown.options.clear()

        total_debt = 0.0

        for p in players:
            # Populate dropdown
            payer_dropdown.options.append(ft.dropdown.Option(key=str(p['id']), text=p['name']))

            # Calculate Visuals
            balance = p['balance']
            color = ft.colors.RED if balance < 0 else ft.colors.GREEN

            if balance < 0:
                total_debt += balance

            debt_list_view.controls.append(
                ft.Row(
                    [
                        ft.Text(p['name'], weight=ft.FontWeight.BOLD),
                        ft.Text(f"{balance:.2f}€", color=color, weight=ft.FontWeight.BOLD)
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                )
            )

        debt_list_view.controls.append(ft.Divider())
        debt_list_view.controls.append(
            ft.Text(f"Total em Falta: {total_debt:.2f}€", color=ft.colors.RED, weight=ft.FontWeight.BOLD)
        )
        page.update()

    def submit_payment(e):
        if not payer_dropdown.value or not payment_amount_input.value:
            return

        try:
            amount = float(payment_amount_input.value)
            payload = {
                "player_id": int(payer_dropdown.value),
                "amount": amount
            }

            response = requests.post(f"{API_URL}/players/pay", json=payload)

            if response.status_code == 200:
                show_toast(f"Pagamento de {amount}€ aceite!", "green")
                payment_amount_input.value = ""
                refresh_treasury_data()
            else:
                show_toast("Erro ao processar pagamento", "red")

        except ValueError:
            show_toast("Valor inválido", "red")
        except Exception as err:
            show_toast(f"Erro de conexão: {err}", "red")

    btn_submit_payment = ft.ElevatedButton("Registar Pagamento 💰", on_click=submit_payment)

    # =========================================================================
    # UI COMPONENT: ADMIN TAB
    # =========================================================================
    col_team_a = ft.Column()
    col_team_b = ft.Column()
    champion_dropdown = ft.Dropdown(label="Quem ganhou a época?")

    def refresh_admin_data():
        """Loads players for game registration and champion selection."""
        players = fetch_api("players/")

        # Reset controls
        col_team_a.controls.clear()
        col_team_b.controls.clear()
        team_a_checkboxes.clear()
        team_b_checkboxes.clear()
        champion_dropdown.options.clear()

        for p in players:
            # Team A Checkbox
            cb_a = ft.Checkbox(label=p['name'], value=False)
            cb_a.data = p['id'] # Store ID in the control
            team_a_checkboxes.append(cb_a)
            col_team_a.controls.append(cb_a)

            # Team B Checkbox
            cb_b = ft.Checkbox(label=p['name'], value=False)
            cb_b.data = p['id']
            team_b_checkboxes.append(cb_b)
            col_team_b.controls.append(cb_b)

            # Champion Dropdown
            champion_dropdown.options.append(ft.dropdown.Option(p['name']))

        page.update()

    # Game Inputs
    result_dropdown = ft.Dropdown(
        label="Resultado",
        options=[
            ft.dropdown.Option("TEAM_A", "Vitória A"),
            ft.dropdown.Option("TEAM_B", "Vitória B"),
            ft.dropdown.Option("DRAW", "Empate")
        ]
    )

    double_points_check = ft.Checkbox(label="Pontos x2?", fill_color=ft.colors.YELLOW)

    def submit_game(e):
        ids_a = [cb.data for cb in team_a_checkboxes if cb.value]
        ids_b = [cb.data for cb in team_b_checkboxes if cb.value]

        if not ids_a or not ids_b:
            show_toast("Selecione jogadores em ambas as equipas", "red")
            return

        if not result_dropdown.value:
            show_toast("Indique o resultado", "red")
            return

        try:
            payload = {
                "date": str(datetime.date.today()),
                "result": result_dropdown.value,
                "team_a_players": ids_a,
                "team_b_players": ids_b,
                "is_double_points": double_points_check.value
            }

            requests.post(f"{API_URL}/matches/", json=payload)

            show_toast("Jogo Gravado! (-3€ a cada jogador)", "green")

            # Reset UI
            refresh_treasury_data()
            refresh_leaderboard()
            for cb in team_a_checkboxes + team_b_checkboxes:
                cb.value = False
            page.update()

        except Exception as err:
            show_toast(f"Erro ao gravar: {err}", "red")

    btn_submit_game = ft.ElevatedButton("Gravar Jogo (Custa 3€)", on_click=submit_game)

    # Season Management
    def close_season_handler(e):
        if not champion_dropdown.value:
            show_toast("Escolha o Campeão primeiro!", "red")
            return

        # Confirmation Logic
        if btn_close_season.text == "Fechar Época":
            btn_close_season.text = "Tens a Certeza?"
            btn_close_season.bgcolor = ft.colors.ORANGE
            page.update()
            return

        try:
            requests.post(
                f"{API_URL}/season/close",
                json={"champion_name": champion_dropdown.value, "season_name": "Época"}
            )

            show_toast("Época Fechada! Troféu entregue 🏆", "green")

            refresh_dynamic_champions()
            refresh_leaderboard()

            # Reset Button
            btn_close_season.text = "Fechar Época"
            btn_close_season.bgcolor = ft.colors.RED
            page.update()

        except Exception as err:
            show_toast(f"Erro: {err}", "red")

    btn_close_season = ft.ElevatedButton(
        "Fechar Época",
        bgcolor=ft.colors.RED,
        color=ft.colors.WHITE,
        on_click=close_season_handler
    )

    # Player Creation
    new_player_input = ft.TextField(label="Novo Jogador")

    def create_player_handler(e):
        if new_player_input.value:
            try:
                requests.post(f"{API_URL}/players/", json={"name": new_player_input.value})
                show_toast("Criado!", "green")
                refresh_admin_data()
                new_player_input.value = ""
            except:
                show_toast("Erro: Jogador já existe?", "red")

    btn_create_player = ft.ElevatedButton("Criar", on_click=create_player_handler)

    # =========================================================================
    # LOGIN SYSTEM
    # =========================================================================
    password_input = ft.TextField(label="Senha", password=True)

    def login_handler(e):
        entered_pass = password_input.value

        if entered_pass == ADMIN_PASSWORD:
            state["role"] = "admin"
            show_toast("Bem-vindo Admin 👑")
            build_main_layout()

        elif entered_pass == TREASURER_PASSWORD:
            state["role"] = "treasurer"
            show_toast("Bem-vindo Tesoureiro 💰")
            build_main_layout()

        else:
            show_toast("Senha errada", "red")

    login_view = ft.Column(
        [
            ft.Text("Área Restrita", size=20, weight=ft.FontWeight.BOLD),
            password_input,
            ft.ElevatedButton("Entrar", on_click=login_handler),
            ft.TextButton("Voltar à Tabela", on_click=lambda e: build_main_layout())
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER
    )

    def go_to_login(e):
        page.clean()
        page.add(login_view)

    # =========================================================================
    # LAYOUT BUILDER
    # =========================================================================
    def build_main_layout():
        page.clean()

        # 1. Top Bar with Login Button
        page.appbar = ft.AppBar(
            title=ft.Text("Terças FC"),
            center_title=False,
            bgcolor=ft.colors.SURFACE_VARIANT,
            actions=[
                ft.IconButton(
                    ft.Icons.PERSON,
                    on_click=go_to_login,
                    tooltip="Login Admin"
                )
            ]
        )

        # 2. Define Tabs
        # Tab 1: Public League View (Always visible)
        tabs_list = [
            ft.Tab(
                text="Liga",
                icon=ft.Icons.LEADERBOARD,
                content=ft.Column(
                    [
                        ft.Text("Classificação", size=20, weight=ft.FontWeight.BOLD),
                        ft.Row([leaderboard_table], scroll=ft.ScrollMode.ALWAYS),
                        rules_view
                    ],
                    scroll=ft.ScrollMode.AUTO
                )
            )
        ]

        # Tab 2: Treasury (Visible for Admin & Treasurer)
        if state["role"] in ["admin", "treasurer"]:
            refresh_treasury_data()
            tabs_list.append(
                ft.Tab(
                    text="Tesouraria",
                    icon=ft.Icons.EURO,
                    content=ft.Column(
                        [
                            ft.Text("Gestão de Dívidas", size=20),
                            ft.Row([payer_dropdown, payment_amount_input], alignment=ft.MainAxisAlignment.CENTER),
                            btn_submit_payment,
                            ft.Divider(),
                            debt_list_view
                        ],
                        scroll=ft.ScrollMode.AUTO
                    )
                )
            )

        # Tab 3: Admin (Visible for Admin only)
        if state["role"] == "admin":
            refresh_admin_data()
            tabs_list.append(
                ft.Tab(
                    text="Admin",
                    icon=ft.Icons.SETTINGS,
                    content=ft.Column(
                        [
                            ft.Text("Registar Jogo", weight=ft.FontWeight.BOLD),
                            ft.Container(
                                content=ft.Row(
                                    [
                                        ft.Column([ft.Text("Eq. A", color=ft.colors.GREEN), col_team_a]),
                                        ft.VerticalDivider(),
                                        ft.Column([ft.Text("Eq. B", color=ft.colors.BLUE), col_team_b])
                                    ]
                                ),
                                height=200,
                                border=ft.border.all(1, "grey"),
                                padding=5
                            ),
                            result_dropdown,
                            double_points_check,
                            btn_submit_game,
                            ft.Divider(),

                            ft.Text("Gestão", weight=ft.FontWeight.BOLD),
                            ft.Row([new_player_input, btn_create_player]),
                            ft.Divider(),

                            ft.Text("Fim de Época", color=ft.colors.RED),
                            champion_dropdown,
                            btn_close_season
                        ],
                        scroll=ft.ScrollMode.AUTO
                    )
                )
            )

        # 3. Add Tabs to Page
        tabs_control = ft.Tabs(selected_index=0, tabs=tabs_list, expand=True)
        page.add(tabs_control)

    # --- Initial Execution ---
    refresh_leaderboard()
    refresh_dynamic_champions()
    build_main_layout()

# =============================================================================
# EXPOSE APP FOR RENDER (ASGI)
# =============================================================================
app = ft.app(target=main, export_asgi_app=True)