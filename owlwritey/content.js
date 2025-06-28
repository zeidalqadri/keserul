// Content Script for WhatsApp Web Voice-Note Transcriber
// Detects voice messages, extracts audio, and handles transcription

class WhatsAppVoiceTranscriber {
  constructor() {
    console.log('[OwlWritey] WhatsAppVoiceTranscriber content script injected and running');
    
    // Filter out noisy WhatsApp CDN 403 errors from console
    this.setupConsoleFiltering();
    
    this.observer = null;
    this.settings = {};
    // Map HTTP status codes to user-friendly messages (Task 20.1)
    this.statusMessages = {
      403: 'Access denied – refresh or reopen chat',
      410: 'Message expired – ask sender to resend'
      // 5xx and other codes will fall back to a generic message handled later
    };
    this.processedMessages = new Set();
    this.isInitialized = false;
    this.debounceTimer = null;
    
    // Selectors for WhatsApp Web elements (multiple fallbacks for robustness)
    this.selectors = {
      voiceMessage: [
        '[data-icon="audio-play"]',
        'span[data-icon="audio-play"]',
        '[data-testid="audio-play"]',
        '[data-testid="audio"]', 
        'button[data-testid*="audio"]',
        'div[data-testid*="audio"]',
        '[role="button"] span[data-testid*="audio"]',
        'button[aria-label*="audio"]',
        '.message-in audio, .message-out audio',
        'audio',
        'button[data-testid="media-play"]',
        'span[data-testid="audio-duration"]',
        '[data-icon*="audio"]'
      ],
      audioElement: 'audio',
      messageContainer: '[data-testid="msg-meta"]',
      chatName: '[data-testid="conversation-title"]',
      messageBubble: '[data-testid="msg-container"]'
    };
    
    this.init();
  }

  setupConsoleFiltering() {
    // Store original console.error
    const originalError = console.error;
    
    // Override console.error to filter known, expected WhatsApp errors
    console.error = (...args) => {
      const message = args.join(' ');
      
      // Filter out expected WhatsApp CDN 403 errors (these are normal due to media encryption)
      if (message.includes('media-kul3-1.cdn.whatsapp.net') && 
          message.includes('403') && 
          message.includes('Forbidden')) {
        return; // Suppress this expected error
      }
      
      // Filter out storage mutation events (Chrome internal)
      if (message.includes('x-storagemutated') || 
          message.includes('Event handler') && message.includes('initial evaluation')) {
        return; // Suppress this Chrome internal warning
      }
      
      // Allow all other errors to be logged normally
      originalError.apply(console, args);
    };
  }

  async init() {
    try {
      console.log('Initializing WhatsApp Voice Transcriber...');
      
      // Load settings
      await this.loadSettings();
      
      // Start observing DOM changes
      this.startObserving();
      
      // Add keyboard shortcuts
      this.addKeyboardShortcuts();
      
      // Add styles
      this.injectStyles();
      
      this.isInitialized = true;
      console.log('WhatsApp Voice Transcriber initialized successfully');
      
      // Wait for WhatsApp to be fully loaded before scanning for voice messages
      this.waitForWhatsAppReady();
      
    } catch (error) {
      console.error('Failed to initialize WhatsApp Voice Transcriber:', error);
    }
  }

  // Wait for WhatsApp to be fully loaded before processing voice messages
  async waitForWhatsAppReady() {
    console.log('[OwlWritey] Waiting for WhatsApp to fully load...');
    
    const maxWaitTime = 30000; // 30 seconds max wait
    const checkInterval = 1000; // Check every 1 second
    const startTime = Date.now();
    
    const checkReady = () => {
      // Check for reliable WhatsApp readiness indicators
      const indicators = [
        // Primary: WhatsApp title in document indicates app is loaded
        () => document.title.includes('WhatsApp'),
        // Secondary: Main app container exists
        () => document.querySelector('#app') !== null,
        // Tertiary: Any basic WhatsApp UI element
        () => document.querySelector('header') !== null || document.querySelector('[role="banner"]') !== null
      ];
      
      const passedChecks = indicators.filter(check => {
        try {
          return check();
        } catch (e) {
          return false;
        }
      });
      
      console.log(`[OwlWritey] WhatsApp loading check: ${passedChecks.length}/${indicators.length} indicators ready`);
      console.log(`[OwlWritey] Document title: "${document.title}"`);
      
      // Consider WhatsApp ready if title includes WhatsApp (most reliable indicator)
      if (passedChecks.length >= 1 && document.title.includes('WhatsApp')) {
        console.log('[OwlWritey] WhatsApp appears to be loaded! Starting voice message scan...');
        
        // Add a small delay to ensure rendering is complete
        setTimeout(() => {
          this.processExistingVoiceMessages();
        }, 2000);
        
        return true;
      }
      
      // Check timeout
      if (Date.now() - startTime > maxWaitTime) {
        console.log('[OwlWritey] Timeout waiting for WhatsApp to load. Starting scan anyway...');
        this.processExistingVoiceMessages();
        return true;
      }
      
      return false;
    };
    
    // Initial check
    if (checkReady()) {
      return;
    }
    
    // Poll until ready or timeout
    const pollInterval = setInterval(() => {
      if (checkReady()) {
        clearInterval(pollInterval);
      }
    }, checkInterval);
  }

  // Load settings from storage
  async loadSettings() {
    return new Promise((resolve) => {
      sendMessageWithRetry({ type: 'GET_SETTINGS' }, { maxRetries: 5, initialDelay: 1000 }, (response) => {
        this.settings = response || {
          autoTranscribe: true,
          generateSummaries: true,
          storeHistory: true,
          batterySaver: true,
          language: 'auto'
        };
        resolve();
      });
    });
  }

  // Start observing DOM changes
  startObserving() {
    this.observer = new MutationObserver((mutations) => {
      // Debounce the processing
      clearTimeout(this.debounceTimer);
      this.debounceTimer = setTimeout(() => {
        this.processNewVoiceMessages(mutations);
      }, 100);
    });

    this.observer.observe(document.body, {
      childList: true,
      subtree: true,
      attributes: true,
      attributeFilter: ['data-testid']
    });
  }

