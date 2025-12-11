import "dart:convert";
import "package:http/http.dart" as http;
import "../models/player.dart";

class ApiService {
  // Link of my API
  static const String baseUrl = "https://tercas-fc-api.onrender.com";

  Future<List<Player>> getLeaderboard() async {
    try {
      final responde = await http.get(Uri.parse("$baseUrl/table"));

      if (responde.statusCode == 200) {
        List<dynamic> body = json.decode(responde.body);
        // Convert json list in a list of player objects
        return body.map((item) => Player.fromJson(item)).toList();
      } else {
        throw Exception("Falha ao carregar tabela: ${responde.statusCode}");
      }
    } catch (e) {
      throw Exception("Erro de conexão: $e");
    }
  }
}
