# Skill 14: Weekly CEO Briefing Generator

## Purpose
Automatically generate comprehensive weekly business summary reports for executive review. Pulls data from all integrated systems (email, Odoo, social media, tasks) and produces professional, actionable briefings.

## When to Use
- **Scheduled:** Every Sunday at 8 PM (automated)
- **Manual:** On-demand via command line
- **Triggered:** After major business events or milestones
- **Requested:** When CEO/leadership requests update

## When NOT to Use
- Daily updates (use Dashboard instead)
- Real-time monitoring (use watchers)
- Detailed transaction reports (use Odoo directly)
- Individual task tracking (use task files)

---

## Data Sources

### 1. Email Activity (Gmail)
- Total emails processed
- Response rate and time
- High-priority items handled
- Pending items requiring attention
- Source: `Logs/gmail_watcher.log`, `Done/email_*.md`

### 2. Financial Data (Odoo)
- Revenue (invoices created/paid)
- New customers/partners
- Outstanding invoices
- Payment status
- Source: Odoo via `actions/odoo_rpc.py`

### 3. Social Media Activity
- LinkedIn posts published
- Facebook posts published
- Engagement metrics (if available)
- Source: `Logs/linkedin_poster.log`, `Logs/facebook_poster.log`, `Done/`

### 4. WhatsApp Communications
- Messages received and processed
- Response rate
- Source: `Logs/whatsapp_watcher.log`, `Done/whatsapp_*.md`

### 5. Tasks & Projects
- Tasks completed
- Tasks pending
- Projects in progress
- Source: `Done/`, `Needs_Action/`, `Pending_Approval/`, `Plans/`

### 6. System Performance
- Uptime and reliability
- Errors encountered
- Processing speed
- Source: All log files

---

## Report Structure

### Executive Summary
- **Period:** Week of [Start Date] - [End Date]
- **Overall Status:** Green/Yellow/Red
- **Key Highlights:** Top 3-5 achievements
- **Critical Issues:** Top 1-3 concerns
- **Action Required:** Immediate decisions needed

### Financial Overview
- **Revenue This Week:** $X,XXX
- **New Invoices:** X invoices totaling $X,XXX
- **Payments Received:** $X,XXX
- **Outstanding:** $X,XXX (X invoices)
- **New Customers:** X partners added
- **Week-over-Week:** +/- X%

### Sales & Marketing Activity
- **LinkedIn Posts:** X published, Y engagement
- **Facebook Posts:** X published, Y engagement
- **Email Campaigns:** X sent, Y% open rate
- **Lead Generation:** X new leads
- **Conversion Rate:** X%

### Communication Metrics
- **Emails Processed:** X total
  - Automated responses: X
  - Flagged for review: X
  - Average response time: X hours
- **WhatsApp Messages:** X processed
- **Response Rate:** X%

### Tasks & Projects
- **Completed This Week:** X tasks
  - High priority: X
  - Medium priority: X
  - Low priority: X
- **In Progress:** X tasks
- **Pending Approval:** X items
- **Overdue:** X tasks (if any)

### System Performance
- **Uptime:** X%
- **Messages Processed:** X total
- **Errors:** X (X% error rate)
- **Processing Speed:** Avg X seconds
- **Automation Rate:** X% automated

### Risks & Issues
- **Critical:** Issues requiring immediate attention
- **High:** Issues to address this week
- **Medium:** Issues to monitor
- **Resolved:** Issues fixed this week

### Recommendations
- **Strategic:** Long-term improvements
- **Tactical:** Short-term actions
- **Operational:** Process optimizations
- **Technical:** System enhancements

### Week Ahead
- **Upcoming Deadlines:** Key dates
- **Scheduled Activities:** Planned tasks
- **Resource Needs:** Requirements
- **Focus Areas:** Priorities

---

## Output Format

### Markdown Report
```markdown
# Weekly CEO Briefing
**Period:** January 1-7, 2026  
**Generated:** January 7, 2026 8:00 PM  
**Status:** 🟢 Green

---

## Executive Summary

### Key Highlights
✅ Revenue up 15% week-over-week  
✅ 5 new customers onboarded  
✅ 100% email response rate maintained  

### Critical Issues
⚠️ 2 invoices overdue by 30+ days  

### Action Required
🎯 Approve 3 pending proposals in Pending_Approval/

---

## Financial Overview

| Metric | This Week | Last Week | Change |
|--------|-----------|-----------|--------|
| Revenue | $12,500 | $10,870 | +15% |
| New Invoices | 8 | 6 | +33% |
| Payments | $9,200 | $8,500 | +8% |
| Outstanding | $15,300 | $12,600 | +21% |

### New Customers
- TechCorp Solutions Ltd ($3,750)
- ABC Industries ($2,500)
- XYZ Consulting ($1,800)

---

[Additional sections...]
```

### HTML Version (Optional)
- Professional styling
- Charts and graphs
- Responsive design
- Print-friendly

### PDF Version (Optional)
- Executive presentation format
- Company branding
- Shareable document

