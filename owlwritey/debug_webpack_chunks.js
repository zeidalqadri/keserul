// Webpack Chunk Detection Debug Script
// Run this in WhatsApp Web Console to debug moduleRaid module detection

console.log('🔧 Debugging webpack chunk detection issue...');

// 1. Check what webpack-related globals exist
console.log('\n1️⃣ Webpack globals detection:');
const webpackGlobals = Object.keys(window).filter(key => 
  key.toLowerCase().includes('webpack') || key.includes('chunk')
);
console.log('Webpack-related window properties:', webpackGlobals);

// 2. Check each webpack chunk array
webpackGlobals.forEach(key => {
  if (Array.isArray(window[key])) {
    console.log(`${key}: Array with ${window[key].length} items`);
  } else {
    console.log(`${key}: ${typeof window[key]}`);
  }
});

// 3. Manual moduleRaid test
console.log('\n2️⃣ Manual moduleRaid test:');
const webpackChunkKey = Object.keys(window).find(
  key => key.startsWith('webpackChunk') && Array.isArray(window[key])
);

if (webpackChunkKey) {
  console.log(`Found webpack chunk: ${webpackChunkKey}`);
  console.log(`Chunk length: ${window[webpackChunkKey].length}`);
} else {
  console.error('No webpack chunk array found');
}

// 4. Check timing
console.log('\n3️⃣ Timing check:');
console.log('Document ready state:', document.readyState);
console.log('WhatsApp app element:', document.querySelector('#app') ? '✅' : '❌');
