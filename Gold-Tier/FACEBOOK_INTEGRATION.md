# Facebook Integration Guide
**Gold Tier Phase 3: Social Media Outbound Expansion**  
**Date:** 2026-03-30  
**Status:** ✅ READY FOR SETUP

---

## Overview

Facebook posting capability has been added to the AI Employee system, following the same HITL approval workflow as LinkedIn. All posts require human review before publishing.

**Key Features:**
- ✅ Persistent browser session (login once)
- ✅ Text + image posting
- ✅ Visibility control (public/friends/only_me)
- ✅ Rate limiting (max 3 posts/day)
- ✅ Error handling and screenshots
- ✅ HITL approval workflow
- ✅ Audit trail and logging

---

## Setup Instructions

### Step 1: Install Dependencies

Facebook poster uses Playwright (already installed for LinkedIn).

**Verify Playwright:**
```bash
cd Gold-Tier
python -c "from playwright.sync_api import sync_playwright; print('✅ Playwright available')"
```

**If not installed:**
```bash
pip install playwright
playwright install chromium
```

### Step 2: First-Time Login

Run the Facebook poster in interactive mode for first-time setup:

```bash
cd Gold-Tier
python actions/facebook_poster.py
```

**What happens:**
1. Browser window opens
2. Facebook login page appears
3. **You manually log in:**
   - Enter your email and password
   - Complete 2FA if required
   - Wait for feed to load
4. Session is saved in `actions/facebook_session/`
5. Future posts will reuse this session

**Important:**
- Use your personal Facebook account or business page credentials
- Complete any security checks Facebook requires
- Wait for the feed to fully load before closing

### Step 3: Verify Setup

Test the connection:

```bash
cd Gold-Tier
python actions/facebook_poster.py
```

When prompted, type `yes` to post a test message.

**Expected result:**
- ✅ Browser opens with Facebook already logged in
- ✅ Test post appears in composer
- ✅ Post publishes successfully
- ✅ Screenshot saved in Logs/

---

## Usage

### Create a Facebook Post

**1. Create action file in Pending_Approval/:**

```markdown
---
type: facebook_post
approved: false
priority: medium
visibility: public
---

# Facebook Post: Your Title

## Post Text
Your post content here...

Can be multiple paragraphs.

Include emojis, hashtags, etc.

#YourHashtags #GoHere

## Image (Optional)
path: /path/to/image.jpg
alt_text: Image description

## Metadata
- Visibility: public
- Tags: tag1, tag2
```

**2. Review and approve:**
- Open the file in Pending_Approval/
- Review content, tone, and accuracy
- Edit if needed
- Move to Approved/ folder

**3. Automatic posting:**
- approved_watcher detects the file (30s polling)
- Calls actions/facebook_poster.py
- Posts to Facebook
- Moves file to Approved/Done/ with result

**4. Verify:**
- Check your Facebook profile/page
- Review post appearance
- Monitor engagement

---

## Workflow Diagram

```
Create Post → Pending_Approval/facebook_post_*.md
       ↓
Human Reviews → Edits if needed
       ↓
Approves → Moves to Approved/
       ↓
approved_watcher (30s poll) → Detects facebook_post
       ↓
actions/facebook_poster.py → Opens browser
       ↓
Facebook → Post published
       ↓
Screenshot saved → File moved to Done/
       ↓
Human verifies on Facebook
```

---

## Post Examples

### Example 1: Simple Text Post
```markdown
---
type: facebook_post
approved: false
visibility: public
---

# Facebook Post: Business Update

## Post Text
🎉 Great news! We've just launched our new AI Employee system!

It automates business communications across email, WhatsApp, and social media.

Check it out: [link]

#BusinessAutomation #AI #Innovation
```

### Example 2: Post with Image
```markdown
---
type: facebook_post
approved: false
visibility: public
---

# Facebook Post: Product Screenshot

## Post Text
📢 New feature alert!

Our multi-channel dashboard is now live. Manage all your communications from ONE place!

See it in action below 👇

Try it free: [link]

## Image
path: assets/dashboard-screenshot.png
alt_text: Multi-channel communication dashboard

## Metadata
- Visibility: public
```

### Example 3: Friends-Only Post
```markdown
---
type: facebook_post
approved: false
visibility: friends
---

# Facebook Post: Personal Update

## Post Text
Quick update for friends: Working on something exciting! 🚀

Building an AI system that automates business communications. It's been an amazing journey.

More details coming soon!

## Metadata
- Visibility: friends
```

---

## Rate Limiting

