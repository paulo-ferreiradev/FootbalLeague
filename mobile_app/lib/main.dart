import 'package:flutter/material.dart';
import 'screens/leaderboard_screen.dart';

void main() {
  runApp(const TercasFCApp());
}

class TercasFCApp extends StatelessWidget {
  const TercasFCApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Terças FC',
      debugShowCheckedModeBanner: false,
      // Tema Geral da App (Fica tudo centralizado aqui)
      theme: ThemeData.dark().copyWith(
        primaryColor: Colors.green,
        scaffoldBackgroundColor: const Color(0xFF121212),
        colorScheme: const ColorScheme.dark(
          primary: Colors.green,
          secondary: Colors.greenAccent,
        ),
      ),
      home: const LeaderboardScreen(),
    );
  }
}