  // Process existing voice messages on page load (called after WhatsApp is ready)
  processExistingVoiceMessages() {
    console.log('[OwlWritey] Looking for existing voice messages...');
    const voiceMessages = this.findVoiceMessages(document);
    console.log(`[OwlWritey] Found ${voiceMessages.length} existing voice messages`);
    
    if (voiceMessages.length === 0) {
      console.log('[OwlWritey] No voice messages found in current view. They will be detected when they appear.');
      
      // Optional debug info (only if needed)
      this.selectors.voiceMessage.forEach(selector => {
        try {
          const elements = document.querySelectorAll(selector);
          if (elements.length > 0) {
            console.log(`[OwlWritey] DEBUG: ${selector} found ${elements.length} elements`);
          }
        } catch (e) {
          // Ignore invalid selectors
        }
      });
    } else {
      console.log('[OwlWritey] Processing existing voice messages...');
      voiceMessages.forEach(message => {
        this.processVoiceMessage(message);
      });
    }
  }

  // Find voice messages using multiple selectors
  findVoiceMessages(container) {
    const found = new Set();
    
    this.selectors.voiceMessage.forEach(selector => {
      try {
        const elements = container.querySelectorAll(selector);
        elements.forEach(el => {
          // If we found an audio play button/icon, find its parent voice message container
          let voiceMessageContainer = el;
          
          // Look for the actual voice message container (usually a few levels up)
          let parent = el.parentElement;
          let depth = 0;
          while (parent && depth < 10) {
            // Look for common voice message container patterns
            const classList = parent.classList ? Array.from(parent.classList).join(' ') : '';
            const hasVoiceMessageClass = classList.includes('message') || 
                                       parent.hasAttribute('data-testid') ||
                                       parent.querySelector('audio') ||
                                       classList.includes('voice') ||
                                       classList.includes('audio');
            
            if (hasVoiceMessageClass) {
              voiceMessageContainer = parent;
              break;
            }
            parent = parent.parentElement;
            depth++;
          }
          
          found.add(voiceMessageContainer);
        });
      } catch (e) {
        // Ignore invalid selectors
      }
    });
    
    return Array.from(found);
  }

  // Process new voice messages from mutations
  processNewVoiceMessages(mutations) {
    mutations.forEach(mutation => {
      if (mutation.type === 'childList') {
        mutation.addedNodes.forEach(node => {
          if (node.nodeType === Node.ELEMENT_NODE) {
            // Check if the added node is a voice message
            const voiceMessages = this.findVoiceMessages(node);
            
            // Also check if the node itself is a voice message
            const isVoiceMessage = this.selectors.voiceMessage.some(selector => {
              try {
                return node.matches && node.matches(selector);
              } catch (e) {
                return false;
              }
            });
            
            if (isVoiceMessage) {
              voiceMessages.push(node);
            }
            
            if (voiceMessages.length > 0) {
              console.log(`[OwlWritey] Found ${voiceMessages.length} new voice messages`);
            }
            
            voiceMessages.forEach(message => {
              this.processVoiceMessage(message);
            });
          }
        });
      }
    });
  }

  // Process a single voice message
  processVoiceMessage(voiceMessageElement) {
    if (!voiceMessageElement) {
      console.log('[OwlWritey] Invalid voice message element, skipping');
      return;
    }
    
    const messageId = this.getMessageId(voiceMessageElement);
    
    if (this.processedMessages.has(messageId)) {
      console.log('[OwlWritey] Message already processed, skipping:', messageId);
      return;
    }
    
    this.processedMessages.add(messageId);
    console.log('[OwlWritey] Processing new voice message:', messageId);
    
    // Add transcribe button
    this.addTranscribeButton(voiceMessageElement);
    
    // TEMPORARILY DISABLE auto-transcription to stop the loop
    console.log('[OwlWritey] Auto-transcription disabled to prevent loops. Use manual transcribe button or Ctrl+Shift+T.');
    
    // Auto-transcribe if enabled (DISABLED FOR NOW)
    // if (this.settings.autoTranscribe) {
    //   setTimeout(() => {
    //     this.transcribeVoiceMessage(voiceMessageElement);
    //   }, 1000);
    // }
  }

  // Get unique message ID
  getMessageId(element) {
    if (!element) return 'invalid-' + Date.now();
    
    // Try multiple strategies to get a unique ID
    let id = '';
    
    // Strategy 1: Look for any existing data attributes
    if (element.dataset && element.dataset.id) {
      id = 'data-id-' + element.dataset.id;
    }
    
    // Strategy 2: Look for message container with data-testid
    if (!id) {
      const messageContainer = element.closest('[data-testid*="message"]');
      if (messageContainer) {
        const timestamp = messageContainer.querySelector('[data-testid*="timestamp"]');
        if (timestamp) {
          id = 'timestamp-' + timestamp.textContent.trim();
        } else {
          id = 'container-' + messageContainer.textContent.slice(0, 30).replace(/\s+/g, '-');
        }
      }
    }
    
    // Strategy 3: Use audio element source or duration if available
    if (!id) {
      const audioEl = element.querySelector('audio') || element.closest('*').querySelector('audio');
      if (audioEl && audioEl.src) {
        id = 'audio-src-' + audioEl.src.slice(-20);
      } else if (audioEl && audioEl.duration) {
        id = 'audio-duration-' + audioEl.duration;
      }
    }
    
    // Strategy 4: Use element position and content as fallback
    if (!id) {
      const rect = element.getBoundingClientRect();
      id = `pos-${Math.round(rect.top)}-${Math.round(rect.left)}-${element.textContent.slice(0, 10).replace(/\s+/g, '-')}`;
    }
    
    // Final fallback
    if (!id) {
      id = 'fallback-' + Date.now() + '-' + Math.random().toString(36).substr(2, 5);
    }
    
    return id;
  }