### Limits
- **Maximum:** 3 posts per day
- **Minimum interval:** 4 hours between posts
- **Weekly limit:** 15 posts per week

### Tracking
Rate limits are tracked in `Logs/facebook_rate_limit.json`

### If Rate Limited
```
❌ Rate limit exceeded: 3 posts in last 24 hours
   Maximum: 3 posts per day
   Please wait before posting again
```

**Solution:** Wait 4+ hours before next post

---

## Visibility Options

### Public
- **Who can see:** Everyone on Facebook
- **Use for:** Business announcements, promotions, public content
- **Setting:** `visibility: public`

### Friends
- **Who can see:** Only your Facebook friends
- **Use for:** Personal updates, behind-the-scenes, community posts
- **Setting:** `visibility: friends`

### Only Me
- **Who can see:** Only you
- **Use for:** Testing, drafts, private notes
- **Setting:** `visibility: only_me`

---

## Safety & Compliance

### Facebook Terms of Service
✅ No automated engagement (likes, comments, shares)  
✅ No spam or repetitive content  
✅ No misleading information  
✅ Respect rate limits  
✅ No data scraping  
✅ No impersonation  
✅ HITL approval for all posts

### Content Guidelines
- ✅ Original content or properly attributed
- ✅ Appropriate for public audience
- ✅ No prohibited content
- ✅ Brand-aligned messaging
- ✅ Factually accurate
- ✅ Professional tone

### Best Practices
- Post during peak hours (9am-3pm local time)
- Keep posts concise (under 500 characters)
- Use high-quality images (1200x630px)
- Include clear call-to-action
- Respond to comments promptly (manual)
- Monitor post performance

---

## Troubleshooting

### Issue: Session Expired
**Symptoms:** Browser shows login page  
**Cause:** Facebook logged out or cookies expired

**Fix:**
```bash
# Delete session folder
rm -rf Gold-Tier/actions/facebook_session

# Run poster again
cd Gold-Tier
python actions/facebook_poster.py

# Log in manually when browser opens
```

### Issue: Selector Not Found
**Symptoms:** "Could not find 'What's on your mind' button"  
**Cause:** Facebook UI changed

**Fix:**
1. Check error screenshot in Logs/
2. Open browser DevTools (F12)
3. Find new selector for the element
4. Update SELECTORS in facebook_poster.py
5. Test again

### Issue: Post Not Appearing
**Symptoms:** Script says success but post not visible  
**Cause:** Visibility setting or Facebook review

**Fix:**
1. Check visibility setting (public/friends/only_me)
2. Wait 5-10 minutes (Facebook may review)
3. Check Facebook Activity Log
4. Verify in Facebook notifications

### Issue: Rate Limited
**Symptoms:** "Rate limit exceeded" error  
**Cause:** Too many posts in 24 hours

**Fix:**
1. Wait 4+ hours before next post
2. Check `Logs/facebook_rate_limit.json`
3. Reduce posting frequency
4. Spread posts throughout the day

### Issue: Image Upload Failed
**Symptoms:** Post created but no image  
**Cause:** Image path incorrect or format unsupported

**Fix:**
1. Verify image path is correct
2. Check image format (JPG, PNG supported)
3. Ensure image size < 10MB
4. Try posting without image first

---

## Testing

### Test 1: Connection Test
```bash
cd Gold-Tier
python actions/facebook_poster.py
```

**Expected:**
- Browser opens
- Facebook loads (logged in)
- Prompts for test post
- Type `yes` to post
- Post appears on Facebook

### Test 2: File-Based Post
```bash
# Create test file
cd Gold-Tier

# Move to Approved
mv Pending_Approval/facebook_post_test_announcement.md Approved/

# Run watcher
python -c "import os; os.chdir('Gold-Tier'); from Watchers.approved_watcher import ApprovedWatcher; w = ApprovedWatcher(); w.run_once()"
```

**Expected:**
- Watcher detects file
- Calls facebook_poster.py
- Post published to Facebook
- File moved to Approved/Done/

### Test 3: End-to-End
1. Create post in Pending_Approval/
2. Review and move to Approved/
3. Wait 30 seconds (watcher interval)
4. Check Approved/Done/ for result
5. Verify post on Facebook

---

## Logging & Monitoring

### Log Files
- `Logs/facebook_poster.log` - All posting operations
- `Logs/facebook_rate_limit.json` - Rate limit tracking
- `Logs/approved_watcher.log` - Watcher operations

