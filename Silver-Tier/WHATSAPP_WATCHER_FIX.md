# WhatsApp Watcher Fix - Silver Tier

## Problem
The WhatsApp watcher was failing with timeout errors when trying to detect the chat list:
```
ERROR: Page.wait_for_selector: Timeout 30000ms exceeded
waiting for locator("div[aria-label=\"Chat list\"]")
```

## Root Cause
WhatsApp Web's DOM structure changed in 2025-2026:
- Obfuscated class names
- Removed or changed aria-labels
- Moved from `role="listitem"` to `role="row"` (grid structure)
- More reliance on `data-testid` attributes

## Solution Implemented

### 1. Updated Selectors (Multi-Fallback Strategy)
```python
SELECTORS = {
    'qr_code': 'canvas[aria-label*="Scan"]',  # More flexible
    'chat_list_primary': '[data-testid="chat-list"]',  # Primary
    'chat_list_role': 'div[role="grid"]',  # Fallback 1
    'chat_list_side': '#pane-side',  # Fallback 2 (most stable)
    'chat_item': 'div[role="row"]',  # Updated from listitem
}
```

### 2. Improved Navigation Logic
- **4-tier fallback strategy** for detecting chat list:
  1. Try `data-testid="chat-list"` (20s timeout)
  2. Try `role="grid"` (20s timeout)
  3. Try `#pane-side` ID selector (20s timeout)
  4. Try search box as indicator (20s timeout)
  
- **Network idle wait**: Added `wait_for_load_state('networkidle')` after navigation
- **Buffer time**: 3-5 second delays for dynamic content
- **Debug screenshots**: Auto-capture on failure with timestamp
- **Automatic reload**: Retry once if all strategies fail

### 3. Improved Message Detection
- Removed page reload on every check (too slow)
- Multiple fallback selectors for chat items:
  - Primary: `div[role="row"]`
  - Fallback 1: `div[role="listitem"]`
  - Fallback 2: `[data-testid^="cell-frame-container"]`

### 4. Debug Tools Added
Created `debug_whatsapp_selectors.py` to:
- Test all selector strategies
- Show element counts
- Display attributes
- Allow manual inspection (60s window)

## Test Results
✅ **Working!**
```
INFO: Strategy 2: Looking for chat list by role...
INFO: ✅ Chat list found via role attribute
INFO: ✅ WhatsApp Web loaded successfully
INFO: Found 67 chat items
INFO: WhatsApp Watcher completed cycle, processed 0 messages
```

## How to Use

### Run WhatsApp Watcher Only
```bash
python -m Watchers.whatsapp_watcher
```

### Run Both Watchers (Gmail + WhatsApp)
```bash
python run_both_watchers.py
```

### Debug Selectors
```bash
python debug_whatsapp_selectors.py
```

## Configuration
- **Interval**: 60 seconds (configurable in `__init__`)
- **Headless**: False by default (set to True after QR scan)
- **Session**: Saved in `Watchers/whatsapp_session/`
- **Logs**: `Logs/whatsapp_watcher.log`
- **Output**: `.md files in `Needs_Action/`

## Future Maintenance
If selectors break again:
1. Run `debug_whatsapp_selectors.py`
2. Inspect browser with F12 DevTools
3. Update `SELECTORS` dictionary
4. Add new fallback strategy if needed

## Key Improvements
- ✅ Robust multi-fallback selector strategy
- ✅ Network idle detection
- ✅ Auto-retry with reload
- ✅ Debug screenshots on failure
- ✅ No page reload on every check (faster)
- ✅ Comprehensive logging
- ✅ Session persistence working
- ✅ Found 67 chats successfully

## Next Steps
1. Send test WhatsApp message to trigger unread detection
2. Verify `.md` file creation in `Needs_Action/`
3. Test with urgent keywords (URGENT, ASAP, etc.)
4. Integrate with Ralph Wiggum loop for processing
5. Consider headless mode after testing