  // Add transcribe button to voice message
  addTranscribeButton(voiceMessageElement) {
    if (!voiceMessageElement) {
      console.log('[OwlWritey] Cannot add transcribe button - invalid element');
      return;
    }
    
    // Check if button already exists in the element or its parent
    const existingButton = voiceMessageElement.querySelector('.transcribe-btn') ||
                          (voiceMessageElement.parentNode && voiceMessageElement.parentNode.querySelector('.transcribe-btn'));
    
    if (existingButton) {
      console.log('[OwlWritey] Transcribe button already exists, skipping');
      return;
    }
    
    console.log('[OwlWritey] Adding transcribe button to voice message');
    
    const button = document.createElement('button');
    button.className = 'transcribe-btn';
    button.innerHTML = '➜ 📝 Transcribe';
    button.style.cssText = `
      margin-left: 8px;
      padding: 4px 8px;
      background: #25D366;
      color: white;
      border: none;
      border-radius: 4px;
      font-size: 12px;
      cursor: pointer;
      transition: background 0.2s;
    `;
    
    button.addEventListener('click', (e) => {
      e.stopPropagation();
      
      // Dynamically find the voice message element to avoid stale references
      const currentVoiceMessage = this.findVoiceMessageFromButton(button);
      if (currentVoiceMessage) {
        console.log('[OwlWritey] Found current voice message element for transcription');
        this.transcribeVoiceMessage(currentVoiceMessage);
      } else {
        console.error('[OwlWritey] Could not find voice message element from button');
        this.showToast('Could not find voice message to transcribe', 'error');
      }
    });
    
    button.addEventListener('mouseenter', () => {
      button.style.background = '#128C7E';
    });
    
    button.addEventListener('mouseleave', () => {
      button.style.background = '#25D366';
    });
    
    // Insert button after the voice message
    try {
      if (voiceMessageElement.parentNode) {
        voiceMessageElement.parentNode.insertBefore(button, voiceMessageElement.nextSibling);
        console.log('[OwlWritey] Transcribe button added successfully');
      } else {
        console.log('[OwlWritey] Cannot add button - no parent node');
      }
    } catch (error) {
      console.error('[OwlWritey] Error adding transcribe button:', error);
    }
  }

  // Find voice message element from transcribe button (avoids stale references)
  // FIXED: Return message container instead of voice icon span
  findVoiceMessageFromButton(button) {
    if (!button || !button.parentNode) {
      return null;
    }
    
    console.log('[OwlWritey DEBUG] Finding voice message container from button');
    
    // Look for audio play/pause buttons (voice message indicators)
    const voiceSelectors = [
      '[data-icon="audio-play"]',
      '[data-icon="audio-pause"]', 
      'span[data-icon="audio-play"]',
      'span[data-icon="audio-pause"]'
    ];
    
    // Strategy 1: Find the message container first, then verify it contains voice elements
    let messageContainer = button.closest('[data-testid*="message"]') || 
                          button.closest('[class*="message"]') ||
                          button.closest('div[role="row"]');
    
    if (messageContainer) {
      // Verify this container actually contains voice message elements
      for (const selector of voiceSelectors) {
        const voiceIcon = messageContainer.querySelector(selector);
        if (voiceIcon) {
          console.log('[OwlWritey DEBUG] Found voice message container with icon:', selector);
          console.log('[OwlWritey DEBUG] Container element:', messageContainer);
          console.log('[OwlWritey DEBUG] Container children count:', messageContainer.children.length);
          return messageContainer; // Return the container, not the icon!
        }
      }
    }
    
    // Strategy 2: Look in button's parent and find the message container from there
    const parent = button.parentNode;
    for (const selector of voiceSelectors) {
      const voiceIcon = parent.querySelector(selector);
      if (voiceIcon) {
        // Found voice icon, now find its message container
        const container = voiceIcon.closest('[data-testid*="message"]') || 
                         voiceIcon.closest('[class*="message"]') ||
                         voiceIcon.closest('div[role="row"]');
        if (container) {
          console.log('[OwlWritey DEBUG] Found voice message container via parent search');
          console.log('[OwlWritey DEBUG] Container element:', container);
          return container;
        }
      }
    }
    
    // Strategy 3: Look in grandparent container  
    const grandParent = parent.parentNode;
    if (grandParent) {
      for (const selector of voiceSelectors) {
        const voiceIcon = grandParent.querySelector(selector);
        if (voiceIcon) {
          // Found voice icon, now find its message container
          const container = voiceIcon.closest('[data-testid*="message"]') || 
                           voiceIcon.closest('[class*="message"]') ||
                           voiceIcon.closest('div[role="row"]');
          if (container) {
            console.log('[OwlWritey DEBUG] Found voice message container via grandparent search');
            console.log('[OwlWritey DEBUG] Container element:', container);
            return container;
          }
        }
      }
    }
    
    console.log('[OwlWritey DEBUG] Could not find voice message container from button');
    return null;
  }

  // Transcribe a voice message
  async transcribeVoiceMessage(voiceMessageElement) {
    // Critical: Validate element first
    if (!voiceMessageElement) {
      console.error('[OwlWritey] Cannot transcribe - voiceMessageElement is null');
      this.showToast('Cannot transcribe - invalid voice message', 'error');
      return;
    }
    
    if (!voiceMessageElement.parentNode) {
      console.error('[OwlWritey] Cannot transcribe - voice message element has no parent');
      this.showToast('Cannot transcribe - element is disconnected', 'error');
      return;
    }
    
    try {
      console.log('[OwlWritey] Starting transcription for voice message');
      
      // Check battery level if battery saver is enabled
      if (this.settings.batterySaver) {
        const batteryLevel = await this.getBatteryLevel();
        if (batteryLevel < 0.2) {
          this.showToast('Battery saver: Transcription paused', 'warning');
          return;
        }
      }
      
      // Show loading state (with additional safety check)
      this.showLoadingState(voiceMessageElement);
      
      // Extract audio blob
      const audioBlob = await this.extractAudioBlob(voiceMessageElement);
      
      if (!audioBlob) {
        throw new Error('Could not extract audio from voice message');
      }
      
      // Get chat information
      const chatInfo = this.getChatInfo();
      
      // Convert audio blob to ArrayBuffer
      const audioBuffer = await audioBlob.arrayBuffer();
      
      // Send audio data to background/service worker for transcription
      sendMessageWithRetry({
        type: 'TRANSCRIBE_AUDIO',
        data: {
          audioBuffer,
          options: {
            language: this.settings.language,
            batterySaver: this.settings.batterySaver
          },
          chatInfo
        }
      }, { maxRetries: 5, initialDelay: 1000 }, (response) => {
        if (response === undefined) {
          this.showError(voiceMessageElement, 'Failed to communicate with background script. Transcription unavailable.');
        }
      });
      
      // Store context for when transcription completes
      voiceMessageElement.transcriptionContext = {
        chatInfo,
        audioBlob,
        startTime: Date.now()
      };
      
    } catch (error) {
      console.error('[OwlWritey] Error transcribing voice message:', error);
      
      // Only show error UI if element is still valid
      if (voiceMessageElement && voiceMessageElement.parentNode) {
        this.showError(voiceMessageElement, error.message);
      } else {
        // Show toast notification instead if element is invalid
        console.error('[OwlWritey] Cannot show error on invalid element, using toast');
        this.showToast('Transcription failed: ' + error.message, 'error');
      }
    }
  }

