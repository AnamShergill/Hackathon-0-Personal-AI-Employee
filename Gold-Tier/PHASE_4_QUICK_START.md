# Phase 4: Weekly CEO Briefing - Quick Start Guide

## What It Does

Automatically generates comprehensive weekly business reports every Sunday at 8 PM, pulling data from:
- Email activity (Gmail)
- Financial data (Odoo)
- Social media (LinkedIn, Facebook)
- Tasks and projects
- System performance

## Quick Commands

### Generate Briefing Now
```bash
cd Gold-Tier
python actions/weekly_briefing_generator.py --run-now
```

### View Latest Report
```bash
cat Briefings/Weekly_Report_*.md | tail -100
```

### Start Scheduler (for automatic generation)
```bash
cd Gold-Tier
python schedulers/daily_runner.py
```

## What You Get

A professional Markdown report with:
- 🟢/🟡/🔴 Status indicator
- Executive summary with highlights
- Financial overview (revenue, invoices, customers)
- Communication metrics (emails, social media)
- Task completion breakdown
- System performance stats
- Actionable recommendations
- Week ahead planning

## Files

- **Generator**: `actions/weekly_briefing_generator.py`
- **Skill**: `Skills/14_WEEKLY_CEO_BRIEFING.md`
- **Scheduler**: `schedulers/daily_runner.py`
- **Output**: `Briefings/Weekly_Report_YYYY-MM-DD.md`
- **Docs**: `WEEKLY_CEO_BRIEFING.md`

## Schedule

- **Sunday 8 PM**: Weekly CEO Briefing generated
- **Monday 8 AM**: Weekly cleanup (logs)

## Test It

```bash
cd Gold-Tier

# 1. Test Odoo connection
python actions/odoo_rpc.py --action test

# 2. Generate test briefing
python actions/weekly_briefing_generator.py --run-now

# 3. View output
cat Briefings/Weekly_Report_2026-03-30.md
```

## Status: ✅ COMPLETE

All components implemented and tested. Ready for production use.

For detailed documentation, see `WEEKLY_CEO_BRIEFING.md`.
