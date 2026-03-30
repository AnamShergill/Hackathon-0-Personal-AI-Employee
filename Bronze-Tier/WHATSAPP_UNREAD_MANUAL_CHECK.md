# Manual WhatsApp Unread Detection Guide

## Problem
The watcher is not detecting your unread WhatsApp messages.

## Manual Inspection Steps

1. **Open WhatsApp Web in your regular browser**
   - Go to https://web.whatsapp.com
   - Make sure you have at least ONE unread message visible

2. **Open Developer Tools**
   - Press F12 or Right-click → Inspect
   - Go to the "Elements" or "Inspector" tab

3. **Find an UNREAD chat in the list**
   - Look for a chat with a green dot or unread count badge
   - Right-click on that chat → Inspect Element

4. **Look for these attributes** (write down what you find):
   
   ### Check for unread badge:
   ```html
   <span data-testid="icon-unread-count">1</span>
   ```
   - ✅ Found? → Note the exact `data-testid` value
   - ❌ Not found? → Continue to next check

   ### Check for aria-label with "unread":
   ```html
   <div aria-label="1 unread message from Contact Name">
   ```
   - ✅ Found? → Note the exact text pattern
   - ❌ Not found? → Continue to next check

   ### Check for bold text (strong tags):
   ```html
   <strong>Contact Name</strong>
   <strong>Message preview text...</strong>
   ```
   - ✅ Found? → Unread chats usually have bold sender names
   - ❌ Not found? → Continue to next check

   ### Check for green dot or status icon:
   ```html
   <span data-icon="unread-count"></span>
   <span data-icon="status-unread"></span>
   ```
   - ✅ Found? → Note the exact `data-icon` value

   ### Check the parent container:
   ```html
   <div role="row" ...>  <!-- or role="listitem" -->
     <div data-testid="cell-frame-container-...">
       <!-- chat content here -->
     </div>
   </div>
   ```
   - Note the `role` attribute value
   - Note any `data-testid` attributes

5. **Compare with a READ chat**
   - Inspect a chat that has NO unread messages
   - What's different? (no badge, no bold, no green dot?)

## What to Report Back

Please provide:
1. **Screenshot** of the unread chat in DevTools showing the HTML
2. **Exact HTML snippet** of the unread indicator (copy from DevTools)
3. **Any `data-testid` values** you see on the unread chat
4. **Any `aria-label` text** that mentions "unread"
5. **Differences** between read and unread chats

## Quick Test Commands

Once you have the information, we can update the selectors in `whatsapp_watcher.py`.

### Current selectors being checked:
```python
# Strategy 1: Unread badge with count
'span[data-testid="icon-unread-count"]'

# Strategy 2: Aria-label with "unread"
'div[aria-label*="unread" i]'

# Strategy 3: Unread icon markers
'span[data-icon*="unread"]'

# Strategy 4: Bold text (strong tags)
'strong'
```

## Alternative: Use Browser Console

Open Console tab (F12 → Console) and run:

```javascript
// Find all chat items
const chats = document.querySelectorAll('div[role="row"]');
console.log(`Total chats: ${chats.length}`);

// Check first 5 chats for unread indicators
for (let i = 0; i < Math.min(5, chats.length); i++) {
  const chat = chats[i];
  const name = chat.querySelector('span[title]')?.title || 'Unknown';
  const badge = chat.querySelector('[data-testid="icon-unread-count"]');
  const aria = chat.querySelector('[aria-label*="unread" i]');
  const bold = chat.querySelectorAll('strong').length;
  
  console.log(`Chat ${i+1}: ${name}`);
  console.log(`  - Badge: ${badge ? badge.innerText : 'NO'}`);
  console.log(`  - Aria: ${aria ? 'YES' : 'NO'}`);
  console.log(`  - Bold elements: ${bold}`);
}
```

Copy the console output and share it!
