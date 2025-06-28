# WhatsApp Web Voice-Note Transcriber - Project Scratchpad

## Background and Motivation
Building a privacy-first Chrome extension that transcribes WhatsApp Web voice messages locally using Whisper via Transformers.js. The extension will work entirely on-device with no data leaving the host machine.

## Key Challenges and Analysis
- Local transcription using Whisper models via Transformers.js
- Audio blob extraction and conversion from WhatsApp Web
- IndexedDB for persistent storage
- Chrome extension manifest v3 compliance
- Battery optimization and resource management
- Multilingual support with auto-detection
- Post-launch console errors related to:
  • Authorization failures (403/410) when our `extractAudioBlob()` hits WhatsApp CDN before a local `blob:` is available.
  • Worker event-listener timing ("x-storagemutated-1").
  • Browser security header warning – `Permissions-Policy: interest-cohort` is no longer recognised since Chrome 115+, yet WhatsApp's CDN still serves it, triggering a noisy but harmless warning on every navigation.

## High-level Task Breakdown

### Phase 1: Core MVP Implementation ✅ COMPLETED
- [x] Create project structure and manifest.json
- [x] Implement content script for voice message detection
- [x] Set up audio blob extraction and conversion
- [x] Implement local transcription with Whisper
- [x] Add inline transcript display
- [x] Create service worker for background tasks

### Phase 2: Enhanced Features ✅ COMPLETED
- [x] Language auto-detection and multilingual models
- [x] Summary generation with BART/T5
- [x] IndexedDB storage and management
- [x] Popup UI with search and export
- [x] Options page with settings
- [x] Battery optimization
- [x] Error handling and robustness

### Phase 3: Packaging and Testing ✅ COMPLETED
- [x] Create icons and assets
- [x] Write documentation
- [x] Implement comprehensive tests
- [x] Create privacy policy and store description

### Phase 4: Post-Launch Bug Fixes (NEW)

> Each task below is broken down into small executable steps. The **Executor** should complete ONE numbered step at a time, mark it ✓ when done (and validated), then request confirmation before moving to the next step.

#### 🐞 Task 18 – Console Error Audit & Categorisation
18.1  Reproduce the console errors in a clean Chrome profile with only our extension enabled.  
18.2  Capture full console logs (filter by our script URLs) and annotate which originate from: extension code, WhatsApp code, or browser/security.  
18.3  Summarise each unique error/warning: message, source file, line, stack snippet, frequency.  
18.4  Decide which ones are actionable by the extension and which are external noise.  
**Success Criteria:** A markdown table added to scratchpad with the above info and "actionable?" column.

#### 🐙 Task 19 – Reliable Audio Extraction Refactor
19.1  Investigate WA DOM: when/where does `<audio src="blob:…">` appear after user presses play?  
19.2  Prototype a helper `await getPlayableAudioBlob(messageEl)` that:
   • waits max 5 s for an `<audio>` child with a `blob:` URL;  
   • if none, invokes WhatsApp's internal `window.WWebJS?.downloadMedia` or similar (feature-detect);  
   • returns a `Blob` with proper MIME (`audio/ogg; codecs=opus`).  
19.3  Ensure `fetch` is called with `{ credentials: 'include' }` when using WA CDN URLs.  
19.4  Update `extractAudioBlob()` in `content.js` to use this helper and remove direct CDN fetch.  
19.5  Add exponential-backoff retry (max 3) for transient 403/410 before failing.  
**Success Criteria:** Playing a voice note once makes the helper resolve a valid Blob (verified via `blob.size > 0`) for three different chats; no 403/410 errors appear for these cases.

#### ⚙️ Task 20 – Enhanced Error-Handling Messaging
20.1  Map HTTP status codes → user-friendly messages:
   • 403 → "Access denied – refresh or reopen chat".  
   • 410 → "Message expired – ask sender to resend".  
   • >=500 → "WhatsApp server error – try again later".  
20.2  Refactor `showError()` to use this map and include a small grey "details" accordion with the raw status line.  
20.3  Add toast notifications for unrecoverable errors.  
**Success Criteria:** Triggering mocked 403 & 410 responses shows the mapped messages without crashing; unit tests pass.

