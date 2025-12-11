import 'package:flutter/material.dart';
import '../models/match.dart';
import '../services/api_service.dart';
import '../services/auth_service.dart'; // <--- Precisamos disto para saber quem tu és

class MatchCard extends StatelessWidget {
  final Match match;

  // Callback para avisar o ecrã principal para atualizar os números
  final VoidCallback? onUpdate;

  const MatchCard({super.key, required this.match, this.onUpdate});

  // Função que trata do clique
  void _vote(BuildContext context, String status) async {
    // 1. Quem sou eu?
    final user = await AuthService().getUserSession();
    if (user == null) return; // Se não tiver logado, não faz nada (segurança)

    // 2. Enviar voto
    final api = ApiService();
    final success = await api.updateAttendance(match.id, user['id'], status);

    // 3. Feedback visual
    if (success) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(
            status == 'going'
                ? "Confirmado! Vamos a isso! ⚽"
                : "Falhaste a convocatória. 😢",
          ),
          backgroundColor: status == 'going' ? Colors.green : Colors.red,
          duration: const Duration(seconds: 2),
        ),
      );
      // Pede para atualizar a tabela/contadores se possível
      if (onUpdate != null) onUpdate!();
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text("Erro ao guardar. Verifica a internet.")),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    // Texto de estado
    String statusText = match.isOpen
        ? "Convocatória Aberta 🟢"
        : "Convocatória Fechada 🔴";

    return Container(
      margin: const EdgeInsets.all(16),
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [Colors.green[900]!, Colors.black],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(20),
        boxShadow: [
          BoxShadow(
            color: Colors.green.withOpacity(0.3),
            blurRadius: 10,
            offset: const Offset(0, 5),
          ),
        ],
      ),
      child: Column(
        children: [
          Text(
            statusText,
            style: const TextStyle(
              color: Colors.white54,
              fontSize: 12,
              fontWeight: FontWeight.bold,
              letterSpacing: 2,
            ),
          ),
          const SizedBox(height: 10),

          // Detalhes do Jogo
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    match.date,
                    style: const TextStyle(
                      color: Colors.white,
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  Text(
                    "${match.location} • ${match.opponent}",
                    style: const TextStyle(color: Colors.grey, fontSize: 13),
                  ),
                ],
              ),
              Container(
                padding: const EdgeInsets.symmetric(
                  horizontal: 12,
                  vertical: 6,
                ),
                decoration: BoxDecoration(
                  color: Colors.white.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(10),
                ),
                child: Text(
                  match.time,
                  style: const TextStyle(
                    color: Colors.yellow,
                    fontSize: 22,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
            ],
          ),
          const Divider(color: Colors.white24, height: 30),

          // Botões de Ação
          if (!match.isOpen)
            Container(
              padding: const EdgeInsets.all(10),
              decoration: BoxDecoration(
                color: Colors.white10,
                borderRadius: BorderRadius.circular(10),
              ),
              child: const Text(
                "Inscrições encerradas.",
                style: TextStyle(color: Colors.white70),
              ),
            )
          else
            Row(
              children: [
                Expanded(
                  child: ElevatedButton.icon(
                    onPressed: () => _vote(context, 'going'), // <--- VOU
                    icon: const Icon(Icons.check_circle, color: Colors.white),
                    label: const Text(
                      "VOU",
                      style: TextStyle(color: Colors.white),
                    ),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.green[700],
                    ),
                  ),
                ),
                const SizedBox(width: 10),
                Expanded(
                  child: ElevatedButton.icon(
                    onPressed: () =>
                        _vote(context, 'not_going'), // <--- NÃO VOU
                    icon: const Icon(Icons.cancel, color: Colors.white),
                    label: const Text(
                      "NÃO",
                      style: TextStyle(color: Colors.white),
                    ),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.red[900],
                    ),
                  ),
                ),
              ],
            ),

          const SizedBox(height: 10),
          Text(
            "${match.confirmedPlayers} Jogadores confirmados",
            style: const TextStyle(
              color: Colors.grey,
              fontSize: 12,
              fontStyle: FontStyle.italic,
            ),
          ),
        ],
      ),
    );
  }
}
