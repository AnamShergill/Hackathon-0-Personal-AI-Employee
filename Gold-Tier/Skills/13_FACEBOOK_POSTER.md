# Skill 13: Facebook Poster

## Purpose
Automatically post content to Facebook (personal profile or business page) with text and optional images. Follows HITL approval workflow for all posts to ensure brand safety and compliance with Facebook's Terms of Service.

## When to Use
- Scheduled social media content
- Business updates and announcements
- Product/service promotions
- Community engagement posts
- Event announcements
- Behind-the-scenes content
- Customer success stories

## When NOT to Use
- Spam or repetitive content
- Prohibited content (violence, hate speech, etc.)
- Misleading information
- Content violating Facebook ToS
- High-frequency posting (>3 posts/day)
- Automated engagement (likes, comments)

---

## Input Format

### Action File Structure
```markdown
---
type: facebook_post
approved: false
priority: medium
created: YYYY-MM-DD HH:MM:SS
visibility: public|friends|only_me
---

# Facebook Post: [Title]

## Post Text
[Your post content here]

## Image (Optional)
path: /path/to/image.jpg
alt_text: Image description

## Metadata
- Visibility: public|friends|only_me
- Scheduled: YYYY-MM-DD HH:MM (optional)
- Tags: tag1, tag2, tag3 (optional)
```

---

## HITL (Human-in-the-Loop) Rules

### ALWAYS Require Approval
1. **All posts** - No auto-posting without human review
2. **Promotional content** - Sales, marketing, product launches
3. **Long posts** - Over 500 characters
4. **Posts with images** - Visual content needs review
5. **Sensitive topics** - Politics, religion, controversial subjects
6. **Business-critical** - Company announcements, official statements

### Safety Checks
- ✅ Content reviewed for brand alignment
- ✅ No prohibited content
- ✅ Appropriate visibility setting
- ✅ Image quality and relevance verified
- ✅ Tone and messaging approved
- ✅ Compliance with Facebook ToS

### Never Auto-Execute
- ❌ Posting without approval
- ❌ Automated likes or comments
- ❌ Mass friend requests
- ❌ Scraping or data collection
- ❌ Impersonation
- ❌ Spam or repetitive content

---

## Post Examples

### Example 1: Business Update
```markdown
---
type: facebook_post
approved: false
priority: medium
visibility: public
---

# Facebook Post: Q1 Milestone Achievement

## Post Text
🎉 Exciting news! We've just hit a major milestone - 1000+ businesses automated with our AI Employee system!

Thank you to our amazing clients for trusting us with your business operations. Your success is our success! 💼

What's next? We're expanding to support even more communication channels and adding advanced analytics.

Stay tuned for more updates! 🚀

#BusinessAutomation #AIEmployee #Milestone #ThankYou

## Metadata
- Visibility: public
- Tags: business, automation, milestone
```

### Example 2: Post with Image
```markdown
---
type: facebook_post
approved: false
priority: medium
visibility: public
---

# Facebook Post: New Feature Announcement

## Post Text
📢 New Feature Alert! 

Introducing multi-channel dashboard - manage all your communications from ONE place!

✅ Email
✅ WhatsApp  
✅ LinkedIn
✅ Facebook

See it in action in the image below! 👇

Try it free for 14 days: [link]

## Image
path: assets/dashboard-screenshot.png
alt_text: Multi-channel communication dashboard interface

## Metadata
- Visibility: public
- Tags: newfeature, dashboard, automation
```

### Example 3: Community Engagement
```markdown
---
type: facebook_post
approved: false
priority: low
visibility: public
---

# Facebook Post: Question for Community

## Post Text
Quick question for business owners: 🤔

What's your biggest challenge with managing customer communications?

A) Too many channels to monitor
B) Slow response times
C) Missing important messages
D) All of the above

Drop your answer in the comments! We're building solutions based on YOUR needs.

## Metadata
- Visibility: public
- Tags: community, question, engagement
```

---

## Execution

### Workflow
1. **Create action file** in Pending_Approval/
2. **Human reviews** content, image, visibility
3. **Approve** by moving to Approved/
4. **approved_watcher** detects facebook_post
5. **facebook_poster.py** executes posting
6. **Result logged** in Approved/Done/

### Command (Manual Testing)
```bash
cd Gold-Tier
python actions/facebook_poster.py --file Approved/facebook_post_test.md
```

---

## Technical Implementation

### Browser Automation
- **Tool:** Playwright (Chromium)
- **Session:** Persistent in facebook_session/
- **Login:** One-time manual, cookies saved
- **Selectors:** Role-based, aria-label, data-testid fallbacks

### Posting Process
1. Load persistent session
2. Navigate to Facebook
3. Find "What's on your mind?" composer
4. Enter post text
5. Upload image (if provided)
6. Set visibility
7. Click Post button
8. Wait for confirmation
9. Take success screenshot
10. Log result