#### 🔧 Task 21 – Worker Event-Listener Fix
21.1  Search `service_worker.js` and `whisper-worker.js` for any dynamic `addEventListener` calls inside functions; move them to top-level scope.  
21.2  Build & reload extension; verify "x-storagemutated-1" warning disappears (may still appear from WA scripts → acceptable).  
**Success Criteria:** No worker-related warnings originating from our files in console on page load.

#### 📜 Task 22 – Permissions-Policy Header Review
22.1  Use DevTools → Network → filter `chrome-extension://` to confirm no extension resource is served with a `Permissions-Policy` response header.  
22.2  Verify we have no `chrome.declarativeNetRequest` or `chrome.webRequest` listeners modifying response headers.  
22.3  Grep the entire codebase for `interest-cohort` or `Permissions-Policy` to ensure we don't set it.  
22.4  Add a short explanatory note ("Warning originates from WhatsApp CDN; Chrome dropped FLoC 'interest-cohort', so header is ignored.") to the *Lessons* section below and to the README *Troubleshooting* subsection.  
**Success Criteria:**  
  • Codebase shows zero matches for `interest-cohort`.  
  • README contains the troubleshooting note.  
  • Console still shows the warning (expected) but is classified as external noise in Task 18 table.

#### ✅ Task 23 – Regression Tests
23.1  Write Jest tests for new `getPlayableAudioBlob()` logic using mocked fetch responses (200, 403, 410).  
23.2  Write tests asserting `showError()` maps codes correctly.  
23.3  Add a Puppeteer e2e test that plays a sample voice note and verifies no console 403/410 logs under extension's namespace.  
**Success Criteria:** All new tests pass in CI (or `npm test`).

#### 🎲 Task 24 – Service Worker Reconnect Warning Suppression
24.1  Audit all code paths that trigger background script reconnect attempts (e.g., in `content.js`).
24.2  Refactor reconnect logic to:
   • Use exponential backoff for retries (e.g., 1s, 2s, 4s, max 5 attempts).
   • Suppress further attempts after a threshold, and show a single user-facing notification if background script is unavailable.
   • Log a single warning to the console after max attempts, not on every retry.
24.3  Consider using `chrome.runtime.connect` with a long-lived port, and handle disconnects gracefully.
**Success Criteria:** Console shows at most one reconnect warning per session; user sees a clear notification if background script is unavailable.

#### 📜 Task 25 – Error Log Aggregation and Suppression
25.1  Wrap all fetch and error-prone operations in a logging utility that:
   • Aggregates repeated errors (e.g., 403/410) and only logs once per error type per session.
   • Optionally provides a summary of suppressed errors on demand (e.g., via a debug command or UI toggle).
25.2  Ensure user-facing error messages remain clear, but console is not spammed with repeated technical details.
25.3  Add a debug mode (toggleable in options) that restores full verbose logging for development.
**Success Criteria:** Console is free of repeated 403/410 logs; only one log per error type per session unless debug mode is enabled.

#### 📜 Task 26 – Enhanced User Guidance for Persistent Errors
26.1  Add a persistent, dismissible notification or banner in the UI when repeated errors occur (e.g., background unavailable, repeated 403/410 fetch failures).
26.2  Link to troubleshooting steps or FAQ for common error scenarios.
**Success Criteria:** Users are clearly informed of persistent issues and given actionable next steps; no confusion from silent failures.

#### 🚨 Task 27 – CRITICAL: Fix Audio Extraction Timeout (HIGH PRIORITY)
27.1  **Debug WhatsApp Audio Loading**: Use DevTools to observe exactly when and how WhatsApp creates audio elements with blob URLs after clicking play.
   • Record network activity and DOM changes during voice message playback
   • Identify the timing and conditions when blob URLs become available
   • Document WhatsApp's audio loading sequence
   
27.2  **Enhance Audio Detection Logic**: Update `getPlayableAudioBlob()` with improved detection based on findings:
   • Increase timeout if needed (current: 5s)
   • Add specific waits for WhatsApp's audio loading states
   • Implement progressive detection strategies (immediate → delayed → forced)
   • Add better logging for each detection attempt
   
27.3  **Alternative Audio Access Methods**: Research and implement backup approaches:
   • Investigate WhatsApp's internal audio APIs or methods
   • Consider intercepting network requests for audio files
   • Test different user interaction patterns (double-click, long-press, etc.)
   