  // Extract audio blob from voice message
  async extractAudioBlob(voiceMessageElement) {
    if (!voiceMessageElement) {
      console.error('[OwlWritey] Cannot extract audio - voiceMessageElement is null');
      return null;
    }
    
    try {
      console.log('[OwlWritey] Extracting audio blob from voice message...');
      const blob = await this.getPlayableAudioBlob(voiceMessageElement);
      console.log('[OwlWritey] Audio blob extraction completed');
      return blob;
    } catch (error) {
      console.error('[OwlWritey] Error extracting audio blob:', error);
      
      // Only show error if element is still valid
      if (voiceMessageElement && voiceMessageElement.parentNode) {
        this.showError(voiceMessageElement, 'Error extracting audio: ' + error.message);
      } else {
        // Show toast instead if element is invalid
        this.showToast('Error extracting audio: ' + error.message, 'error');
      }
      return null;
    }
  }

  /**
   * Wait for WhatsApp to attach a playable <audio> element (with a blob: URL) and return its Blob.
   * If only a CDN URL is present, prompt the user to play the voice note in WhatsApp before transcribing.
   */
  async getPlayableAudioBlob(voiceMessageElement, timeout = 10000) {
    if (!voiceMessageElement) {
      throw new Error('Invalid voice message element for audio extraction');
    }
    
    console.log('[OwlWritey DEBUG] === Starting audio extraction debug ===');
    console.log('[OwlWritey DEBUG] Voice message element (should be container):', voiceMessageElement);
    console.log('[OwlWritey DEBUG] Element tag:', voiceMessageElement.tagName);
    console.log('[OwlWritey DEBUG] Element data attributes:', Array.from(voiceMessageElement.attributes).map(attr => `${attr.name}="${attr.value}"`));
    console.log('[OwlWritey DEBUG] Container children count:', voiceMessageElement.children.length);
    console.log('[OwlWritey DEBUG] Container innerHTML preview:', voiceMessageElement.innerHTML.substring(0, 200) + '...');
    
    // Snapshot initial state of all audio elements
    const initialAudioElements = document.querySelectorAll('audio');
    console.log('[OwlWritey DEBUG] Initial audio elements on page:', initialAudioElements.length);
    initialAudioElements.forEach((audio, idx) => {
      console.log(`[OwlWritey DEBUG] Initial audio[${idx}]:`, {
        src: audio.src,
        currentSrc: audio.currentSrc,
        readyState: audio.readyState,
        paused: audio.paused,
        duration: audio.duration
      });
    });
    
    const start = Date.now();
    
    // 1. Try to find and click the play button to force WhatsApp to inject the audio element
    try {
      // Look for the actual play button (audio-play icon) within the container
      const playButton = voiceMessageElement.querySelector('[data-icon="audio-play"]') ||
                        voiceMessageElement.querySelector('span[data-icon="audio-play"]') ||
                        voiceMessageElement.querySelector('div[data-icon="audio-play"]') ||
                        voiceMessageElement.querySelector('[role="button"][data-icon="audio-play"]');
      
      if (playButton) {
        console.log('[OwlWritey DEBUG] Found play button in container:', playButton);
        console.log('[OwlWritey DEBUG] Play button attributes:', Array.from(playButton.attributes).map(attr => `${attr.name}="${attr.value}"`));
        console.log('[OwlWritey DEBUG] Play button parent:', playButton.parentElement);
        console.log('[OwlWritey DEBUG] Clicking play button to activate audio...');
        
        // Try clicking the button and also trigger any parent button elements
        playButton.click();
        
        // Also try clicking parent elements that might be the actual clickable area
        let parent = playButton.parentElement;
        let depth = 0;
        while (parent && depth < 3) {
          if (parent.tagName === 'BUTTON' || parent.getAttribute('role') === 'button') {
            console.log('[OwlWritey DEBUG] Also clicking parent button at depth', depth, ':', parent);
            parent.click();
            break;
          }
          parent = parent.parentElement;
          depth++;
        }
        
        // Wait longer for WhatsApp to process the click and load audio
        await new Promise(r => setTimeout(r, 1000));
        
        // Check if new audio/video elements appeared after click
        const postClickAudioElements = document.querySelectorAll('audio, video');
        console.log('[OwlWritey DEBUG] Audio/video elements after click:', postClickAudioElements.length);
        if (postClickAudioElements.length > initialAudioElements.length) {
          console.log('[OwlWritey DEBUG] New media elements created after click!');
          for (let i = initialAudioElements.length; i < postClickAudioElements.length; i++) {
            const newMedia = postClickAudioElements[i];
            console.log(`[OwlWritey DEBUG] New media[${i}]:`, {
              tagName: newMedia.tagName,
              src: newMedia.src,
              currentSrc: newMedia.currentSrc,
              readyState: newMedia.readyState,
              paused: newMedia.paused,
              duration: newMedia.duration
            });
          }
        }
      } else {
        console.log('[OwlWritey DEBUG] No play button found in container');
        console.log('[OwlWritey DEBUG] Available elements in container:', 
                   Array.from(voiceMessageElement.querySelectorAll('*')).slice(0, 10).map(el => el.tagName + (el.getAttribute('data-icon') ? `[${el.getAttribute('data-icon')}]` : '')));
      }
    } catch (error) {
      console.log('[OwlWritey DEBUG] Could not click play button:', error.message);
    }

    let attemptCount = 0;
    while (Date.now() - start < timeout) {
      attemptCount++;
      console.log(`[OwlWritey DEBUG] === Detection attempt ${attemptCount} (${Date.now() - start}ms elapsed) ===`);
      
      // Search for audio/video elements in multiple locations (container-focused)
      let audioElement = null;
      
      // Strategy 1: Direct search within the container (most likely to succeed now)
      console.log('[OwlWritey DEBUG] Strategy 1: Searching within container for audio/video...');
      audioElement = voiceMessageElement.querySelector('audio') || voiceMessageElement.querySelector('video');
      if (audioElement) {
        console.log('[OwlWritey DEBUG] Strategy 1 SUCCESS: Found media element in container:', audioElement.tagName);
      }
      
      // Strategy 2: Search all media elements within container (deeper search)
      if (!audioElement) {
        console.log('[OwlWritey DEBUG] Strategy 2: Deep search within container...');
        const allMediaInContainer = voiceMessageElement.querySelectorAll('audio, video');
        console.log(`[OwlWritey DEBUG] Strategy 2: Found ${allMediaInContainer.length} media elements in container`);
        if (allMediaInContainer.length > 0) {
          audioElement = allMediaInContainer[allMediaInContainer.length - 1]; // Use most recent
          console.log('[OwlWritey DEBUG] Strategy 2 SUCCESS: Using most recent media element in container:', audioElement.tagName);
        }
      }
      
      // Strategy 3: Search in sibling containers (adjacent messages)
      if (!audioElement) {
        console.log('[OwlWritey DEBUG] Strategy 3: Searching sibling containers...');
        const parent = voiceMessageElement.parentElement;
        if (parent) {
          const siblingContainers = parent.querySelectorAll('[data-testid*="message"]');
          console.log(`[OwlWritey DEBUG] Strategy 3: Found ${siblingContainers.length} sibling containers`);
          for (const container of siblingContainers) {
            const mediaInSibling = container.querySelector('audio, video');
            if (mediaInSibling && mediaInSibling.src) {
              audioElement = mediaInSibling;
              console.log('[OwlWritey DEBUG] Strategy 3 SUCCESS: Found media in sibling container:', audioElement.tagName);
              break;
            }
          }
        }
      }
      
      // Strategy 4: Global search for recently created audio/video elements
      if (!audioElement) {
        console.log('[OwlWritey DEBUG] Strategy 4: Global search for recent media elements...');
        const allMedia = document.querySelectorAll('audio, video');
        console.log(`[OwlWritey DEBUG] Strategy 4: Found ${allMedia.length} total media elements globally`);
        
        if (allMedia.length > 0) {
          // Find the most recently created media element
          audioElement = allMedia[allMedia.length - 1];
          console.log('[OwlWritey DEBUG] Strategy 4: Using most recent global media element:', audioElement.tagName);
        }
      }
      
      if (audioElement) {
        console.log('[OwlWritey DEBUG] Found media element:', {
          tagName: audioElement.tagName,
          src: audioElement.src,
          currentSrc: audioElement.currentSrc,
          readyState: audioElement.readyState,
          paused: audioElement.paused,
          duration: audioElement.duration,
          networkState: audioElement.networkState,
          preload: audioElement.preload,
          muted: audioElement.muted,
          controls: audioElement.controls
        });
        
        if (audioElement.src) {
          const src = audioElement.src;
          console.log('[OwlWritey DEBUG] Media src found:', src);
          
          // Case A: blob URL already available – fetch locally (will succeed without credentials)
          if (src.startsWith('blob:')) {
            try {
              console.log('[OwlWritey DEBUG] Found blob URL! Attempting to fetch...');
              const resp = await fetch(src);
              console.log('[OwlWritey DEBUG] Fetch response:', {
                status: resp.status,
                statusText: resp.statusText,
                headers: Object.fromEntries(resp.headers.entries())
              });
              const blob = await resp.blob();
              console.log('[OwlWritey DEBUG] Media blob extracted successfully:', {
                size: blob.size,
                type: blob.type
              });
              return blob;
            } catch (err) {
              console.error('[OwlWritey DEBUG] Failed to fetch blob:', err);
              throw new Error('Failed to fetch local media blob.');
            }
          } else {
            // Case B: CDN URL or other URL type
            console.log('[OwlWritey DEBUG] Found non-blob URL:', src.substring(0, 100));
            if (src.includes('whatsapp.net') || src.includes('cdn')) {
              console.log('[OwlWritey DEBUG] Detected WhatsApp CDN URL - waiting for blob conversion...');
            }
          }
        } else {
          console.log('[OwlWritey DEBUG] Media element has no src attribute');
          // Check for source elements within video/audio tags
          const sourceElements = audioElement.querySelectorAll('source');
          if (sourceElements.length > 0) {
            console.log('[OwlWritey DEBUG] Found source elements:', sourceElements.length);
            sourceElements.forEach((source, idx) => {
              console.log(`[OwlWritey DEBUG] Source[${idx}]:`, {
                src: source.src,
                type: source.type
              });
            });
          }
        }
      } else {
        console.log('[OwlWritey DEBUG] No media element found in any strategy');
      }
      
      // Log current DOM state around the voice message
      console.log('[OwlWritey DEBUG] Current DOM structure around voice message:');
      const parent = voiceMessageElement.parentElement;
      if (parent) {
        console.log('[OwlWritey DEBUG] Parent HTML:', parent.innerHTML.substring(0, 200) + '...');
      }
      
      // Wait 250 ms before re-checking DOM
      console.log('[OwlWritey DEBUG] Waiting 250ms before next attempt...');
      await new Promise(r => setTimeout(r, 250));
    }
    
    console.error('[OwlWritey DEBUG] === Timed out after', attemptCount, 'attempts ===');
    console.error('[OwlWritey DEBUG] Final state - all media elements:', document.querySelectorAll('audio, video').length);
    document.querySelectorAll('audio, video').forEach((media, idx) => {
      console.error(`[OwlWritey DEBUG] Final ${media.tagName}[${idx}]:`, {
        src: media.src,
        currentSrc: media.currentSrc,
        readyState: media.readyState,
        parentElement: media.parentElement?.tagName || 'none'
      });
    });
    
    // Also log what's actually in the container
    console.error('[OwlWritey DEBUG] Container content summary:');
    console.error('[OwlWritey DEBUG] - Container tag:', voiceMessageElement.tagName);
    console.error('[OwlWritey DEBUG] - Container children:', voiceMessageElement.children.length);
    console.error('[OwlWritey DEBUG] - Media in container:', voiceMessageElement.querySelectorAll('audio, video').length);
    console.error('[OwlWritey DEBUG] - Buttons in container:', voiceMessageElement.querySelectorAll('button, [role="button"]').length);
    console.error('[OwlWritey DEBUG] - Icons in container:', voiceMessageElement.querySelectorAll('[data-icon]').length);
    
    throw new Error('Timed out waiting for audio element. Try playing the voice note once then transcribe again.');
  }