### Error Handling
- Session expired → Prompt for re-login
- Selector not found → Try fallback selectors
- Network error → Retry with exponential backoff
- Rate limit → Log warning, schedule retry
- Any error → Screenshot + detailed log

---

## Safety & Compliance

### Facebook Terms of Service
- ✅ No automated engagement (likes, comments, shares)
- ✅ No spam or repetitive content
- ✅ No misleading information
- ✅ Respect rate limits (max 3 posts/day recommended)
- ✅ No data scraping
- ✅ No impersonation

### Rate Limiting
- **Maximum:** 3 posts per day
- **Minimum interval:** 4 hours between posts
- **Burst protection:** No more than 1 post per hour
- **Weekly limit:** 15 posts per week

### Content Guidelines
- ✅ Original content or properly attributed
- ✅ Appropriate for public audience
- ✅ No prohibited content
- ✅ Brand-aligned messaging
- ✅ Factually accurate
- ✅ Professional tone

---

## Logging & Monitoring

### Log File
`Logs/facebook_poster.log`

### Logged Events
- Session initialization
- Login attempts
- Post attempts
- Success/failure
- Errors and exceptions
- Screenshots saved
- Rate limit checks

### Metrics to Track
- Total posts published
- Success rate
- Average posting time
- Errors encountered
- Session expiry frequency

---

## Troubleshooting

### Issue: Session Expired
**Cause:** Facebook logged out or cookies expired  
**Fix:**
1. Delete facebook_session/ folder
2. Run facebook_poster.py
3. Log in manually when browser opens
4. Session will be saved for future use

### Issue: Selector Not Found
**Cause:** Facebook UI changed  
**Fix:**
1. Check Logs/ for error screenshots
2. Update selectors in facebook_poster.py
3. Use browser DevTools to find new selectors
4. Test with --debug flag

### Issue: Post Not Appearing
**Cause:** Visibility setting or Facebook review  
**Fix:**
1. Check visibility setting (public/friends/only_me)
2. Wait 5-10 minutes (Facebook may review)
3. Check Facebook notifications for issues
4. Verify post in Activity Log

### Issue: Rate Limited
**Cause:** Too many posts in short time  
**Fix:**
1. Wait 4+ hours before next post
2. Check rate limit tracking in logs
3. Reduce posting frequency
4. Spread posts throughout the day

---

## Configuration

### Environment Variables
```bash
# In .env (optional)
FACEBOOK_SESSION_DIR=facebook_session
FACEBOOK_MAX_POSTS_PER_DAY=3
FACEBOOK_MIN_INTERVAL_HOURS=4
FACEBOOK_HEADLESS=false  # Set true for production
```

### Visibility Options
- **public:** Anyone can see
- **friends:** Only friends can see
- **only_me:** Only you can see (draft/test)

---

## Integration with Orchestrator

### Detection in approved_watcher.py
```python
def _determine_file_type(self, file_path: Path) -> str:
    filename = file_path.name.lower()
    
    if 'facebook' in filename:
        return 'facebook_post'
    
    # Check content
    with open(file_path, 'r') as f:
        content = f.read()
        if 'type: facebook_post' in content or 'type: "facebook_post"' in content:
            return 'facebook_post'
```

### Execution in approved_watcher.py
```python
def _post_to_facebook(self, file_path: str) -> bool:
    logger.info(f"[FACEBOOK] Posting to Facebook: {file_path}")
    
    try:
        result = subprocess.run(
            [sys.executable, 'actions/facebook_poster.py', '--file', file_path],
            capture_output=True,
            text=True,
            timeout=120
        )
        
        if result.returncode == 0:
            logger.info("✅ Facebook post successful")
            return True
        else:
            logger.error(f"Facebook post failed: {result.stderr}")
            return False
            
    except Exception as e:
        logger.error(f"Error calling facebook_poster: {e}")
        return False
```

---

## Best Practices

### Content
- Keep posts concise (under 500 characters for best engagement)
- Use emojis sparingly for emphasis
- Include clear call-to-action
- Add relevant hashtags (3-5 max)
- Use high-quality images (1200x630px recommended)

### Timing
- Post during peak engagement hours (9am-3pm local time)
- Avoid weekends for business content
- Space posts 4+ hours apart
- Test different times to find what works

### Engagement
- Respond to comments promptly (manual)
- Monitor post performance
- Adjust strategy based on metrics
- Don't over-post (quality > quantity)

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

---

## Success Indicators

✅ Posts published successfully to Facebook  
✅ HITL approval workflow enforced  
✅ No ToS violations  
✅ Session persists across runs  
✅ Errors logged with screenshots  
✅ Rate limits respected  
✅ Content quality maintained  
✅ Audit trail complete

---

**Skill Status:** ✅ Active  
**Last Updated:** 2026-03-30  
**Owner:** AI Employee System (Gold Tier)  
**Dependencies:** Playwright, actions/facebook_poster.py, approved_watcher.py