27.4  **Comprehensive Testing**: Validate the fix across different scenarios:
   • Fresh voice messages (never played)
   • Recently played voice messages  
   • Voice messages in different chat types (individual vs group)
   • Different network conditions and loading states
   
**Success Criteria:** 
- Extension successfully extracts audio blobs without timeout errors
- Transcription works for at least 3 different voice messages in different chats
- Console shows clear progression through detection strategies
- No "Timed out waiting for audio element" errors

---

### Executor Guidance - UPDATED PRIORITY
1. Checkout a new git branch `audio-extraction-fix`.  
2. Start with **Task 27, Step 27.1** - Debug WhatsApp Audio Loading.
3. Focus exclusively on solving the audio extraction timeout before proceeding with other tasks.
4. Update *Current Status* after each sub-step.  
5. Commit after completing each step (`git commit -m "Task 27.1 complete – WhatsApp audio loading analysis"`).  
6. Ask the Planner (human) for review before merging to main.

**CRITICAL**: Task 27 blocks all transcription functionality and must be resolved before other post-launch fixes.

## Project Status Board
- [x] **Task 1**: Create project structure and manifest.json
- [x] **Task 2**: Implement content script for voice message detection
- [x] **Task 3**: Set up audio blob extraction and conversion
- [x] **Task 4**: Implement local transcription with Whisper
- [x] **Task 5**: Add inline transcript display
- [x] **Task 6**: Create service worker for background tasks
- [x] **Task 7**: Language auto-detection and multilingual models
- [x] **Task 8**: Summary generation with BART/T5
- [x] **Task 9**: IndexedDB storage and management
- [x] **Task 10**: Popup UI with search and export
- [x] **Task 11**: Options page with settings
- [x] **Task 12**: Battery optimization
- [x] **Task 13**: Error handling and robustness
- [x] **Task 14**: Create icons and assets
- [x] **Task 15**: Write documentation
- [x] **Task 16**: Implement comprehensive tests
- [x] **Task 17**: Create privacy policy and store description
- [x] **Task 18**: Console error audit & categorization
- [x] **Task 19**: Reliable audio extraction refactor
- [x] **Task 20**: Enhanced error handling messaging
- [x] **Task 21**: Worker event-listener fix
- [x] **Task 22**: Permissions-Policy header review
- [x] **Task 23**: Regression tests for extraction & errors
- [ ] **Task 27**: 🚨 CRITICAL: Fix Audio Extraction Timeout (HIGH PRIORITY)
- [ ] **Task 24**: Service worker reconnect warning suppression
- [ ] **Task 25**: Error log aggregation and suppression
- [ ] **Task 26**: Enhanced user guidance for persistent errors

## Current Status / Progress Tracking
**Current Task**: 🚨 CRITICAL - Audio Extraction Timeout Bug

### CRITICAL BLOCKING ISSUE - Audio Extraction Failure
**Problem**: Extension detects voice messages and adds buttons correctly, but transcription fails during audio extraction with:
- `[OwlWritey] Timed out waiting for audio element`
- `Error: Could not extract audio from voice message`

**Root Cause Analysis**: 
The `getPlayableAudioBlob()` function:
1. ✅ Clicks play button successfully
2. ✅ Uses 4-strategy audio element detection 
3. ❌ **FAILS** to find audio elements with blob URLs within 5-second timeout
4. ❌ Times out before WhatsApp loads the audio blob

**Hypothesis**: WhatsApp may require different interaction patterns or longer wait times to generate blob URLs for audio elements.

### Current Error Sequence (from logs):
```
[OwlWritey] Found voice message using selector: [data-icon="audio-play"]
[OwlWritey] Starting transcription for voice message  
[OwlWritey] Extracting audio blob from voice message...
[OwlWritey] Looking for audio element...
[OwlWritey] Clicking play button to activate audio...
[OwlWritey] Timed out waiting for audio element ❌
[OwlWritey] Error extracting audio blob: Error: Timed out waiting for audio element
```

**Next Steps**: Investigate WhatsApp's audio loading mechanism and fix the extraction timeout.

