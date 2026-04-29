# Weekly CEO Briefing System - Complete Guide

## Overview

The Weekly CEO Briefing System automatically generates comprehensive business summary reports every Sunday at 8 PM. It pulls data from all integrated systems (email, Odoo, social media, tasks) and produces professional, actionable briefings suitable for executive review.

## Status: ✅ FULLY OPERATIONAL

**Phase 4 Complete** - All components implemented and tested.

---

## Architecture

### Components

1. **Skill Documentation**: `Skills/14_WEEKLY_CEO_BRIEFING.md`
   - Defines purpose, data sources, report structure
   - Comprehensive specification (1000+ lines)

2. **Generator Script**: `actions/weekly_briefing_generator.py`
   - Collects data from all sources
   - Calculates metrics and status indicators
   - Generates professional Markdown reports
   - Provides CLI interface

3. **Scheduler Integration**: `schedulers/daily_runner.py`
   - Runs every Sunday at 8 PM
   - Calls weekly_briefing_generator.py
   - Logs execution results

4. **Output Directory**: `Briefings/`
   - Stores all generated reports
   - Filename format: `Weekly_Report_YYYY-MM-DD.md`

---

## Data Sources

### 1. Email Activity (Gmail)
- Total emails processed (from Done/ folder)
- Response rate and time
- Pending items (from Needs_Action/)
- Flagged items (from Pending_Approval/)

### 2. Financial Data (Odoo)
- Revenue (invoices created/paid)
- New customers/partners
- Outstanding invoices
- Overdue invoices
- Payment status

### 3. Social Media Activity
- LinkedIn posts published (from Done/)
- Facebook posts published (from Done/)
- Post counts and activity

### 4. Tasks & Projects
- Tasks completed (from Done/)
- Tasks in progress (from Plans/)
- Tasks pending approval (from Pending_Approval/)

### 5. System Performance
- Uptime and reliability
- Errors encountered (from Logs/)
- Processing speed
- Automation rate

---

## Report Structure

Each weekly briefing includes:

1. **Executive Summary**
   - Overall status (🟢 Green / 🟡 Yellow / 🔴 Red)
   - Key highlights (top achievements)
   - Critical issues (concerns requiring attention)
   - Action required (immediate decisions)

2. **Financial Overview**
   - Revenue summary table
   - New customers list
   - Outstanding invoices
   - Overdue invoices (if any)

3. **Communication Metrics**
   - Email activity and response times
   - Social media posts and reach

4. **Tasks & Projects**
   - Completed tasks breakdown
   - Active tasks status

5. **System Performance**
   - Uptime percentage
   - Error rates
   - Automation metrics

6. **Recommendations**
   - Actionable suggestions based on data
   - Strategic, tactical, and operational items

7. **Week Ahead**
   - Focus areas for next week
   - Upcoming priorities

---

## Usage

### Automatic (Scheduled)

The briefing runs automatically every Sunday at 8 PM via the scheduler:

```bash
# Start the scheduler (runs in background)
cd Gold-Tier
python schedulers/daily_runner.py
```

The scheduler will:
- Run every Sunday at 20:00 (8 PM)
- Generate briefing for the past week (Monday-Sunday)
- Save to Briefings/ folder
- Log execution results

### Manual (On-Demand)

Generate a briefing anytime:

```bash
cd Gold-Tier
python actions/weekly_briefing_generator.py --run-now
```

### Advanced Options

```bash
# Generate for specific week
python actions/weekly_briefing_generator.py --week 2026-03-24

# Future: Email delivery (not yet implemented)
python actions/weekly_briefing_generator.py --run-now --email ceo@company.com

# Future: PDF generation (not yet implemented)
python actions/weekly_briefing_generator.py --run-now --pdf
```

---

## Status Indicators

### Overall Status Calculation

The system automatically calculates overall status based on key metrics:

- **🟢 Green**: All metrics positive, no critical issues
  - Revenue >= 0
  - Error rate < 5%
  - No overdue invoices

- **🟡 Yellow**: Some concerns, monitoring required
  - Revenue decline 0-20%
  - Error rate 5-15%
  - 1-5 overdue invoices

- **🔴 Red**: Critical issues, immediate action needed
  - Revenue decline > 20%
  - Error rate > 15%
  - More than 5 overdue invoices

---

## Customization

### Modify Report Content

Edit `actions/weekly_briefing_generator.py` to:
- Add new data sources
- Change metric calculations
- Adjust report sections
- Modify status thresholds

### Change Schedule

Edit `schedulers/daily_runner.py`:

```python
# Current: Sunday 8 PM
schedule.every().sunday.at("20:00").do(sunday_evening_routine)

# Change to Friday 5 PM
schedule.every().friday.at("17:00").do(sunday_evening_routine)

# Or daily briefing
schedule.every().day.at("17:00").do(sunday_evening_routine)
```

### Add Custom Metrics

Example: Add customer satisfaction score

```python
def collect_custom_metrics(self) -> Dict[str, Any]:
    """Collect custom business metrics"""
    metrics = {
        'customer_satisfaction': 0,
        'nps_score': 0
    }
    
    # Your data collection logic here
    
    return metrics
```

---

## Testing

### Test Report Generation

