import 'package:flutter/material.dart';
import 'package:purchases_flutter/purchases_flutter.dart';

import '../services/purchases_service.dart';

class PaywallScreen extends StatefulWidget {
  const PaywallScreen({super.key});

  @override
  State<PaywallScreen> createState() => _PaywallScreenState();
}

class _PaywallScreenState extends State<PaywallScreen> {
  Offerings? offerings;
  bool loading = true;
  String? message;

  @override
  void initState() {
    super.initState();
    load();
  }

  Future<void> load() async {
    try {
      offerings = await PurchasesService.offerings();
    } catch (_) {
      message = 'RevenueCat non ancora configurato';
    } finally {
      if (mounted) setState(() => loading = false);
    }
  }

  Future<void> _buy(Package package) async {
    try {
      await PurchasesService.buy(package);
      if (!mounted) return;
      Navigator.of(context).pop(true);
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('$e')),
      );
    }
  }

  Future<void> _restore() async {
    try {
      await PurchasesService.restore();
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Acquisti ripristinati')),
      );
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('$e')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final packages = offerings?.current?.availablePackages ?? <Package>[];
    return Scaffold(
      appBar: AppBar(title: const Text('AstraVideo Pro')),
      body: ListView(
        padding: const EdgeInsets.all(20),
        children: [
          const Icon(Icons.workspace_premium, size: 64),
          const SizedBox(height: 16),
          const Text(
            'Sblocca AstraVideo Pro',
            style: TextStyle(fontSize: 28, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 12),
          const Text(
            '1080p • niente watermark • più crediti • nessuna pubblicità • coda prioritaria',
          ),
          const SizedBox(height: 24),
          if (loading)
            const Center(child: CircularProgressIndicator())
          else if (packages.isEmpty)
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Text(
                  message ?? 'Configura RevenueCat per caricare i piani reali.',
                ),
              ),
            )
          else
            ...packages.map(
              (package) => Card(
                child: ListTile(
                  title: Text(package.storeProduct.title),
                  subtitle: Text(package.storeProduct.description),
                  trailing: FilledButton(
                    onPressed: () => _buy(package),
                    child: Text(package.storeProduct.priceString),
                  ),
                ),
              ),
            ),
          const SizedBox(height: 16),
          TextButton(
            onPressed: _restore,
            child: const Text('Ripristina acquisti'),
          ),
        ],
      ),
    );
  }
}
