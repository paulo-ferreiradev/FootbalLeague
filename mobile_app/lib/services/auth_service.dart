import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';
import 'api_service.dart';

class AuthService {
  // Guardar dados no telemóvel
  Future<void> saveUserSession(int id, String name, String role) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setInt('userId', id);
    await prefs.setString('userName', name);
    await prefs.setString('userRole', role);
    await prefs.setBool('isLoggedIn', true);
  }

  // Verificar se já está logado
  Future<Map<String, dynamic>?> getUserSession() async {
    final prefs = await SharedPreferences.getInstance();
    if (prefs.getBool('isLoggedIn') == true) {
      return {
        'id': prefs.getInt('userId'),
        'name': prefs.getString('userName'),
        'role': prefs.getString('userRole'),
      };
    }
    return null;
  }

  // Fazer Login na API
  Future<bool> login(String username, String password) async {
    try {
      final response = await http.post(
        Uri.parse('${ApiService.baseUrl}/login'),
        headers: {"Content-Type": "application/json"},
        body: jsonEncode({"username": username, "password": password}),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        if (data['success'] == true) {
          // Guardar na memória
          await saveUserSession(data['player_id'], data['name'], data['role']);
          return true;
        }
      }
      return false;
    } catch (e) {
      print("Erro login: $e");
      return false;
    }
  }

  // Sair
  Future<void> logout() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.clear();
  }
}
