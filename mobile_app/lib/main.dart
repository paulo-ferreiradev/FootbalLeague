import 'package:flutter/material.dart';
import 'screens/login_screen.dart'; // <--- MUDANÇA 1

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
      theme: ThemeData.dark().copyWith(
        primaryColor: Colors.green,
        scaffoldBackgroundColor: const Color(0xFF121212),
        colorScheme: const ColorScheme.dark(
          primary: Colors.green,
          secondary: Colors.greenAccent,
        ),
      ),
      home: const LoginScreen(), // <--- MUDANÇA 2 (Começa aqui!)
    );
  }
}
