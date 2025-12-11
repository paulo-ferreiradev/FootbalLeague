import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';

/// Widget que mostra diferentes menus conforme o role do utilizador.
class RoleBasedMenu extends StatefulWidget {
  final void Function(String menu)? onMenuSelected;
  const RoleBasedMenu({Key? key, this.onMenuSelected}) : super(key: key);

  @override
  State<RoleBasedMenu> createState() => _RoleBasedMenuState();
}

class _RoleBasedMenuState extends State<RoleBasedMenu> {
  String? _role;

  @override
  void initState() {
    super.initState();
    _loadRole();
  }

  Future<void> _loadRole() async {
    final prefs = await SharedPreferences.getInstance();
    setState(() {
      _role = prefs.getString('role') ?? 'player';
    });
  }

  @override
  Widget build(BuildContext context) {
    if (_role == null) {
      return const Center(child: CircularProgressIndicator());
    }
    switch (_role) {
      case 'admin':
        return _AdminMenu(onMenuSelected: widget.onMenuSelected);
      case 'treasurer':
        return _TreasurerMenu(onMenuSelected: widget.onMenuSelected);
      default:
        return _PlayerMenu(onMenuSelected: widget.onMenuSelected);
    }
  }
}

class _AdminMenu extends StatelessWidget {
  final void Function(String menu)? onMenuSelected;
  const _AdminMenu({this.onMenuSelected});

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        ListTile(
          leading: const Icon(Icons.sports_soccer),
          title: const Text('Lançar Resultados'),
          onTap: () => onMenuSelected?.call('resultados'),
        ),
        ListTile(
          leading: const Icon(Icons.people),
          title: const Text('Gestão de Jogadores'),
          onTap: () => onMenuSelected?.call('jogadores'),
        ),
        ListTile(
          leading: const Icon(Icons.attach_money),
          title: const Text('Gestão Financeira'),
          onTap: () => onMenuSelected?.call('financeira'),
        ),
      ],
    );
  }
}

class _TreasurerMenu extends StatelessWidget {
  final void Function(String menu)? onMenuSelected;
  const _TreasurerMenu({this.onMenuSelected});

  @override
  Widget build(BuildContext context) {
    return ListTile(
      leading: const Icon(Icons.attach_money),
      title: const Text('Gestão Financeira'),
      onTap: () => onMenuSelected?.call('financeira'),
    );
  }
}

class _PlayerMenu extends StatelessWidget {
  final void Function(String menu)? onMenuSelected;
  const _PlayerMenu({this.onMenuSelected});

  @override
  Widget build(BuildContext context) {
    return ListTile(
      leading: const Icon(Icons.account_circle),
      title: const Text('Perfil'),
      onTap: () => onMenuSelected?.call('perfil'),
    );
  }
}
