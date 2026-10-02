import 'package:purchases_flutter/purchases_flutter.dart';

class PurchasesService {
  PurchasesService._();

  static bool _configured = false;

  static Future<void> configure({required String apiKey, required String appUserId}) async {
    if (apiKey.trim().isEmpty) return;
    await Purchases.setLogLevel(LogLevel.debug);
    await Purchases.configure(PurchasesConfiguration(apiKey)..appUserID = appUserId);
    _configured = true;
  }

  static Future<Offerings?> offerings() async {
    if (!_configured) return null;
    return Purchases.getOfferings();
  }

  static Future<bool> isPro() async {
    if (!_configured) return false;
    final info = await Purchases.getCustomerInfo();
    return info.entitlements.active.containsKey('pro');
  }

  static Future<CustomerInfo> buy(Package package) async {
    if (!_configured) {
      throw StateError('RevenueCat non configurato');
    }
    return Purchases.purchasePackage(package);
  }

  static Future<CustomerInfo> restore() async {
    if (!_configured) {
      throw StateError('RevenueCat non configurato');
    }
    return Purchases.restorePurchases();
  }
}
