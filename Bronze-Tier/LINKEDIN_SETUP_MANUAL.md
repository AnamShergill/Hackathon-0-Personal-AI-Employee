# LinkedIn Setup - Manual Guide

## ✅ Dependencies Installed
- schedule ✅
- playwright ✅  
- chromium browser ✅

## 📁 Folders Created
- Watchers/linkedin_session/ ✅
- Pending_Approval/ ✅
- Approved/ ✅

## 🔐 First-Time Login (DO THIS NOW)

### Step 1: Open LinkedIn Poster
The browser should already be open from the setup script. If not, run:
```bash
python Watchers/linkedin_poster.py
```

### Step 2: Login to LinkedIn
In the browser window that opened:
1. **Enter your LinkedIn email**
2. **Enter your LinkedIn password**
3. **Complete 2FA** if prompted (code from phone/email)
4. **Wait for feed to load** - you should see your LinkedIn homepage

### Step 3: Verify Login
Once you see your LinkedIn feed:
- You should see "Start a post" button
- You should see your profile picture in top right
- URL should be: https://www.linkedin.com/feed/

### Step 4: Session Saved!
The session is automatically saved to `Watchers/linkedin_session/`

You can close the browser or press Ctrl+C in the terminal.

## ✅ Verification

### Check Session Files
```bash
ls Watchers/linkedin_session/
```
You should see several files (cookies, local storage, etc.)

### Check Screenshots
```bash
ls Logs/linkedin_*.png
```
You should see a success screenshot.

## 🧪 Test Posting

### Option 1: Interactive Test
```bash
python Watchers/linkedin_poster.py
```
- Browser opens (already logged in!)
- You'll be asked if you want to post a test message
- Type 'yes' to post
- Check your LinkedIn feed - post should appear

### Option 2: Generate and Post
```bash
# 1. Generate a post
python -c "exec(open('Skills/08_LINKEDIN_POST_GENERATOR.md').read().split('\`\`\`python')[1].split('\`\`\`')[0])"

# 2. Check it
cat Pending_Approval/linkedin_post_*.md

# 3. Approve it
mv Pending_Approval/linkedin_post_*.md Approved/

# 4. Post it
python Watchers/linkedin_poster.py Approved/linkedin_post_*.md
```

### Option 3: Full Automation
```bash
# Terminal 1: Start approved watcher
python Watchers/approved_watcher.py

# Terminal 2: Generate and approve
python -c "exec(open('Skills/08_LINKEDIN_POST_GENERATOR.md').read().split('\`\`\`python')[1].split('\`\`\`')[0])"
sleep 5
mv Pending_Approval/linkedin_post_*.md Approved/

# Watch Terminal 1 - should auto-post within 30 seconds!
```

## 🎯 Verification Checklist

- [ ] Browser opened to LinkedIn
- [ ] Logged in successfully
- [ ] Session files created in `Watchers/linkedin_session/`
- [ ] Screenshot saved in `Logs/`
- [ ] Test post appeared on LinkedIn feed
- [ ] Approved watcher can detect and post files

## 🐛 Troubleshooting

### Browser won't open
```bash
# Check playwright installation
playwright install chromium

# Try again
python Watchers/linkedin_poster.py
```

### Login fails / 2FA issues
- Complete 2FA in the browser
- Wait for feed to fully load
- Don't close browser too quickly

### Session not saving
- Check folder exists: `ls Watchers/linkedin_session/`
- Check permissions
- Try running as admin if needed

### Post not appearing
- Check screenshots in `Logs/`
- Verify selectors are working
- Check LinkedIn for rate limits
- Try manual post in regular browser first

## 📊 Current Status

After completing the steps above, you should have:
- ✅ LinkedIn session configured
- ✅ Browser automation working
- ✅ Test post successful
- ✅ Ready for production use

## 🚀 Next Steps

1. **Start all watchers**:
   ```bash
   python run_all_watchers.py
   ```

2. **Generate daily posts**:
   - Scheduler will auto-generate at 10 AM
   - Or run manually anytime

3. **Review and approve**:
   - Check `Pending_Approval/`
   - Edit if needed
   - Move to `Approved/`

4. **Auto-posting**:
   - Approved watcher posts within 30 seconds
   - Check LinkedIn to verify

## 🎉 Silver Tier Complete!

Once you've verified LinkedIn posting works, Silver Tier is 100% done!

You now have:
- ✅ Gmail automation
- ✅ WhatsApp automation
- ✅ LinkedIn automation
- ✅ HITL workflow
- ✅ Scheduling
- ✅ Complete monitoring

**Congratulations!** 🎊

---

**Quick Commands**:
- Generate post: See QUICK_REFERENCE.md
- Start watchers: `python run_all_watchers.py`
- Check status: `cat Dashboard.md`