---

## Execution

### Automated (Scheduled)
```bash
# Runs every Sunday at 8 PM via scheduler
# Configured in schedulers/weekly_runner.py
```

### Manual (On-Demand)
```bash
cd Gold-Tier
python actions/weekly_briefing_generator.py --run-now
```

### With Options
```bash
# Generate for specific week
python actions/weekly_briefing_generator.py --week 2026-01-01

# Generate and email
python actions/weekly_briefing_generator.py --run-now --email ceo@company.com

# Generate PDF
python actions/weekly_briefing_generator.py --run-now --pdf

# Custom date range
python actions/weekly_briefing_generator.py --start 2026-01-01 --end 2026-01-07
```

---

## Configuration

### Settings (in script or config file)
```python
BRIEFING_CONFIG = {
    'schedule': 'Sunday 20:00',  # 8 PM every Sunday
    'output_dir': 'Briefings/',
    'format': ['markdown', 'html'],  # Output formats
    'email_to': 'ceo@company.com',  # Auto-email recipient
    'include_charts': True,
    'include_recommendations': True,
    'status_thresholds': {
        'green': {'revenue_growth': 0, 'error_rate': 0.05},
        'yellow': {'revenue_growth': -10, 'error_rate': 0.10},
        'red': {'revenue_growth': -20, 'error_rate': 0.15}
    }
}
```

---

## Status Indicators

### Overall Status
- 🟢 **Green:** All metrics positive, no critical issues
- 🟡 **Yellow:** Some concerns, monitoring required
- 🔴 **Red:** Critical issues, immediate action needed

### Calculation
```python
status = 'green'
if revenue_growth < -10% or error_rate > 10%:
    status = 'yellow'
if revenue_growth < -20% or error_rate > 15% or critical_issues > 0:
    status = 'red'
```

---

## Data Collection Logic

### Email Metrics
```python
# Count processed emails
emails_done = len(glob('Done/email_*.md'))

# Calculate response time
avg_response_time = calculate_avg_from_logs('Logs/gmail_watcher.log')

# Count pending
emails_pending = len(glob('Needs_Action/email_*.md'))
```

### Financial Metrics
```python
# Query Odoo for invoices
client = OdooRPCClient()
client.authenticate()

# This week's invoices
invoices = client.search_read('account.move', 
    domain=[('invoice_date', '>=', week_start)],
    fields=['amount_total', 'payment_state'])

# Calculate totals
revenue = sum(inv['amount_total'] for inv in invoices if inv['payment_state'] == 'paid')
outstanding = sum(inv['amount_total'] for inv in invoices if inv['payment_state'] != 'paid')
```

### Social Media Metrics
```python
# Count posts from Done/
linkedin_posts = len(glob('Done/linkedin_post_*.md'))
facebook_posts = len(glob('Done/facebook_post_*.md'))

# Parse logs for engagement (if available)
engagement = parse_social_logs()
```

---

## Recommendations Engine

### Automatic Recommendations
Based on data analysis, generate actionable recommendations:

**If revenue down:**
- "Consider increasing outreach efforts"
- "Review pricing strategy"
- "Follow up on pending proposals"

**If response time high:**
- "Review email processing rules"
- "Consider additional automation"
- "Check for bottlenecks"

**If error rate high:**
- "Review recent errors in logs"
- "Update selectors if UI changed"
- "Consider system maintenance"

**If outstanding invoices high:**
- "Send payment reminders"
- "Review payment terms"
- "Follow up with overdue clients"

---

## Integration

### With Scheduler
```python
# In schedulers/weekly_runner.py
import schedule

def run_weekly_briefing():
    subprocess.run(['python', 'actions/weekly_briefing_generator.py', '--run-now'])

schedule.every().sunday.at("20:00").do(run_weekly_briefing)
```

### With Orchestrator
```python
# Detect briefing request
if 'generate_weekly_briefing' in action_type:
    subprocess.run(['python', 'actions/weekly_briefing_generator.py', '--run-now'])
```

### With Email Sender
```python
# Auto-email after generation
if config['email_to']:
    send_email(
        to=config['email_to'],
        subject=f"Weekly CEO Briefing - {week_start}",
        body=briefing_content,
        attachments=[briefing_pdf]
    )
```

---

## Example Output