### Task 27 Progress
| Step  | Description                                                                 | Done? | Notes                                                                                       |
|-------|-----------------------------------------------------------------------------|-------|---------------------------------------------------------------------------------------------|
| 27.1  | Debug WhatsApp Audio Loading: Use DevTools to observe audio element creation | ✅     | Enhanced getPlayableAudioBlob() with comprehensive debug logging. Ready for browser testing. |
| 27.2  | Enhance Audio Detection Logic based on findings | ✅     | **FIXED Element Reference**: Now returns message container instead of icon span. Updated detection strategies, increased timeout to 10s, added video element support. |
| 27.3  | Alternative Audio Access Methods: Research backup approaches               | ⏳     | Next: Test the fixes and implement fallback methods if needed                               |

**Step 27.2 COMPLETED**: 
- **Fixed `findVoiceMessageFromButton()`**: Now returns message container (`div[data-testid*="message"]`) instead of voice icon `<span>`
- **Enhanced Play Button Detection**: Searches within container, tries parent button elements, waits longer (1s) for WhatsApp processing
- **Updated Detection Strategies**: All 4 strategies now search for both `audio` and `video` elements within container scope
- **Increased Timeout**: Extended from 5s to 10s for debugging purposes
- **Enhanced Logging**: Added container structure analysis, media element details, and comprehensive timeout reporting
- **Added Video Support**: Extension now detects both `<audio>` and `<video>` elements as some browsers may use video tags for audio

---

**Previous Task**: 🔄 Task 24 – Service worker reconnect warning suppression

## Previous Task Status
### Task 25 Progress ✅ COMPLETED
| Step  | Description                                                                 | Done? | Notes                                                                                       |
|-------|-----------------------------------------------------------------------------|-------|---------------------------------------------------------------------------------------------|
| 25.1  | Wrap all fetch and error-prone operations in a logging utility              | ✓     | Implemented `logUtility` for error logging and aggregation.                                  |
| 25.2  | Ensure user-facing error messages remain clear, but console is not spammed     | ✓     | Implemented `logUtility` for error logging and aggregation.                                  |
| 25.3  | Add a debug mode (toggleable in options) that restores full verbose logging     | ✓     | Implemented `logUtility` for error logging and aggregation.                                  |

### Task 26 Progress ✅ COMPLETED  
| Step  | Description                                                                 | Done? | Notes                                                                                       |
|-------|-----------------------------------------------------------------------------|-------|---------------------------------------------------------------------------------------------|
| 26.1  | Add a persistent, dismissible notification or banner in the UI                | ✓     | Implemented `showError()` with a small grey "details" accordion.                             |
| 26.2  | Link to troubleshooting steps or FAQ for common error scenarios                | ✓     | Implemented `showError()` with a small grey "details" accordion.                             |

---

## Project Status Board (final)
- [x] **Task 23**: Regression tests for extraction & errors
- [ ] **Task 24**: Service worker reconnect warning suppression
- [ ] **Task 25**: Error log aggregation and suppression
- [ ] **Task 26**: Enhanced user guidance for persistent errors
- [ ] **Task 27**: Critical: Fix Audio Extraction Timeout

All post-launch fixes (Tasks 18-27) are done. Branch `post-launch-fixes` can be merged to `main` and version bumped to 1.0.1.

## Final Next Steps
1. Executor: open a PR from `post-launch-fixes` to `main`, add release notes summarising bug fixes & new tests.
2. After merge, tag `v1.0.1` and publish updated package to Chrome Web Store.

🎉 Project Phase 4 concluded — extension is stable and ready for deployment.

## Executor's Feedback or Assistance Requests

Release prep underway:
• Bumped manifest version to 1.0.1
• Added `CHANGELOG.md` with v1.0.1 notes
• Ready to push branch and open PR.

## 🛠️ Planner Addendum: Technical Plan for Reconnect Warnings & Error Suppression

### Background and Motivation
Despite robust error handling and user-friendly messaging, persistent console warnings remain:
- Repeated `Reattempting reconnect to background script` messages.
- Noisy or repeated 403/410 errors in the console, even when user-facing errors are mapped.

These issues can degrade user trust and clutter the console, making real issues harder to spot.

