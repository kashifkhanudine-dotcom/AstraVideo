import 'package:dio/dio.dart';
import 'package:flutter/material.dart';

void main() {
  runApp(const AstraVideoApp());
}

class AstraVideoApp extends StatelessWidget {
  const AstraVideoApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'AstraVideo',
      theme: ThemeData(
        brightness: Brightness.dark,
        scaffoldBackgroundColor: const Color(0xFF080A0F),
        colorScheme: const ColorScheme.dark(
          primary: Color(0xFF7C5CFC),
          secondary: Color(0xFF35C2FF),
          surface: Color(0xFF11141B),
        ),
        useMaterial3: true,
      ),
      home: const MainShell(),
    );
  }
}

class ApiService {
  ApiService()
      : _dio = Dio(BaseOptions(
          baseUrl: 'http://10.0.2.2:8000',
          connectTimeout: const Duration(seconds: 10),
          receiveTimeout: const Duration(seconds: 30),
        ));

  final Dio _dio;

  Future<Map<String, dynamic>> createGeneration({
    required String prompt,
    required int duration,
    required String resolution,
    required String aspectRatio,
  }) async {
    final response = await _dio.post('/v1/generations', data: {
      'prompt': prompt,
      'mode': 'text-to-video',
      'duration_seconds': duration,
      'resolution': resolution,
      'aspect_ratio': aspectRatio,
    });
    return Map<String, dynamic>.from(response.data as Map);
  }

  Future<List<Map<String, dynamic>>> getGenerations() async {
    final response = await _dio.get('/v1/generations');
    return (response.data as List)
        .map((item) => Map<String, dynamic>.from(item as Map))
        .toList();
  }
}

class MainShell extends StatefulWidget {
  const MainShell({super.key});

  @override
  State<MainShell> createState() => _MainShellState();
}

class _MainShellState extends State<MainShell> {
  int index = 0;

  @override
  Widget build(BuildContext context) {
    final pages = [
      HomeScreen(onCreate: () => setState(() => index = 1)),
      const CreateScreen(),
      const LibraryScreen(),
      const ProfileScreen(),
    ];

    return Scaffold(
      body: SafeArea(child: pages[index]),
      bottomNavigationBar: NavigationBar(
        selectedIndex: index,
        onDestinationSelected: (value) => setState(() => index = value),
        destinations: const [
          NavigationDestination(icon: Icon(Icons.home_outlined), selectedIcon: Icon(Icons.home), label: 'Home'),
          NavigationDestination(icon: Icon(Icons.auto_awesome_outlined), selectedIcon: Icon(Icons.auto_awesome), label: 'Crea'),
          NavigationDestination(icon: Icon(Icons.video_library_outlined), selectedIcon: Icon(Icons.video_library), label: 'Libreria'),
          NavigationDestination(icon: Icon(Icons.person_outline), selectedIcon: Icon(Icons.person), label: 'Profilo'),
        ],
      ),
    );
  }
}

class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key, required this.onCreate});

  final VoidCallback onCreate;

  @override
  Widget build(BuildContext context) {
    return ListView(
      padding: const EdgeInsets.all(20),
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            const Text('ASTRAVIDEO', style: TextStyle(fontSize: 20, fontWeight: FontWeight.w800)),
            Chip(label: const Text('⚡ 120'), backgroundColor: Theme.of(context).colorScheme.surface),
          ],
        ),
        const SizedBox(height: 30),
        const Text('Crea qualcosa di incredibile', style: TextStyle(fontSize: 30, fontWeight: FontWeight.bold)),
        const SizedBox(height: 10),
        const Text('Trasforma una semplice idea in un video AI pronto per TikTok, Reels e Shorts.'),
        const SizedBox(height: 24),
        FilledButton.icon(
          onPressed: onCreate,
          icon: const Icon(Icons.auto_awesome),
          label: const Padding(
            padding: EdgeInsets.symmetric(vertical: 16),
            child: Text('Genera video'),
          ),
        ),
        const SizedBox(height: 32),
        const Text('Stili', style: TextStyle(fontSize: 20, fontWeight: FontWeight.w700)),
        const SizedBox(height: 12),
        const Wrap(
          spacing: 10,
          runSpacing: 10,
          children: [
            Chip(label: Text('Cinematic')),
            Chip(label: Text('Realistic')),
            Chip(label: Text('Anime')),
            Chip(label: Text('Commercial')),
          ],
        ),
      ],
    );
  }
}

class CreateScreen extends StatefulWidget {
  const CreateScreen({super.key});

  @override
  State<CreateScreen> createState() => _CreateScreenState();
}

class _CreateScreenState extends State<CreateScreen> {
  final controller = TextEditingController();
  final api = ApiService();
  int duration = 5;
  String resolution = '720p';
  String ratio = '9:16';
  bool loading = false;
  String? message;

