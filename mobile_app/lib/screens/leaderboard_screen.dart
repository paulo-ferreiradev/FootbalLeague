import 'package:flutter/material.dart';
import '../models/player.dart';
import '../services/api_service.dart';

class LeaderboardScreen extends StatefulWidget {
  const LeaderboardScreen({super.key});

  @override
  State<LeaderboardScreen> createState() => _LeaderboardScreenState();
}

class _LeaderboardScreenState extends State<LeaderboardScreen> {
  late Future<List<Player>> futurePlayers;
  final ApiService api = ApiService();

  @override
  void initState() {
    super.initState();
    // Initiate the request right after screen opens
    futurePlayers = api.getLeaderboard();
  }

  void _refresh() {
    setState(() {
      futurePlayers = api.getLeaderboard();
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text(
          "Classificação 🏆",
          style: TextStyle(fontWeight: FontWeight.bold),
        ),
        backgroundColor: Colors.green[900],
        actions: [
          IconButton(icon: const Icon(Icons.refresh), onPressed: _refresh),
        ],
      ),
      body: FutureBuilder<List<Player>>(
        future: futurePlayers,
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Center(child: CircularProgressIndicator());
          } else if (snapshot.hasError) {
            return Center(child: Text("Erro: ${snapshot.error}"));
          } else if (!snapshot.hasData || snapshot.data!.isEmpty) {
            return const Center(child: Text("Sem dados disponíveis."));
          }

          return SingleChildScrollView(
            scrollDirection: Axis.vertical,
            child: SingleChildScrollView(
              scrollDirection: Axis.horizontal,
              child: DataTable(
                columnSpacing: 20,
                headingRowColor: MaterialStateProperty.all(Colors.grey[900]),
                columns: const [
                  DataColumn(
                    label: Text(
                      '#',
                      style: TextStyle(fontWeight: FontWeight.bold),
                    ),
                  ),
                  DataColumn(
                    label: Text(
                      'Nome',
                      style: TextStyle(fontWeight: FontWeight.bold),
                    ),
                  ),
                  DataColumn(
                    label: Text(
                      'P',
                      style: TextStyle(
                        fontWeight: FontWeight.bold,
                        color: Colors.yellow,
                      ),
                    ),
                  ),
                  DataColumn(
                    label: Text(
                      'J',
                      style: TextStyle(fontWeight: FontWeight.bold),
                    ),
                  ),
                  DataColumn(
                    label: Text('V', style: TextStyle(color: Colors.green)),
                  ),
                  DataColumn(
                    label: Text('E', style: TextStyle(color: Colors.blue)),
                  ),
                  DataColumn(
                    label: Text('D', style: TextStyle(color: Colors.red)),
                  ),
                ],
                rows: List<DataRow>.generate(snapshot.data!.length, (index) {
                  final player = snapshot.data![index];
                  final nameDisplay = player.isFixed
                      ? "${player.name} (F)"
                      : player.name;

                  return DataRow(
                    cells: [
                      DataCell(Text((index + 1).toString())),
                      DataCell(
                        Text(
                          nameDisplay,
                          style: const TextStyle(fontWeight: FontWeight.bold),
                        ),
                      ),
                      DataCell(
                        Text(
                          player.points.toString(),
                          style: const TextStyle(
                            color: Colors.yellow,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ),
                      DataCell(Text(player.games_played.toString())),
                      DataCell(
                        Text(
                          player.wins.toString(),
                          style: const TextStyle(color: Colors.green),
                        ),
                      ),
                      DataCell(
                        Text(
                          player.draws.toString(),
                          style: const TextStyle(color: Colors.blue),
                        ),
                      ),
                      DataCell(
                        Text(
                          player.losses.toString(),
                          style: const TextStyle(color: Colors.red),
                        ),
                      ),
                    ],
                  );
                }),
              ),
            ),
          );
        },
      ),
    );
  }
}
