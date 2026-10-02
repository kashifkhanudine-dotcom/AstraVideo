import 'package:firebase_auth/firebase_auth.dart';
import 'package:firebase_core/firebase_core.dart';
import 'package:flutter/material.dart';

const firebaseEnabled = bool.fromEnvironment('ENABLE_FIREBASE', defaultValue: false);

Future<void> initializeFirebaseIfEnabled() async {
  if (firebaseEnabled) {
    await Firebase.initializeApp();
  }
}

class AuthGate extends StatelessWidget {
  const AuthGate({super.key, required this.child});

  final Widget child;

  @override
  Widget build(BuildContext context) {
    if (!firebaseEnabled) return child;

    return StreamBuilder<User?>(
      stream: FirebaseAuth.instance.authStateChanges(),
      builder: (context, snapshot) {
        if (snapshot.connectionState == ConnectionState.waiting) {
          return const Scaffold(body: Center(child: CircularProgressIndicator()));
        }
        return snapshot.data == null ? const LoginScreen() : child;
      },
    );
  }
}

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final emailController = TextEditingController();
  final passwordController = TextEditingController();
  bool loading = false;
  String? error;

  Future<void> _run(Future<UserCredential> Function() action) async {
    setState(() {
      loading = true;
      error = null;
    });
    try {
      await action();
    } on FirebaseAuthException catch (e) {
      setState(() => error = e.message ?? e.code);
    } catch (e) {
      setState(() => error = e.toString());
    } finally {
      if (mounted) setState(() => loading = false);
    }
  }

  Future<void> signInEmail() => _run(() => FirebaseAuth.instance.signInWithEmailAndPassword(
        email: emailController.text.trim(),
        password: passwordController.text,
      ));

  Future<void> createAccount() => _run(() => FirebaseAuth.instance.createUserWithEmailAndPassword(
        email: emailController.text.trim(),
        password: passwordController.text,
      ));

  Future<void> signInGoogle() => _run(() => FirebaseAuth.instance.signInWithProvider(GoogleAuthProvider()));

  Future<void> signInApple() => _run(() => FirebaseAuth.instance.signInWithProvider(AppleAuthProvider()));

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        child: ListView(
          padding: const EdgeInsets.all(24),
          children: [
            const SizedBox(height: 48),
            const Icon(Icons.auto_awesome, size: 54),
            const SizedBox(height: 18),
            const Text('AstraVideo', textAlign: TextAlign.center, style: TextStyle(fontSize: 32, fontWeight: FontWeight.bold)),
            const SizedBox(height: 8),
            const Text('Accedi per creare e salvare i tuoi video AI.', textAlign: TextAlign.center),
            const SizedBox(height: 32),
            TextField(
              controller: emailController,
              keyboardType: TextInputType.emailAddress,
              decoration: const InputDecoration(labelText: 'Email', border: OutlineInputBorder()),
            ),
            const SizedBox(height: 14),
            TextField(
              controller: passwordController,
              obscureText: true,
              decoration: const InputDecoration(labelText: 'Password', border: OutlineInputBorder()),
            ),
            const SizedBox(height: 18),
            FilledButton(onPressed: loading ? null : signInEmail, child: const Padding(padding: EdgeInsets.all(14), child: Text('Accedi'))),
            TextButton(onPressed: loading ? null : createAccount, child: const Text('Crea account')),
            const Divider(height: 32),
            OutlinedButton.icon(onPressed: loading ? null : signInGoogle, icon: const Icon(Icons.login), label: const Text('Continua con Google')),
            const SizedBox(height: 10),
            OutlinedButton.icon(onPressed: loading ? null : signInApple, icon: const Icon(Icons.apple), label: const Text('Continua con Apple')),
            if (loading) ...[const SizedBox(height: 18), const Center(child: CircularProgressIndicator())],
            if (error != null) ...[const SizedBox(height: 18), Text(error!, style: TextStyle(color: Theme.of(context).colorScheme.error))],
          ],
        ),
      ),
    );
  }
}
