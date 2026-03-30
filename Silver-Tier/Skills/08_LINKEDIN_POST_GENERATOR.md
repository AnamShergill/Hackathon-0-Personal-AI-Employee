# Skill: LinkedIn Post Generator

## Overview
This skill generates professional, sales-oriented LinkedIn posts to promote business, share insights, and generate leads. Posts are written to Pending_Approval/ for HITL review before publishing.

## Version
1.0 - Silver Tier

## Prerequisites
- Company_Handbook.md for tone guidelines
- Dashboard.md for business context
- Python 3.13+

## Input
- Optional: Topic/theme for the post
- Optional: Recent business achievements from Dashboard
- Optional: Target audience (B2B, developers, entrepreneurs)

## Output
- LinkedIn post draft in Pending_Approval/linkedin_post_*.md
- Includes post text (under 3000 chars, optimal 150-300)
- Optional image prompt for AI image generation
- Hashtags and call-to-action

## YAML Frontmatter
```yaml
---
skill_id: 08_LINKEDIN_POST_GENERATOR
execution_order: 5
triggers: ["scheduled_daily", "manual_request", "business_milestone"]
dependencies: ["Company_Handbook.md", "Dashboard.md"]
completion_criteria: ["post_drafted", "moved_to_pending_approval"]
---
```

## LinkedIn Post Best Practices
- **Length**: 150-300 characters for high engagement (can go up to 3000)
- **Hook**: First 2 lines are critical (show in feed preview)
- **Structure**: Hook → Value → Call-to-action
- **Hashtags**: 3-5 relevant hashtags
- **Emojis**: Use sparingly for emphasis
- **Tone**: Professional but personable, not salesy

## Post Types
1. **Business Update**: Project completion, milestone, achievement
2. **Industry Insight**: Tips, trends, lessons learned
3. **Problem-Solution**: Address pain point, offer solution
4. **Behind-the-Scenes**: Team culture, process, tools
5. **Call-to-Action**: Service offering, consultation, demo

## Implementation

