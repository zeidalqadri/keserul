// Runs in MAIN world at document_start – injects moduleRaid then removes tag for cleanliness
(() => {
  const url = chrome.runtime.getURL('assets/moduleRaid.js');
  const s   = document.createElement('script');
  s.src     = url;
  s.type    = 'text/javascript';
  s.onload  = () => s.remove();
  (document.documentElement || document.head || document.body).appendChild(s);
})(); 