  // Get chat information
  getChatInfo() {
    const chatNameElement = document.querySelector(this.selectors.chatName);
    const chatName = chatNameElement ? chatNameElement.textContent : 'Unknown Chat';
    
    return {
      chatName,
      chatId: chatName, // Simplified for demo
      timestamp: Date.now()
    };
  }

  // Handle messages from transcriber worker
  handleTranscriberMessage(message) {
    switch (message.type) {
      case 'INITIALIZED':
        console.log('Transcriber worker initialized');
        break;
        
      case 'PARTIAL_TRANSCRIPT':
        this.updatePartialTranscript(message.data);
        break;
        
      case 'TRANSCRIPTION_COMPLETE':
        this.handleTranscriptionComplete(message.data);
        break;
        
      case 'SUMMARY_COMPLETE':
        this.handleSummaryComplete(message.data);
        break;
        
      case 'ERROR':
        console.error('Transcriber error:', message.error);
        this.showToast(`Transcription error: ${message.error}`, 'error');
        break;
    }
  }

  // Update partial transcript display
  updatePartialTranscript(partialData) {
    // Find the current transcription element and update it
    const transcriptionElements = document.querySelectorAll('.transcription-result');
    const latestElement = transcriptionElements[transcriptionElements.length - 1];
    
    if (latestElement) {
      latestElement.textContent = partialData.data;
      latestElement.style.opacity = '0.7';
    }
  }

