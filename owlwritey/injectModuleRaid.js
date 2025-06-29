// Runs in MAIN world at document_start – injects moduleRaid then removes tag for cleanliness
(() => {
  console.log('[OwlWritey] Injecting moduleRaid...');
  
  // Utility to detect when WhatsApp has created its webpack chunk array
  const getWebpackChunkKey = () => {
    return Object.keys(window).find(
      (key) => key.startsWith('webpackChunk') && Array.isArray(window[key])
    );
  };
  
  const loadModuleRaid = () => {
    let url = '';
    if (typeof chrome !== 'undefined' && chrome.runtime) {
      if (chrome.runtime.getURL) {
        url = chrome.runtime.getURL('assets/moduleRaid.js');
      } else if (chrome.runtime.id) {
        url = `chrome-extension://${chrome.runtime.id}/assets/moduleRaid.js`;
      }
    } else if (typeof browser !== 'undefined' && browser.runtime && browser.runtime.getURL) {
      url = browser.runtime.getURL('assets/moduleRaid.js');
    } else {
      // Fallback: try to detect extension ID from current script URL (if any content script URL is known)
      try {
        const currentScript = document.currentScript || document.querySelector('script[src*="chrome-extension://"]');
        if (currentScript) {
          const match = currentScript.src.match(/chrome-extension:\/\/([a-p]{32})/);
          if (match && match[1]) {
            url = `chrome-extension://${match[1]}/assets/moduleRaid.js`;
          }
        }
      } catch (e) {
        console.warn('[OwlWritey] Unable to infer extension ID for fallback URL:', e);
      }
    }
    if (!url) {
      console.error('[OwlWritey] Could not resolve URL for moduleRaid.js');
      return;
    }
    const s   = document.createElement('script');
    s.src     = url;
    s.type    = 'text/javascript';
    
    s.onload  = () => {
      console.log('[OwlWritey] moduleRaid script loaded');
      s.remove();
      // Give moduleRaid a moment to populate its module list
      setTimeout(() => {
        if (window.mR) {
          console.log('[OwlWritey] moduleRaid initialized successfully');
          const moduleCount = Object.keys(window.mR.modules || {}).length;
          console.log(`[OwlWritey] Found ${moduleCount} webpack modules`);
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
  };

  // Poll until the webpack chunk array becomes available (max ~10 seconds)
  const maxAttempts = 200;
  let attempts = 0;
  const interval = setInterval(() => {
    const chunkKey = getWebpackChunkKey();
    if (chunkKey && window[chunkKey].length > 0) {
      console.log(`[OwlWritey] Detected webpack chunk array with ${window[chunkKey].length} chunks: ${chunkKey}`);
      clearInterval(interval);
      loadModuleRaid();
    } else if (++attempts >= maxAttempts) {
      console.warn('[OwlWritey] Timed out waiting for webpack chunks; attempting to load moduleRaid anyway');
      clearInterval(interval);
      loadModuleRaid();
    }
  }, 50);

  // Fallback polling for Store access (Task 28.4)
  const pollForStore = () => {
    let storeAttempts = 0;
    const maxStoreAttempts = 20; // 20 seconds max
    
    const storeInterval = setInterval(() => {
      if (window.mR && Object.keys(window.mR.modules || {}).length > 0) {
        try {
          const storeModules = window.mR.findModule('Msg') || [];
          if (storeModules.length > 0) {
            window.WhatsAppStore = storeModules[0];
            console.log('[OwlWritey] Store access established via fallback polling');
            clearInterval(storeInterval);
            return;
          }
        } catch (e) {
          console.warn('[OwlWritey] Store polling error:', e.message);
        }
      }
      
      if (++storeAttempts >= maxStoreAttempts) {
        console.error('[OwlWritey] Store access failed after fallback polling');
        clearInterval(storeInterval);
      }
    }, 1000); // Check every second
  };

  // Start store polling after a delay to allow moduleRaid to initialize
  setTimeout(pollForStore, 2000);
})(); 