```python
import os
import random
from datetime import datetime
from pathlib import Path
import yaml

def generate_linkedin_post(topic=None, post_type=None):
    """
    Generate a professional LinkedIn post for business promotion
    """
    print("=" * 80)
    print("LINKEDIN POST GENERATOR")
    print("=" * 80)
    print()

    # Load business context from Dashboard
    business_context = load_business_context()

    # Determine post type
    if not post_type:
        post_type = random.choice([
            'business_update',
            'industry_insight',
            'problem_solution',
            'behind_the_scenes',
            'call_to_action'
        ])

    print(f"📝 Generating post type: {post_type}")
    print(f"📋 Topic: {topic if topic else 'Auto-generated'}")
    print()

    # Generate post content
    post_data = create_post_content(post_type, topic, business_context)

    # Save to Pending_Approval
    save_to_pending_approval(post_data)

    # Update dashboard
    update_dashboard_linkedin()

    print()
    print("✅ LinkedIn post generated and saved to Pending_Approval/")
    print("   Next: Human reviews and moves to Approved/ for posting")


def load_business_context():
    """
    Load business context from Dashboard and other sources
    """
    context = {
        'company_name': 'AI Employee Solutions',
        'industry': 'AI Automation & Development',
        'services': [
            'Personal AI Employee Development',
            'Business Process Automation',
            'AI Integration Consulting',
            'Custom AI Solutions'
        ],
        'achievements': [],
        'target_audience': 'Business owners, CTOs, entrepreneurs'
    }

    # Try to load from Dashboard
    try:
        dashboard_path = Path("Dashboard.md")
        if dashboard_path.exists():
            with open(dashboard_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # Extract recent achievements
                if 'Recent Activity' in content:
                    context['achievements'] = extract_achievements(content)
    except Exception as e:
        print(f"⚠️  Could not load dashboard context: {e}")

    return context


def extract_achievements(dashboard_content):
    """
    Extract recent achievements from dashboard
    """
    achievements = []

    # Look for completed tasks, processed messages, etc.
    if 'Completed Today' in dashboard_content:
        achievements.append("Processed multiple client communications efficiently")

    if 'Plans in Progress' in dashboard_content:
        achievements.append("Managing active projects with AI automation")

    if 'WhatsApp' in dashboard_content and 'Gmail' in dashboard_content:
        achievements.append("Multi-channel communication automation live")

    return achievements


def create_post_content(post_type, topic, context):
    """
    Create LinkedIn post content based on type and context
    """
    if post_type == 'business_update':
        return generate_business_update(context)
    elif post_type == 'industry_insight':
        return generate_industry_insight(topic, context)
    elif post_type == 'problem_solution':
        return generate_problem_solution(context)
    elif post_type == 'behind_the_scenes':
        return generate_behind_scenes(context)
    elif post_type == 'call_to_action':
        return generate_call_to_action(context)
    else:
        return generate_industry_insight(topic, context)


def generate_business_update(context):
    """
    Generate a business update/milestone post
    """
    achievements = context.get('achievements', [])

    if achievements:
        achievement = achievements[0]
        hook = f"🎉 Exciting milestone reached!"
    else:
        hook = f"🚀 Building the future of business automation"

    post_text = f"""{hook}

We've been working hard on our Personal AI Employee system, and the results are incredible:

✅ Multi-channel automation (Email + WhatsApp + more)
✅ Intelligent message routing and prioritization
✅ Human-in-the-loop for critical decisions
✅ 24/7 automated response handling

The goal? Help businesses scale their operations without scaling their headcount.

Imagine having an AI assistant that:
• Reads and categorizes all your messages
• Drafts professional responses
• Flags important items for your review
• Works around the clock

This isn't science fiction. It's happening now.

Interested in automating your business communications? Let's talk.

#AIAutomation #BusinessEfficiency #ProductivityTools #AIEmployee #Automation"""

    return {
        'type': 'business_update',
        'text': post_text,
        'hashtags': ['AIAutomation', 'BusinessEfficiency', 'ProductivityTools', 'AIEmployee', 'Automation'],
        'image_prompt': 'Professional business dashboard showing AI automation metrics, modern tech aesthetic, blue and white color scheme',
        'call_to_action': 'Comment "AUTOMATE" to learn how this can work for your business'
    }


def generate_industry_insight(topic, context):
    """
    Generate an industry insight/tips post
    """
    insights = [
        {
            'hook': '💡 The #1 productivity killer in 2026?',
            'body': """Context switching between communication channels.

The average business owner checks:
• Email: 15+ times/day
• WhatsApp: 30+ times/day
• Slack: 20+ times/day
• LinkedIn: 10+ times/day

That's 75+ interruptions. Every. Single. Day.

The solution? Intelligent automation.

Instead of YOU checking everything, let AI:
1. Monitor all channels 24/7
2. Categorize by priority
3. Draft responses
4. Flag what needs YOUR attention

You focus on decisions. AI handles the noise.

This is how modern businesses scale.

What's your biggest communication challenge?""",
            'hashtags': ['Productivity', 'BusinessAutomation', 'TimeManagement', 'AI', 'Efficiency']
        },
        {
            'hook': '🤔 Why do most AI projects fail?',
            'body': """They try to replace humans instead of augmenting them.

The winning formula:
AI handles: Repetitive tasks, data processing, 24/7 monitoring
Humans handle: Strategy, relationships, critical decisions

We call it "Human-in-the-Loop" automation.

Example: Our AI Employee reads 100 messages/day
• 70 are routine → AI drafts responses
• 20 need context → AI flags for review
• 10 are critical → AI escalates immediately

Result? You make 10 decisions instead of 100.
Same quality. 90% less time.

That's the future of work.

Are you augmenting or replacing?""",
            'hashtags': ['ArtificialIntelligence', 'FutureOfWork', 'BusinessStrategy', 'Automation', 'Leadership']
        },
        {
            'hook': '⚡ Speed vs Quality: You can have both',
            'body': """The old trade-off is dead.

With intelligent automation:
• Respond in minutes, not hours
• Maintain professional quality
• Never miss important messages
• Scale without hiring

How?
1. AI monitors all channels
2. Learns your communication style
3. Drafts responses instantly
4. You approve with one click

Fast + Quality + Scalable = Competitive advantage

What's holding you back from automating?""",
            'hashtags': ['BusinessGrowth', 'Automation', 'Efficiency', 'AI', 'Scaling']
        }
    ]

    insight = random.choice(insights)

    post_text = f"""{insight['hook']}

{insight['body']}

#{' #'.join(insight['hashtags'])}"""

    return {
        'type': 'industry_insight',
        'text': post_text,
        'hashtags': insight['hashtags'],
        'image_prompt': 'Modern business professional using AI technology, futuristic office, productivity concept',
        'call_to_action': 'Drop a 💡 if this resonates'
    }


def generate_problem_solution(context):
    """
    Generate a problem-solution post
    """
    post_text = """❌ Problem: Drowning in messages across 5+ platforms

You're not alone. The average professional spends 28% of their workday on email alone.

Add WhatsApp, Slack, LinkedIn, SMS... and you're spending 40%+ of your day just managing communications.

✅ Solution: Intelligent Message Orchestration

What if ONE system:
• Monitored ALL your channels
• Categorized by urgency
• Drafted professional responses
• Only interrupted you for critical items

That's what we built.

Real results from our system:
📊 90% reduction in communication overhead
⚡ 10x faster response times
🎯 100% of critical messages flagged
😌 Zero missed opportunities

The technology exists. The question is: when will you implement it?

Ready to reclaim your time? Let's talk.

#ProblemSolved #BusinessAutomation #ProductivityHack #AIEmployee #TimeManagement"""

    return {
        'type': 'problem_solution',
        'text': post_text,
        'hashtags': ['ProblemSolved', 'BusinessAutomation', 'ProductivityHack', 'AIEmployee', 'TimeManagement'],
        'image_prompt': 'Before and after comparison: cluttered inbox vs organized AI dashboard, clean modern design',
        'call_to_action': 'Comment "SOLUTION" for a free consultation'
    }


def generate_behind_scenes(context):
    """
    Generate a behind-the-scenes post
    """
    post_text = """🔧 Behind the scenes: Building an AI Employee

People ask: "How does it actually work?"

Here's the tech stack:
• Python for orchestration
• Playwright for browser automation
• Claude AI for intelligent processing
• YAML for configuration
• Git for version control

But the real magic? The architecture.

We use a "Human-in-the-Loop" pattern:
1. AI monitors channels 24/7
2. Processes routine items automatically
3. Flags sensitive items (money, contracts, personal info)
4. Human approves critical actions
5. AI executes approved tasks

It's not about replacing humans.
It's about amplifying human decision-making.

The result? A system that:
✅ Never sleeps
✅ Never misses a message
✅ Always maintains quality
✅ Scales infinitely

This is the future of business operations.

What would YOU automate first?

#TechStack #AIEngineering #Automation #BehindTheScenes #Innovation"""

    return {
        'type': 'behind_the_scenes',
        'text': post_text,
        'hashtags': ['TechStack', 'AIEngineering', 'Automation', 'BehindTheScenes', 'Innovation'],
        'image_prompt': 'Software architecture diagram, AI system flowchart, modern tech illustration',
        'call_to_action': 'Engineers: What would you build differently?'
    }


def generate_call_to_action(context):
    """
    Generate a direct call-to-action post
    """
    post_text = """🚀 Is your business ready for AI automation?

Take this 30-second test:

□ You spend 2+ hours/day on email
□ You have messages across 3+ platforms
□ You've missed important messages
□ You wish you could respond faster
□ You want to scale without hiring

If you checked 3+, you need automation.

What we offer:
✅ Custom AI Employee setup
✅ Multi-channel integration (Email, WhatsApp, Slack, etc.)
✅ Intelligent message routing
✅ Professional response drafting
✅ Human-in-the-loop for critical decisions

Investment: Fraction of a full-time employee
ROI: 10-20 hours/week saved
Timeline: Live in 2-4 weeks

Limited spots available this quarter.

Ready to automate? Comment "READY" or DM me.

Let's build your AI Employee together.

#AIAutomation #BusinessGrowth #Consulting #AIEmployee #Productivity"""

    return {
        'type': 'call_to_action',
        'text': post_text,
        'hashtags': ['AIAutomation', 'BusinessGrowth', 'Consulting', 'AIEmployee', 'Productivity'],
        'image_prompt': 'Professional business consultation, modern office, AI technology, call to action visual',
        'call_to_action': 'Comment "READY" to get started'
    }


def save_to_pending_approval(post_data):
    """
    Save LinkedIn post to Pending_Approval/ for HITL review
    """
    # Create filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"linkedin_post_{post_data['type']}_{timestamp}.md"
    filepath = Path("Pending_Approval") / filename

    # Ensure directory exists
    Path("Pending_Approval").mkdir(exist_ok=True)

    # Create post file
    content = f"""---
type: "linkedin_post"
post_type: "{post_data['type']}"
generated: "{datetime.now().isoformat()}"
status: "pending_approval"
requires_approval: true
approval_category: "linkedin_post"
character_count: {len(post_data['text'])}
---

# LinkedIn Post Draft - {post_data['type'].replace('_', ' ').title()}

## Post Text
{post_data['text']}

---

## Metadata
- **Type**: {post_data['type']}
- **Character Count**: {len(post_data['text'])}
- **Hashtags**: {', '.join(['#' + tag for tag in post_data['hashtags']])}
- **Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Image Prompt (Optional)
{post_data.get('image_prompt', 'No image prompt')}

## Call-to-Action
{post_data.get('call_to_action', 'Engage with the post')}

---

## Approval Instructions
1. Review the post text above
2. Edit if needed (keep under 3000 characters)
3. If approved: Move this file to Approved/ folder
4. If rejected: Move to Done/ with rejection note
5. Approved posts will be automatically posted to LinkedIn

## HITL Notes
- ⚠️ This post will be publicly visible on LinkedIn
- ✅ Review for tone, accuracy, and brand alignment
- ✅ Ensure no sensitive business information is shared
- ✅ Verify all claims and statistics

---
*Generated by LinkedIn Post Generator at {datetime.now().isoformat()}*
"""

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"📝 Post saved: {filepath}")
    print(f"   Character count: {len(post_data['text'])}")
    print(f"   Type: {post_data['type']}")


def update_dashboard_linkedin():
    """
    Update Dashboard with LinkedIn post generation activity
    """
    try:
        dashboard_path = Path("Dashboard.md")
        if not dashboard_path.exists():
            return

        with open(dashboard_path, 'r', encoding='utf-8') as f:
            content = f.read()

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        activity_entry = f"[{timestamp}] LinkedIn Post Generator: Created new post draft in Pending_Approval/\n"

        if "{{recent_activity}}" in content:
            updated_content = content.replace("{{recent_activity}}", activity_entry + "{{recent_activity}}")
        else:
            updated_content = content.replace(
                "```\n",
                f"```\n{activity_entry}",
                1
            )

        with open(dashboard_path, 'w', encoding='utf-8') as f:
            f.write(updated_content)

    except Exception as e:
        print(f"⚠️  Could not update dashboard: {e}")


