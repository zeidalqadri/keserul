// Runs in MAIN world at document_start – injects moduleRaid then removes tag for cleanliness
(() => {
  console.log('[OwlWritey] Injecting moduleRaid...');
  
  const url = chrome.runtime.getURL('assets/moduleRaid.js');
  const s   = document.createElement('script');
  s.src     = url;
  s.type    = 'text/javascript';
  
  s.onload  = () => {
    console.log('[OwlWritey] moduleRaid script loaded');
    s.remove();
    
    // Wait a bit for moduleRaid to initialize, then check if it worked
    setTimeout(() => {
      if (window.mR) {
        console.log('[OwlWritey] moduleRaid initialized successfully');
        const moduleCount = Object.keys(window.mR.modules || {}).length;
        console.log(`[OwlWritey] Found ${moduleCount} webpack modules`);
        
        // Try to find Store modules
        try {
          const storeModules = window.mR.findModule('Msg') || [];
          console.log(`[OwlWritey] Found ${storeModules.length} Store modules`);
          if (storeModules.length > 0) {
            window.WhatsAppStore = storeModules[0];
            console.log('[OwlWritey] WhatsApp Store exposed as window.WhatsAppStore');
          }
        } catch (e) {
          console.error('[OwlWritey] Error finding Store modules:', e);
        }
      } else {
        console.error('[OwlWritey] moduleRaid failed to initialize - window.mR not found');
      }
    }, 100);
  };
  
  s.onerror = (error) => {
    console.error('[OwlWritey] Failed to load moduleRaid script:', error);
    s.remove();
  };
  
  (document.documentElement || document.head || document.body).appendChild(s);
})(); 