  // Handle completed transcription
  async handleTranscriptionComplete(result) {
    try {
      // Find the voice message element that was being transcribed
      const voiceMessages = document.querySelectorAll(this.selectors.voiceMessage);
      let targetElement = null;
      
      for (const element of voiceMessages) {
        if (element.transcriptionContext) {
          targetElement = element;
          break;
        }
      }
      
      if (!targetElement) {
        console.warn('No target element found for transcription result');
        return;
      }
      
      const context = targetElement.transcriptionContext;
      delete targetElement.transcriptionContext;
      
      // Display the transcript
      this.displayTranscript(targetElement, result, context);
      
      // Generate summary if enabled
      if (this.settings.generateSummaries) {
        this.generateSummary(result.transcript);
      }
      
      // Store in database if enabled
      if (this.settings.storeHistory) {
        await this.saveTranscript(result, context);
      }
      
      // Show notification
      this.showNotification(result.transcript);
      
      // Show success toast
      this.showToast('Transcription completed!', 'success');
      
    } catch (error) {
      console.error('Error handling transcription complete:', error);
    }
  }

  // Display transcript inline
  displayTranscript(voiceMessageElement, result, context) {
    // Remove loading state
    this.removeLoadingState(voiceMessageElement);
    
    // Create transcript container
    const transcriptContainer = document.createElement('div');
    transcriptContainer.className = 'transcription-result';
    transcriptContainer.style.cssText = `
      margin-top: 8px;
      padding: 8px;
      background: #f0f0f0;
      border-radius: 4px;
      font-size: 14px;
      line-height: 1.4;
      border-left: 3px solid #25D366;
    `;
    
    // Add language indicator
    const languageIndicator = document.createElement('div');
    languageIndicator.style.cssText = `
      font-size: 12px;
      color: #666;
      margin-bottom: 4px;
    `;
    languageIndicator.textContent = `(${result.language})`;
    transcriptContainer.appendChild(languageIndicator);
    
    // Add transcript text
    const transcriptText = document.createElement('div');
    transcriptText.textContent = result.transcript;
    transcriptContainer.appendChild(transcriptText);
    
    // Add summary toggle if summary is available
    if (result.summary) {
      const summaryToggle = document.createElement('button');
      summaryToggle.textContent = '🗂 Summary/Full';
      summaryToggle.style.cssText = `
        margin-top: 8px;
        padding: 4px 8px;
        background: #007bff;
        color: white;
        border: none;
        border-radius: 4px;
        font-size: 12px;
        cursor: pointer;
      `;
      
      let showingSummary = false;
      summaryToggle.addEventListener('click', () => {
        if (showingSummary) {
          transcriptText.textContent = result.transcript;
          summaryToggle.textContent = '🗂 Summary/Full';
        } else {
          transcriptText.textContent = result.summary;
          summaryToggle.textContent = '🗂 Full/Summary';
        }
        showingSummary = !showingSummary;
      });
      
      transcriptContainer.appendChild(summaryToggle);
    }
    
    // Insert after the transcribe button
    const transcribeButton = voiceMessageElement.parentNode.querySelector('.transcribe-btn');
    if (transcribeButton) {
      transcribeButton.parentNode.insertBefore(transcriptContainer, transcribeButton.nextSibling);
    } else {
      voiceMessageElement.parentNode.appendChild(transcriptContainer);
    }
  }

  // Generate summary
  generateSummary(transcript) {
    // This method is now empty as the in-page worker is removed
  }

  // Handle summary completion
  handleSummaryComplete(summaryData) {
    // Update the latest transcript with summary
    const transcriptionElements = document.querySelectorAll('.transcription-result');
    const latestElement = transcriptionElements[transcriptionElements.length - 1];
    
    if (latestElement) {
      // Add summary data to the element
      latestElement.summaryData = summaryData;
    }
  }