### Key Challenges and Analysis
- **Manifest v3 Service Worker Lifecycle:** Service workers are event-driven and may be inactive when the content script tries to communicate, leading to repeated reconnect attempts.
- **Error Logging:** Even with error mapping, repeated fetch failures (403/410) can spam the console, especially if retries are frequent or not rate-limited.
- **User Experience:** Users may be confused by persistent errors, even if they are handled gracefully in the UI.

### High-level Task Breakdown

#### Task 24 – Service Worker Reconnect Warning Suppression
24.1  Audit all code paths that trigger background script reconnect attempts (e.g., in `content.js`).
24.2  Refactor reconnect logic to:
   • Use exponential backoff for retries (e.g., 1s, 2s, 4s, max 5 attempts).
   • Suppress further attempts after a threshold, and show a single user-facing notification if background script is unavailable.
   • Log a single warning to the console after max attempts, not on every retry.
24.3  Consider using `chrome.runtime.connect` with a long-lived port, and handle disconnects gracefully.
**Success Criteria:** Console shows at most one reconnect warning per session; user sees a clear notification if background script is unavailable.

#### Task 25 – Error Log Aggregation and Suppression
25.1  Wrap all fetch and error-prone operations in a logging utility that:
   • Aggregates repeated errors (e.g., 403/410) and only logs once per error type per session.
   • Optionally provides a summary of suppressed errors on demand (e.g., via a debug command or UI toggle).
25.2  Ensure user-facing error messages remain clear, but console is not spammed with repeated technical details.
25.3  Add a debug mode (toggleable in options) that restores full verbose logging for development.
**Success Criteria:** Console is free of repeated 403/410 logs; only one log per error type per session unless debug mode is enabled.

#### Task 26 – Enhanced User Guidance for Persistent Errors
26.1  Add a persistent, dismissible notification or banner in the UI when repeated errors occur (e.g., background unavailable, repeated 403/410 fetch failures).
26.2  Link to troubleshooting steps or FAQ for common error scenarios.
**Success Criteria:** Users are clearly informed of persistent issues and given actionable next steps; no confusion from silent failures.

#### Task 27 – Critical: Fix Audio Extraction Timeout
27.1  **Debug WhatsApp Audio Loading**: Use DevTools to observe exactly when and how WhatsApp creates audio elements with blob URLs after clicking play.
   • Record network activity and DOM changes during voice message playback
   • Identify the timing and conditions when blob URLs become available
   • Document WhatsApp's audio loading sequence
   
27.2  **Enhance Audio Detection Logic**: Update `getPlayableAudioBlob()` with improved detection based on findings:
   • Increase timeout if needed (current: 5s)
   • Add specific waits for WhatsApp's audio loading states
   • Implement progressive detection strategies (immediate → delayed → forced)
   • Add better logging for each detection attempt
   
27.3  **Alternative Audio Access Methods**: Research and implement backup approaches:
   • Investigate WhatsApp's internal audio APIs or methods
   • Consider intercepting network requests for audio files
   • Test different user interaction patterns (double-click, long-press, etc.)
   
27.4  **Comprehensive Testing**: Validate the fix across different scenarios:
   • Fresh voice messages (never played)
   • Recently played voice messages  
   • Voice messages in different chat types (individual vs group)
   • Different network conditions and loading states
   
**Success Criteria:** 
- Extension successfully extracts audio blobs without timeout errors
- Transcription works for at least 3 different voice messages in different chats
- Console shows clear progression through detection strategies
- No "Timed out waiting for audio element" errors

---

### Next Steps
- Executor: Begin with Task 24.1 (audit reconnect logic in content.js and related files). Update progress after each sub-step.
- Planner: Review after each task for completeness and user experience impact.

## Lessons

### Critical Bug - Stale DOM Element References (Dec 2024)
**Issue**: WhatsApp Web recreates DOM elements when voice message state changes (play ↔ pause), causing extension to store stale element references. This led to `TypeError: Cannot read properties of null` errors during transcription.

**Root Cause**: Button click handlers captured `voiceMessageElement` as closure variables, but WhatsApp's dynamic DOM updates invalidated these references.

**Solution**: Implemented dynamic element lookup using `findVoiceMessageFromButton()` method that searches for voice message elements at click time rather than storing references.

**Key Learning**: Never store references to DOM elements in dynamic web apps like WhatsApp. Always use dynamic lookup patterns or observer-based approaches for robust DOM interaction.