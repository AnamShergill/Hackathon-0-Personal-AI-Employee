#!/usr/bin/env python3
"""
Debug script to see what emails are in your Gmail and test different queries
"""
import os
import pickle
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from datetime import datetime, timedelta, timezone

SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

def authenticate():
    """Authenticate with Gmail"""
    creds = None
    if os.path.exists('token.json'):
        with open('token.json', 'rb') as token:
            creds = pickle.load(token)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'wb') as token:
            pickle.dump(creds, token)
    
    return build('gmail', 'v1', credentials=creds)

def get_email_details(service, msg_id):
    """Get email details"""
    message = service.users().messages().get(userId='me', id=msg_id).execute()
    
    headers = message.get('payload', {}).get('headers', [])
    subject = next((h['value'] for h in headers if h['name'].lower() == 'subject'), 'No Subject')
    sender = next((h['value'] for h in headers if h['name'].lower() == 'from'), 'Unknown')
    date = next((h['value'] for h in headers if h['name'].lower() == 'date'), 'Unknown')
    labels = message.get('labelIds', [])
    
    return {
        'id': msg_id,
        'subject': subject,
        'sender': sender,
        'date': date,
        'labels': labels
    }

def main():
    print("=" * 80)
    print("GMAIL WATCHER DEBUG TOOL")
    print("=" * 80)
    print()
    
    service = authenticate()
    print("✅ Authentication successful\n")
    
    # Calculate dates
    now = datetime.now(timezone.utc)
    one_day_ago = (now - timedelta(days=1)).strftime('%Y/%m/%d')
    three_days_ago = (now - timedelta(days=3)).strftime('%Y/%m/%d')
    
    print(f"Current time (UTC): {now.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Looking for emails after: {one_day_ago}")
    print()
    
    # Test queries
    queries = [
        ("1. Current watcher query", f'is:unread (is:starred OR is:important) -in:sent after:{one_day_ago}'),
        ("2. Just unread (last 24h)", f'is:unread -in:sent after:{one_day_ago}'),
        ("3. Just starred (last 24h)", f'is:starred after:{one_day_ago}'),
        ("4. Unread + starred (last 24h)", f'is:unread is:starred after:{one_day_ago}'),
        ("5. All unread (last 3 days)", f'is:unread -in:sent after:{three_days_ago}'),
        ("6. All starred (last 3 days)", f'is:starred after:{three_days_ago}'),
        ("7. Unread in inbox only", f'is:unread in:inbox after:{one_day_ago}'),
        ("8. Everything unread (no time limit)", f'is:unread -in:sent'),
    ]
    
    for description, query in queries:
        print("-" * 80)
        print(f"\n{description}")
        print(f"Query: {query}")
        print()
        
        try:
            results = service.users().messages().list(userId='me', q=query, maxResults=5).execute()
            messages = results.get('messages', [])
            
            if messages:
                print(f"✅ Found {len(messages)} email(s)\n")
                
                for i, msg in enumerate(messages, 1):
                    details = get_email_details(service, msg['id'])
                    print(f"   Email {i}:")
                    print(f"   Subject: {details['subject'][:70]}")
                    print(f"   From: {details['sender'][:70]}")
                    print(f"   Date: {details['date']}")
                    print(f"   Labels: {', '.join(details['labels'])}")
                    print(f"   Gmail ID: {details['id'][:16]}...")
                    
                    # Check specific conditions
                    is_unread = 'UNREAD' in details['labels']
                    is_starred = 'STARRED' in details['labels']
                    is_important = 'IMPORTANT' in details['labels']
                    is_inbox = 'INBOX' in details['labels']
                    is_sent = 'SENT' in details['labels']
                    
                    print(f"   Status: ", end="")
                    if is_unread:
                        print("UNREAD ", end="")
                    if is_starred:
                        print("⭐STARRED ", end="")
                    if is_important:
                        print("➤IMPORTANT ", end="")
                    if is_inbox:
                        print("📥INBOX ", end="")
                    if is_sent:
                        print("📤SENT ", end="")
                    print()
                    print()
            else:
                print("❌ No emails found")
        
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n" + "=" * 80)
    print("DIAGNOSIS & RECOMMENDATIONS")
    print("=" * 80)
    print()
    
    # Get some basic stats
    try:
        unread_count = service.users().messages().list(userId='me', q='is:unread', maxResults=1).execute()
        starred_count = service.users().messages().list(userId='me', q='is:starred', maxResults=1).execute()
        
        total_unread = unread_count.get('resultSizeEstimate', 0)
        total_starred = starred_count.get('resultSizeEstimate', 0)
        
        print(f"📊 Your Gmail Stats:")
        print(f"   Total unread emails: {total_unread}")
        print(f"   Total starred emails: {total_starred}")
        print()
    except:
        pass
    
    print("💡 Troubleshooting Tips:")
    print()
    print("If NO emails found in ANY query:")
    print("  → Your Gmail might be empty or all emails are read")
    print("  → Send yourself a test email and DON'T open it")
    print("  → Make sure to star it (click the star icon)")
    print()
    print("If emails found in 'Everything unread' but not in '24h' queries:")
    print("  → Your emails are older than 24 hours")
    print("  → Send a NEW test email")
    print("  → Or increase the time window in gmail_watcher.py")
    print()
    print("If emails found in 'Just unread' but not 'Current watcher query':")
    print("  → Your emails are not starred AND not marked important by Gmail")
    print("  → Star your test email in Gmail (click the star icon)")
    print("  → Make sure email is still UNREAD (bold in Gmail)")
    print()
    print("If emails found in 'Just starred' but not 'Unread + starred':")
    print("  → You opened the email, so it's no longer unread")
    print("  → In Gmail: Select email → More → Mark as unread")
    print()
    print("To test the watcher:")
    print("  1. Send email to yourself from another account")
    print("  2. In Gmail: DON'T open it, just click the star")
    print("  3. Verify email is bold (unread) with yellow star")
    print("  4. Run: python3 Watchers/gmail_watcher.py")
    print("  5. Wait up to 90 seconds for next poll")
    print()

if __name__ == "__main__":
    main()