  // Save transcript to database
  async saveTranscript(result, context) {
    try {
      const transcriptData = {
        transcript: result.transcript,
        language: result.language,
        confidence: result.confidence,
        duration: result.duration,
        chatName: context.chatInfo.chatName,
        chatId: context.chatInfo.chatId,
        timestamp: context.chatInfo.timestamp,
        hasSummary: !!result.summary,
        summary: result.summary,
        keyPoints: result.keyPoints
      };
      
      // Use the database helper
      if (typeof transcriptDB !== 'undefined') {
        await transcriptDB.saveTranscript(transcriptData);
      }
      
    } catch (error) {
      console.error('Error saving transcript:', error);
    }
  }

  // Show loading state
  showLoadingState(voiceMessageElement) {
    if (!voiceMessageElement || !voiceMessageElement.parentNode) {
      console.log('[OwlWritey] Cannot show loading state - invalid element reference');
      return;
    }
    
    const button = voiceMessageElement.parentNode.querySelector('.transcribe-btn');
    if (button) {
      button.textContent = '⏳ Transcribing...';
      button.disabled = true;
      button.style.background = '#666';
    }
  }

  // Remove loading state
  removeLoadingState(voiceMessageElement) {
    if (!voiceMessageElement || !voiceMessageElement.parentNode) {
      console.log('[OwlWritey] Cannot remove loading state - invalid element reference');
      return;
    }
    
    const button = voiceMessageElement.parentNode.querySelector('.transcribe-btn');
    if (button) {
      button.textContent = '➜ 📝 Transcribe';
      button.disabled = false;
      button.style.background = '#25D366';
    }
  }

  // Show error with friendly message and expandable raw details (Task 20.2)
  showError(voiceMessageElement, errorMessage) {
    this.removeLoadingState(voiceMessageElement);

    // Check if we have a valid element to show error on
    if (!voiceMessageElement || !voiceMessageElement.parentNode) {
      console.log('[OwlWritey] Cannot show error - invalid element reference');
      // Still show toast notification for user feedback
      this.showToast('Transcription failed', 'error');
      return;
    }

    // Attempt to extract numeric status code from the errorMessage string
    let statusCode = null;
    const match = /\b(\d{3})\b/.exec(errorMessage);
    if (match) {
      statusCode = parseInt(match[1], 10);
    }

    // Determine friendly message using statusMessages map
    let friendlyMsg = errorMessage;
    if (statusCode && this.statusMessages[statusCode]) {
      friendlyMsg = this.statusMessages[statusCode];
    } else if (statusCode && statusCode >= 500) {
      friendlyMsg = 'WhatsApp server error – try again later';
    }

    // Build main error container
    const errorDiv = document.createElement('div');
    errorDiv.style.cssText = `
      margin-top: 8px;
      padding: 8px;
      background: #ffebee;
      color: #c62828;
      border-radius: 4px;
      font-size: 12px;
      border-left: 3px solid #c62828;
    `;

    // Friendly text
    const friendlyP = document.createElement('p');
    friendlyP.style.margin = '0 0 4px 0';
    friendlyP.textContent = `Error: ${friendlyMsg}`;
    errorDiv.appendChild(friendlyP);

    // Details accordion with raw message
    const details = document.createElement('details');
    details.style.marginTop = '4px';
    const summary = document.createElement('summary');
    summary.textContent = 'Details';
    summary.style.cursor = 'pointer';
    details.appendChild(summary);
    const pre = document.createElement('pre');
    pre.textContent = errorMessage;
    pre.style.whiteSpace = 'pre-wrap';
    pre.style.userSelect = 'text';
    details.appendChild(pre);
    errorDiv.appendChild(details);

    voiceMessageElement.parentNode.appendChild(errorDiv);

    // Toast notification for quick user visibility
    this.showToast(friendlyMsg, 'error');
  }

  // Show toast notification
  showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = 'transcriber-toast';
    
    const colors = {
      success: '#4caf50',
      error: '#f44336',
      warning: '#ff9800',
      info: '#2196f3'
    };
    
    toast.style.cssText = `
      position: fixed;
      top: 20px;
      right: 20px;
      padding: 12px 16px;
      background: ${colors[type] || colors.info};
      color: white;
      border-radius: 4px;
      font-size: 14px;
      z-index: 10000;
      box-shadow: 0 2px 8px rgba(0,0,0,0.2);
      animation: slideIn 0.3s ease-out;
    `;
    
    toast.textContent = message;
    document.body.appendChild(toast);
    