### Screenshots
- `facebook_login_success_*.png` - Login verification
- `facebook_pre_post_*.png` - Before posting
- `facebook_post_success_*.png` - After posting
- `facebook_error_*.png` - Error states

### Metrics
- Total posts published
- Success rate
- Average posting time
- Errors encountered
- Rate limit hits

---

## Integration with System

### Approved Watcher
- Detects `type: facebook_post` in files
- Calls `actions/facebook_poster.py --file [path]`
- Handles success/failure
- Moves files appropriately

### Main Orchestrator
- Routes Facebook post requests
- Coordinates with other skills
- Updates dashboard

### Skills
- **13_FACEBOOK_POSTER** - Posting skill documentation
- **08_LINKEDIN_POST_GENERATOR** - Similar pattern for LinkedIn

---

## Security Notes

### Session Security
- Session stored in `actions/facebook_session/`
- Contains cookies and authentication tokens
- **Do NOT commit to git** (already in .gitignore)
- Regenerate if compromised

### Access Control
- Only authorized users can approve posts
- All posts require HITL review
- No automated engagement
- Audit trail maintained

### Data Privacy
- Post content stored locally
- No external API calls
- Sensitive data in Pending_Approval/ (access controlled)

---

## Comparison: LinkedIn vs Facebook

| Feature | LinkedIn | Facebook |
|---------|----------|----------|
| Session persistence | ✅ Yes | ✅ Yes |
| Text posts | ✅ Yes | ✅ Yes |
| Image posts | ✅ Yes | ✅ Yes |
| Visibility control | ❌ No | ✅ Yes |
| Rate limiting | ❌ No | ✅ Yes (3/day) |
| HITL approval | ✅ Yes | ✅ Yes |
| Error screenshots | ✅ Yes | ✅ Yes |
| Logging | ✅ Yes | ✅ Yes |

---

## Future Enhancements

### Phase 4
- [ ] Facebook Page posting (in addition to profile)
- [ ] Video upload support
- [ ] Link preview customization
- [ ] Post scheduling (native Facebook scheduler)
- [ ] Analytics integration
- [ ] Multi-image carousel posts
- [ ] Story posting
- [ ] Reels/short video support
- [ ] Comment monitoring and auto-response
- [ ] Engagement metrics tracking

---

## Quick Reference

### Commands
```bash
# First-time setup
cd Gold-Tier
python actions/facebook_poster.py

# Test posting
python actions/facebook_poster.py
# Type 'yes' when prompted

# Post specific file
python actions/facebook_poster.py --file Approved/facebook_post_test.md

# Check rate limits
cat Logs/facebook_rate_limit.json

# View logs
cat Logs/facebook_poster.log
tail -f Logs/facebook_poster.log  # Live monitoring
```

### File Locations
- **Poster Script:** `actions/facebook_poster.py`
- **Skill Docs:** `Skills/13_FACEBOOK_POSTER.md`
- **Session:** `actions/facebook_session/`
- **Logs:** `Logs/facebook_poster.log`
- **Screenshots:** `Logs/facebook_*.png`
- **Rate Limits:** `Logs/facebook_rate_limit.json`

### Workflow
```
Create → Pending_Approval/ → Review → Approved/ → 
approved_watcher → facebook_poster.py → Facebook → Done/
```

---

## Success Indicators

✅ Browser opens with Facebook logged in  
✅ Post composer opens automatically  
✅ Text typed correctly  
✅ Image uploaded (if provided)  
✅ Visibility set correctly  
✅ Post published successfully  
✅ Screenshot captured  
✅ File moved to Done/  
✅ Rate limits respected  
✅ No ToS violations

---

## Support

### If You Need Help
1. Check error screenshots in Logs/
2. Review facebook_poster.log
3. Verify session is valid (re-login if needed)
4. Test with simple text post first
5. Check Facebook for any account issues

### Common Issues
- **Session expired:** Delete facebook_session/ and re-login
- **Selector not found:** Facebook UI changed, update selectors
- **Rate limited:** Wait 4+ hours between posts
- **Post not visible:** Check visibility setting

---

## Status

**Implementation:** ✅ Complete  
**Testing:** ⏳ Awaiting first-time setup  
**Production Ready:** ✅ Yes (after setup)

**Next Steps:**
1. Run first-time setup: `python actions/facebook_poster.py`
2. Log in to Facebook manually
3. Test with sample post
4. Approve test post in Pending_Approval/
5. Verify end-to-end workflow

---

**Documentation Version:** 1.0  
**Last Updated:** 2026-03-30  
**Owner:** AI Employee System (Gold Tier)  
**Status:** Ready for first-time setup
