// WhatsApp Store Access Verification Script for Task 28.3
// Run this in WhatsApp Web Console (F12) after reloading extension

console.log('🔍 Starting Store Access Verification for Task 28.3...');

// Check moduleRaid availability
console.log('\n1️⃣ Testing moduleRaid availability:');
const moduleRaidAvailable = typeof window.mR !== 'undefined';
console.log(`moduleRaid available: ${moduleRaidAvailable ? '✅' : '❌'}`);

if (moduleRaidAvailable) {
  const moduleCount = Object.keys(window.mR.modules || {}).length;
  console.log(`Modules loaded: ${moduleCount}`);
} else {
  console.error('❌ window.mR not found - moduleRaid injection failed');
}

// Test Store detection
console.log('\n2️⃣ Testing WhatsApp Store detection:');
const whatsAppStoreAvailable = typeof window.WhatsAppStore !== 'undefined';
console.log(`WhatsApp Store available: ${whatsAppStoreAvailable ? '✅' : '❌'}`);

if (whatsAppStoreAvailable) {
  console.log('WhatsApp Store keys:', Object.keys(window.WhatsAppStore).slice(0, 10));
  console.log('Store has Msg:', 'Msg' in window.WhatsAppStore ? '✅' : '❌');
}

// Manual Store module detection
console.log('\n3️⃣ Manual Store module detection:');
if (moduleRaidAvailable) {
  try {
    const storeModules = window.mR.findModule('Msg') || [];
    console.log(`Store modules found: ${storeModules.length}`);
    
    if (storeModules.length > 0) {
      const firstStore = storeModules[0];
      console.log('Store.Msg available:', 'Msg' in firstStore ? '✅' : '❌');
      console.log('Store.DownloadManager available:', 'DownloadManager' in firstStore ? '✅' : '❌');
    }
  } catch (e) {
    console.error('Error in Store detection:', e);
  }
}

// Summary
console.log('\n4️⃣ VERIFICATION SUMMARY:');
const success = moduleRaidAvailable && (whatsAppStoreAvailable || window.Store);
console.log(success ? '🎉 SUCCESS: Ready for Task 29' : '❌ FAILED: Needs debugging');