if __name__ == "__main__":
    import sys

    # Parse arguments
    topic = sys.argv[1] if len(sys.argv) > 1 else None
    post_type = sys.argv[2] if len(sys.argv) > 2 else None

    generate_linkedin_post(topic, post_type)

    print()
    print("<COMPLETE>")
    print("LinkedIn Post Generator completed. Post saved to Pending_Approval/")
    print("Next: Human reviews and approves, then linkedin_poster.py will publish")
    print("</COMPLETE>")
```

## Usage Instructions
```bash
# Generate random post
python -c "exec(open('Skills/08_LINKEDIN_POST_GENERATOR.md').read().split('```python')[1].split('```')[0])"

# Generate specific type
python -c "exec(open('Skills/08_LINKEDIN_POST_GENERATOR.md').read().split('```python')[1].split('```')[0]); generate_linkedin_post(post_type='call_to_action')"
```

## Expected Outcomes
- Professional LinkedIn post generated
- Saved to Pending_Approval/ for human review
- Includes post text, hashtags, image prompt, CTA
- Character count optimized (150-300 for engagement)
- Dashboard updated with generation activity

## Post Types Generated
1. **Business Update**: Milestones, achievements, project completions
2. **Industry Insight**: Tips, trends, lessons learned
3. **Problem-Solution**: Address pain points, offer solutions
4. **Behind-the-Scenes**: Tech stack, process, team culture
5. **Call-to-Action**: Direct sales pitch, consultation offer

## HITL Workflow
1. Skill generates post → Pending_Approval/
2. Human reviews and edits if needed
3. Human moves to Approved/ when ready
4. approved_watcher.py detects file in Approved/
5. linkedin_poster.py publishes to LinkedIn
6. File moved to Done/ with confirmation

## Dependencies
- Python 3.13+
- PyYAML for YAML parsing
- Company_Handbook.md for tone guidelines
- Dashboard.md for business context

---
*LinkedIn Post Generator - Silver Tier Social Media Automation*
