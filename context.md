Projeto: Terças FC - Football League Management App Arquitetura: Full Stack Monorepo (/backend em Python, /mobile_app em Flutter)

🛠️ Tech Stack Atual
Backend (API):

Linguagem: Python (FastAPI).

ORM: SQLAlchemy (Abordagem Code-First).

Base de Dados: PostgreSQL (Supabase).

Hospedagem: Render.com.

Libs principais: pydantic, uvicorn, python-multipart.

Segurança: Autenticação simples (Username/Password na BD), Roles ('admin', 'player', 'treasurer').

Frontend (Mobile):

Framework: Flutter (Dart).

Estado/Lógica: StatefulWidgets, FutureBuilder.

Libs principais: http (API), shared_preferences (Sessão/Login), async (Timers).

Plataforma alvo: Android (APK) e Web (Chrome para testes).

✅ O Que Já Foi Implementado (Funcional)

1. Estrutura de Pastas (Monorepo):

backend/: Contém src/main.py, models.py, database.py.

mobile_app/: Contém lib/models, lib/screens, lib/services, lib/widgets.

2. Backend (Lógica de Negócio):

Gestão de Jogos Automática: O sistema deteta se existe jogo agendado. Se não, cria automaticamente um jogo para a próxima Terça-feira às 22:30.

Janela de Convocatória Inteligente: A API calcula se as inscrições estão abertas baseada em constantes (OPEN_DAY, CLOSE_DAY).

Regra atual: Abre Quarta-feira 09:00, Fecha Terça-feira 19:00.

Gestão de Presenças: Endpoint para marcar "Vou" (going) ou "Não Vou" (not_going), ligado ao ID do jogador.

Tabela Classificativa: Algoritmo que calcula pontos (V=3, E=1, D=0), golos e forma (W/D/L) baseado no histórico de jogos fechados.

Login: Validação de username/password e retorno de Role e ID.

3. Frontend (UI/UX):

Login Screen: Persistência de sessão (Auto-login se já tiver token guardado).

Leaderboard Screen: Mostra a tabela classificativa atualizada via API.

Match Card (Widget Inteligente):

Mostra o próximo jogo.

Timer Decrescente: Contador em tempo real até ao fecho da convocatória.

Estados: "Aberto" (Botões VOU/NÃO VOU ativos) vs "Fechado" (Mensagem informativa).

Feedback visual (Snackbars) ao votar.

🚀 Roadmap: O Que Falta Implementar (Objetivos Futuros)
Mantendo a arquitetura atual:

1. Área de Admin (Prioridade Máxima):

Criar lógica no Flutter para mostrar menus diferentes baseados no role do utilizador (Admin vs Player).

Ecrã para Lançar Resultados: Selecionar o jogo, inserir golos ou quem ganhou, e fechar o jogo (status: 'concluido') para atualizar a tabela.

Ecrã para Gestão Financeira: Ver quem pagou a mensalidade ou o jogo avulso (Tesoureiro).

2. Perfil de Jogador:

Ecrã para o jogador ver o seu histórico pessoal (jogos, vitórias, saldo financeiro).

Opção para alterar a password.

3. Notificações (Avançado):

Integrar Firebase Cloud Messaging (FCM).

Backend enviar notificação push automática quando a convocatória abre (Quarta-feira) e avisos de "Última Hora" (Terça à tarde).

4. Melhorias Visuais:

Skeleton loaders enquanto os dados carregam.

Animações na tabela classificativa.