### Sample Executive Summary
```markdown
# Weekly CEO Briefing
**Period:** January 1-7, 2026  
**Generated:** January 7, 2026 8:00 PM  
**Status:** 🟢 Green

---

## Executive Summary

This week showed strong performance across all metrics. Revenue increased 15% week-over-week, driven by 5 new customer acquisitions. Email automation maintained 100% response rate with average response time of 2.3 hours.

### Key Highlights
✅ **Revenue Growth:** $12,500 (+15% WoW)  
✅ **New Customers:** 5 partners onboarded  
✅ **Email Performance:** 100% response rate, 2.3hr avg  
✅ **Social Media:** 4 posts published, strong engagement  
✅ **System Uptime:** 99.8%

### Critical Issues
⚠️ **Overdue Invoices:** 2 invoices overdue by 30+ days ($3,200 total)  
⚠️ **Pending Approvals:** 3 proposals awaiting decision

### Action Required
🎯 **Immediate:** Approve 3 pending proposals in Pending_Approval/  
🎯 **This Week:** Follow up on 2 overdue invoices  
🎯 **Strategic:** Review Q1 goals and adjust if needed

---

## Financial Overview

### Revenue Summary
| Metric | This Week | Last Week | Change |
|--------|-----------|-----------|--------|
| **Total Revenue** | $12,500 | $10,870 | +15% ⬆️ |
| **New Invoices** | 8 ($15,200) | 6 ($12,400) | +33% ⬆️ |
| **Payments Received** | $9,200 | $8,500 | +8% ⬆️ |
| **Outstanding** | $15,300 | $12,600 | +21% ⬆️ |

### New Customers (5)
1. **TechCorp Solutions Ltd** - $3,750 (Consulting)
2. **ABC Industries** - $2,500 (Development)
3. **XYZ Consulting** - $1,800 (Integration)
4. **NewClient Co** - $1,200 (Support)
5. **StartupX** - $950 (Setup)

### Outstanding Invoices
- **Total:** $15,300 across 12 invoices
- **Current (0-30 days):** $12,100 (10 invoices)
- **Overdue (30+ days):** $3,200 (2 invoices) ⚠️

**Action:** Follow up with overdue clients this week

---

[Additional sections...]

## Recommendations

### Strategic
1. **Q1 Revenue Target:** On track for 120% of goal - consider raising Q2 targets
2. **Customer Acquisition:** Strong momentum - maintain current marketing spend
3. **Product Development:** Consider allocating resources to top customer requests

### Tactical
1. **Collections:** Implement automated payment reminders for 15+ day invoices
2. **Social Media:** Increase posting frequency to 2x/week for better engagement
3. **Email Automation:** Current 100% response rate is excellent - document process

### Operational
1. **Approval Workflow:** 3 items pending - review and approve by Tuesday
2. **System Maintenance:** Schedule quarterly review of all integrations
3. **Documentation:** Update runbooks with recent process improvements

---

## Week Ahead (January 8-14)

### Key Dates
- **Monday:** Q1 planning meeting
- **Wednesday:** Client presentation (TechCorp)
- **Friday:** Team review session

### Focus Areas
1. Close 2 overdue invoices
2. Approve pending proposals
3. Maintain email response rate
4. Publish 2 social media posts

### Resource Needs
- None identified

---

**Report Generated:** 2026-01-07 20:00:00  
**Next Report:** 2026-01-14 20:00:00  
**Questions?** Review detailed logs in Logs/ or Odoo dashboard
```

---

## Customization

### Add Custom Sections
```python
def generate_custom_section():
    return """
## Custom Metrics
- Metric 1: Value
- Metric 2: Value
"""
```

### Modify Thresholds
```python
STATUS_THRESHOLDS = {
    'revenue_growth_green': 5,  # 5% growth = green
    'revenue_growth_yellow': -5,  # -5% = yellow
    'revenue_growth_red': -15,  # -15% = red
}
```

### Change Schedule
```python
# Daily briefing
schedule.every().day.at("17:00").do(run_briefing)

# Monthly briefing
schedule.every().month.at("01 09:00").do(run_briefing)
```

---

## Testing

### Generate Test Report
```bash
cd Gold-Tier
python actions/weekly_briefing_generator.py --run-now --test
```

### Verify Data Sources
```bash
# Check Odoo connection
python actions/odoo_rpc.py --action test

# Check log files
ls -la Logs/

# Check completed tasks
ls -la Done/
```

### Review Output
```bash
# View generated report
cat Briefings/Weekly_Report_2026-01-07.md

# Open in browser (if HTML)
open Briefings/Weekly_Report_2026-01-07.html
```

---

## Troubleshooting

### Issue: No Data
**Cause:** Insufficient activity this week  
**Fix:** Generate report for longer period or add sample data

### Issue: Odoo Connection Failed
**Cause:** Odoo not running or credentials wrong  
**Fix:** Start Odoo containers, verify credentials

### Issue: Missing Metrics
**Cause:** Log files not found or empty  
**Fix:** Ensure watchers have run, check log locations

### Issue: Report Not Generated
**Cause:** Script error or permission issue  
**Fix:** Check logs, verify Briefings/ folder exists

---

## Success Indicators

✅ Report generated automatically every Sunday  
✅ All data sources integrated  
✅ Metrics accurate and up-to-date  
✅ Status indicator reflects reality  
✅ Recommendations actionable  
✅ Format professional and readable  
✅ CEO finds report valuable  
✅ Decisions made based on insights

---

**Skill Status:** ✅ Active  
**Last Updated:** 2026-03-30  
**Owner:** AI Employee System (Gold Tier)  
**Dependencies:** Odoo, email logs, social media logs, task files