  Future<void> generate() async {
    if (controller.text.trim().length < 3) return;
    setState(() {
      loading = true;
      message = null;
    });
    try {
      final result = await api.createGeneration(
        prompt: controller.text.trim(),
        duration: duration,
        resolution: resolution,
        aspectRatio: ratio,
      );
      setState(() => message = 'Generazione avviata • ${result['credits_used']} crediti');
    } catch (e) {
      setState(() => message = 'Errore: $e');
    } finally {
      if (mounted) setState(() => loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return ListView(
      padding: const EdgeInsets.all(20),
      children: [
        const Text('Crea video', style: TextStyle(fontSize: 28, fontWeight: FontWeight.bold)),
        const SizedBox(height: 20),
        TextField(
          controller: controller,
          minLines: 5,
          maxLines: 8,
          decoration: InputDecoration(
            hintText: 'Descrivi il video che vuoi creare…',
            filled: true,
            fillColor: Theme.of(context).colorScheme.surface,
            border: OutlineInputBorder(borderRadius: BorderRadius.circular(16), borderSide: BorderSide.none),
          ),
        ),
        const SizedBox(height: 20),
        const Text('Durata'),
        const SizedBox(height: 8),
        SegmentedButton<int>(
          segments: const [ButtonSegment(value: 5, label: Text('5 sec')), ButtonSegment(value: 10, label: Text('10 sec'))],
          selected: {duration},
          onSelectionChanged: (values) => setState(() => duration = values.first),
        ),
        const SizedBox(height: 18),
        const Text('Qualità'),
        const SizedBox(height: 8),
        SegmentedButton<String>(
          segments: const [ButtonSegment(value: '720p', label: Text('720p')), ButtonSegment(value: '1080p', label: Text('1080p'))],
          selected: {resolution},
          onSelectionChanged: (values) => setState(() => resolution = values.first),
        ),
        const SizedBox(height: 18),
        const Text('Formato'),
        const SizedBox(height: 8),
        SegmentedButton<String>(
          segments: const [
            ButtonSegment(value: '9:16', label: Text('9:16')),
            ButtonSegment(value: '16:9', label: Text('16:9')),
            ButtonSegment(value: '1:1', label: Text('1:1')),
          ],
          selected: {ratio},
          onSelectionChanged: (values) => setState(() => ratio = values.first),
        ),
        const SizedBox(height: 28),
        FilledButton.icon(
          onPressed: loading ? null : generate,
          icon: loading
              ? const SizedBox(width: 18, height: 18, child: CircularProgressIndicator(strokeWidth: 2))
              : const Icon(Icons.auto_awesome),
          label: Padding(
            padding: const EdgeInsets.symmetric(vertical: 16),
            child: Text(loading ? 'Generazione…' : 'Genera'),
          ),
        ),
        if (message != null) ...[
          const SizedBox(height: 16),
          Text(message!),
        ],
      ],
    );
  }
}

class LibraryScreen extends StatefulWidget {
  const LibraryScreen({super.key});

  @override
  State<LibraryScreen> createState() => _LibraryScreenState();
}

class _LibraryScreenState extends State<LibraryScreen> {
  final api = ApiService();

  @override
  Widget build(BuildContext context) {
    return FutureBuilder<List<Map<String, dynamic>>>(
      future: api.getGenerations(),
      builder: (context, snapshot) {
        return RefreshIndicator(
          onRefresh: () async => setState(() {}),
          child: ListView(
            padding: const EdgeInsets.all(20),
            children: [
              const Text('Libreria', style: TextStyle(fontSize: 28, fontWeight: FontWeight.bold)),
              const SizedBox(height: 20),
              if (snapshot.connectionState == ConnectionState.waiting)
                const Center(child: CircularProgressIndicator())
              else if (snapshot.hasError)
                Text('Avvia il backend FastAPI e aggiorna.\n${snapshot.error}')
              else if ((snapshot.data ?? []).isEmpty)
                const Text('Nessun video ancora. Crea la tua prima generazione.')
              else
                ...snapshot.data!.map((item) => Card(
                      child: ListTile(
                        leading: const Icon(Icons.movie_outlined),
                        title: Text(item['prompt']?.toString() ?? ''),
                        subtitle: Text('${item['status']} • ${item['resolution']} • ${item['aspect_ratio']}'),
                        trailing: Text('${item['progress']}%'),
                      ),
                    )),
            ],
          ),
        );
      },
    );
  }
}

class ProfileScreen extends StatelessWidget {
  const ProfileScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return ListView(
      padding: const EdgeInsets.all(20),
      children: [
        const Text('Profilo', style: TextStyle(fontSize: 28, fontWeight: FontWeight.bold)),
        const SizedBox(height: 20),
        const Card(child: ListTile(leading: Icon(Icons.bolt), title: Text('Crediti'), trailing: Text('120'))),
        Card(
          child: ListTile(
            leading: const Icon(Icons.workspace_premium),
            title: const Text('AstraVideo Pro'),
            subtitle: const Text('1080p, niente watermark, priorità'),
            trailing: FilledButton(onPressed: () {}, child: const Text('Upgrade')),
          ),
        ),
        const Card(child: ListTile(leading: Icon(Icons.language), title: Text('Lingua'), trailing: Text('Italiano'))),
        const Card(child: ListTile(leading: Icon(Icons.privacy_tip_outlined), title: Text('Privacy'))),
        const Card(child: ListTile(leading: Icon(Icons.help_outline), title: Text('Supporto'))),
      ],
    );
  }
}