    setTimeout(() => {
      toast.style.animation = 'slideOut 0.3s ease-in';
      setTimeout(() => {
        if (toast.parentNode) {
          toast.parentNode.removeChild(toast);
        }
      }, 300);
    }, 3000);
  }

  // Show Chrome notification
  showNotification(transcript) {
    const title = 'WhatsApp Voice Transcriber';
    const message = transcript.length > 120 ? 
      transcript.substring(0, 120) + '...' : transcript;
    sendMessageWithRetry({
      type: 'SHOW_NOTIFICATION',
      title,
      message
    }, { maxRetries: 3, initialDelay: 1000 }, () => {});
  }

  // Get battery level
  async getBatteryLevel() {
    return new Promise((resolve) => {
      sendMessageWithRetry({ type: 'GET_BATTERY_LEVEL' }, { maxRetries: 3, initialDelay: 1000 }, (response) => {
        resolve(response && response.level !== undefined ? response.level : 1.0);
      });
    });
  }

  // Add keyboard shortcuts
  addKeyboardShortcuts() {
    document.addEventListener('keydown', (e) => {
      // Ctrl + Shift + T to transcribe latest voice message
      if (e.ctrlKey && e.shiftKey && e.key === 'T') {
        e.preventDefault();
        this.transcribeLatestVoiceMessage();
      }
    });
  }

  // Transcribe the latest voice message
  transcribeLatestVoiceMessage() {
    const voiceMessages = this.findVoiceMessages(document);
    const latestMessage = voiceMessages[voiceMessages.length - 1];
    
    if (latestMessage) {
      console.log('[OwlWritey] Transcribing latest voice message');
      this.transcribeVoiceMessage(latestMessage);
    } else {
      console.log('[OwlWritey] No voice messages found for transcription');
      this.showToast('No voice messages found', 'warning');
    }
  }

  // Inject CSS styles
  injectStyles() {
    const style = document.createElement('style');
    style.textContent = `
      @keyframes slideIn {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
      }
      
      @keyframes slideOut {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
      }
      
      .transcribe-btn:hover {
        background: #128C7E !important;
      }
      
      .transcription-result {
        transition: opacity 0.3s ease;
      }
    `;
    document.head.appendChild(style);
  }

  // Cleanup
  cleanup() {
    if (this.observer) {
      this.observer.disconnect();
    }
    
    console.log('WhatsApp Voice Transcriber cleaned up');
  }

  /**
   * Show a persistent, dismissible banner for critical errors (e.g., BG script unavailable)
   */
  showPersistentBanner(message) {
    // Remove any existing banner
    const existing = document.getElementById('transcriber-banner');
    if (existing) existing.remove();
    const banner = document.createElement('div');
    banner.id = 'transcriber-banner';
    banner.style.cssText = `
      position: fixed;
      top: 0; left: 0; right: 0;
      background: #f44336;
      color: white;
      padding: 12px 24px;
      font-size: 16px;
      z-index: 10001;
      display: flex;
      align-items: center;
      justify-content: space-between;
      box-shadow: 0 2px 8px rgba(0,0,0,0.15);
    `;
    banner.textContent = message;
    const closeBtn = document.createElement('button');
    closeBtn.textContent = '×';
    closeBtn.style.cssText = `
      background: none;
      border: none;
      color: white;
      font-size: 24px;
      margin-left: 16px;
      cursor: pointer;
    `;
    closeBtn.onclick = () => banner.remove();
    banner.appendChild(closeBtn);
    document.body.appendChild(banner);
  }
}

// Initialize the transcriber when the page is ready
let globalTranscriberInstance;
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    globalTranscriberInstance = new WhatsAppVoiceTranscriber();
    window.globalTranscriberInstance = globalTranscriberInstance; // Expose globally
  });
} else {
  globalTranscriberInstance = new WhatsAppVoiceTranscriber();
  window.globalTranscriberInstance = globalTranscriberInstance; // Expose globally
}

// Handle messages from service worker
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  switch (request.type) {
    case 'TRANSCRIBE_LATEST':
      if (globalTranscriberInstance) {
        globalTranscriberInstance.transcribeLatestVoiceMessage();
      }
      break;
      
    case 'SAVE_TO_DB':
      // Handle saving to database
      if (typeof transcriptDB !== 'undefined') {
        transcriptDB.saveTranscript(request.data);
      }
      break;

    case 'TRANSCRIPTION_COMPLETE': {
      // Find the voice message element that matches the chatInfo (fallback to latest)
      const voiceMessages = globalTranscriberInstance.findVoiceMessages(document);
      let targetElement = null;
      for (const element of voiceMessages) {
        if (element.transcriptionContext && element.transcriptionContext.chatInfo &&
            element.transcriptionContext.chatInfo.timestamp === request.chatInfo.timestamp) {
          targetElement = element;
          break;
        }
      }
      if (!targetElement && voiceMessages.length > 0) {
        targetElement = voiceMessages[voiceMessages.length - 1];
      }
      if (targetElement && globalTranscriberInstance) {
        globalTranscriberInstance.displayTranscript(targetElement, request.data, request.chatInfo);
      }
      break;
    }
    case 'TRANSCRIPTION_ERROR': {
      // Find the voice message element that matches the chatInfo (fallback to latest)
      const voiceMessages = globalTranscriberInstance.findVoiceMessages(document);
      let targetElement = null;
      for (const element of voiceMessages) {
        if (element.transcriptionContext && element.transcriptionContext.chatInfo &&
            element.transcriptionContext.chatInfo.timestamp === request.chatInfo.timestamp) {
          targetElement = element;
          break;
        }
      }
      if (!targetElement && voiceMessages.length > 0) {
        targetElement = voiceMessages[voiceMessages.length - 1];
      }
      if (targetElement && globalTranscriberInstance) {
        globalTranscriberInstance.showError(targetElement, request.error);
      }
      break;
    }
  }
});

// Export class for unit testing (Node/Jest environment)
if (typeof module !== 'undefined' && module.exports) {
  module.exports = WhatsAppVoiceTranscriber;
}

// --- Utility: sendMessageWithRetry ---
let bgCommWarningShown = false;
const DEBUG_MODE = false; // Set true for verbose logging

/**
 * Sends a message to the background script with exponential backoff and retry limit.
 * @param {object} message - The message to send.
 * @param {object} [options] - { maxRetries, initialDelay }
 * @param {function} callback - Callback to receive the response (may be undefined on failure).
 */
function sendMessageWithRetry(message, options = {}, callback) {
  const maxRetries = options.maxRetries || 5;
  let delay = options.initialDelay || 1000;
  let attempt = 0;

  function trySend() {
    chrome.runtime.sendMessage(message, (response) => {
      if (chrome.runtime.lastError || response === undefined) {
        attempt++;
        if (DEBUG_MODE) {
          console.warn('[OwlWritey] BG comms failed (attempt', attempt, '):', chrome.runtime.lastError);
        }
        if (attempt >= maxRetries) {
          if (!bgCommWarningShown) {
            console.warn('[OwlWritey] Failed to communicate with background script after', attempt, 'attempts.');
            bgCommWarningShown = true;
          }
          // Show user notification (if class instance available)
          if (window.globalTranscriberInstance && typeof window.globalTranscriberInstance.showPersistentBanner === 'function') {
            window.globalTranscriberInstance.showPersistentBanner(
              'Extension background process is unavailable. Please refresh the page or check extension status.'
            );
          }
          callback(undefined); // Final failure
        } else {
          setTimeout(trySend, delay);
          delay *= 2;
        }
      } else {
        callback(response);
      }
    });
  }
  trySend();
} 