```bash
cd Gold-Tier
python actions/weekly_briefing_generator.py --run-now
```

Expected output:
- ✅ Report generated successfully
- 📄 Report saved to: Briefings/Weekly_Report_YYYY-MM-DD.md
- Report content printed to console

### Verify Data Sources

1. **Odoo Connection**:
   ```bash
   python actions/odoo_rpc.py --action test
   ```

2. **Check Folders**:
   ```bash
   ls -la Done/
   ls -la Logs/
   ls -la Pending_Approval/
   ```

3. **Review Generated Report**:
   ```bash
   cat Briefings/Weekly_Report_2026-03-30.md
   ```

---

## Troubleshooting

### Issue: No Data in Report

**Cause**: Insufficient activity this week or folders empty

**Fix**:
- Ensure watchers have been running
- Check that Done/, Logs/, Plans/ folders exist
- Generate test data if needed

### Issue: Odoo Connection Failed

**Cause**: Odoo not running or credentials incorrect

**Fix**:
```bash
cd odoo-docker
docker compose ps  # Check if running
docker compose up -d  # Start if needed
```

Verify credentials in `odoo-docker/.env`:
- ODOO_URL=http://localhost:8069
- ODOO_DB_NAME=ai_employee_db
- ODOO_USERNAME=pinkyshergill1986@gmail.com
- ODOO_PASSWORD=anamthecoder

### Issue: Report Not Generated

**Cause**: Script error or permission issue

**Fix**:
- Check logs: `cat Logs/scheduler.log`
- Verify Briefings/ folder exists
- Run manually to see error: `python actions/weekly_briefing_generator.py --run-now`

### Issue: Scheduler Not Running

**Cause**: daily_runner.py not started

**Fix**:
```bash
cd Gold-Tier
python schedulers/daily_runner.py
```

Keep terminal open or run in background/screen/tmux.

---

## Example Output

See `Briefings/Weekly_Report_2026-03-30.md` for a complete example.

Key sections include:
- Executive summary with status indicator
- Financial metrics table
- New customers list
- Communication and social media stats
- Task completion breakdown
- System performance metrics
- Actionable recommendations
- Week ahead focus areas

---

## Future Enhancements

### Planned Features

1. **Email Delivery**
   - Automatic email to CEO/stakeholders
   - HTML formatted version
   - Attachment support

2. **PDF Generation**
   - Professional PDF output
   - Company branding
   - Charts and graphs

3. **Advanced Analytics**
   - Week-over-week comparisons
   - Trend analysis
   - Predictive insights

4. **Interactive Dashboard**
   - Web-based visualization
   - Real-time metrics
   - Drill-down capabilities

5. **Custom Alerts**
   - Threshold-based notifications
   - Slack/Teams integration
   - SMS for critical issues

### Implementation Notes

To add email delivery:
```python
# In weekly_briefing_generator.py
def send_email_report(self, report: str, recipient: str):
    """Send report via email"""
    from actions.email_sender import send_email
    
    send_email(
        to=recipient,
        subject=f"Weekly CEO Briefing - {self.week_start.strftime('%B %d, %Y')}",
        body=report
    )
```

To add PDF generation:
```python
# Requires: pip install markdown2 weasyprint
def generate_pdf(self, report: str) -> Path:
    """Convert Markdown report to PDF"""
    import markdown2
    from weasyprint import HTML
    
    html = markdown2.markdown(report)
    pdf_path = self.briefings_dir / f"Weekly_Report_{self.week_start.strftime('%Y-%m-%d')}.pdf"
    HTML(string=html).write_pdf(pdf_path)
    
    return pdf_path
```

---

## Integration with Other Systems

### With Email Sender

```python
# Auto-email after generation
if args.email:
    generator = WeeklyBriefingGenerator()
    filepath = generator.generate_and_save()
    
    with open(filepath, 'r') as f:
        report = f.read()
    
    send_email(
        to=args.email,
        subject=f"Weekly CEO Briefing - {generator.week_start.strftime('%B %d, %Y')}",
        body=report
    )
```

### With Slack/Teams

```python
# Post summary to Slack
def post_to_slack(report: str):
    import requests
    
    webhook_url = os.getenv('SLACK_WEBHOOK_URL')
    
    # Extract executive summary
    summary = extract_executive_summary(report)
    
    requests.post(webhook_url, json={
        'text': f"📊 Weekly CEO Briefing Generated\n\n{summary}"
    })
```

---

## Success Metrics

✅ Report generated automatically every Sunday  
✅ All data sources integrated (Email, Odoo, Social, Tasks, System)  
✅ Metrics accurate and up-to-date  
✅ Status indicator reflects reality  
✅ Recommendations actionable  
✅ Format professional and readable  
✅ CEO finds report valuable  
✅ Decisions made based on insights  

---

## Support

For issues or questions:
1. Check this documentation
2. Review logs in `Logs/scheduler.log`
3. Test components individually
4. Review skill documentation in `Skills/14_WEEKLY_CEO_BRIEFING.md`

---

**System Status**: ✅ Operational  
**Last Updated**: 2026-03-30  
**Version**: 1.0 (Phase 4 Complete)  
**Owner**: AI Employee System (Gold Tier)  
**Dependencies**: Odoo, email logs, social media logs, task files
