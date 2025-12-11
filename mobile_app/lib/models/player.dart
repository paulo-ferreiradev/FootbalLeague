class Player {
  final int id;
  final String name;
  final bool isFixed;
  final int points;
  final int games_played;
  final int wins;
  final int draws;
  final int losses;

  Player({
    required this.id,
    required this.name,
    required this.isFixed,
    required this.points,
    required this.games_played,
    required this.wins,
    required this.draws,
    required this.losses,
  });

  // Transform JSON in a player
  factory Player.fromJson(Map<String, dynamic> json) {
    return Player(
      id: json["id"],
      name: json["name"],
      isFixed: json["is_fixed"] ?? false, // Null protection
      points: json["points"] ?? 0,
      games_played: json["games_played"] ?? 0,
      wins: json["wins"] ?? 0,
      draws: json["draws"] ?? 0,
      losses: json["losses"] ?? 0,
    );
  }
}
