"""
Test script to debug Gmail query and see what emails are found
"""
import os
import pickle
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from datetime import datetime, timedelta

SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

def test_gmail_queries():
    """Test different Gmail queries to find your email"""
    
    # Authenticate
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
    
    service = build('gmail', 'v1', credentials=creds)
    
    # Calculate time
    one_day_ago = (datetime.utcnow() - timedelta(days=1)).strftime('%Y/%m/%d')
    
    # Test different queries
    queries = [
        ('Current query (unread + important)', f'is:unread is:important -in:sent after:{one_day_ago}'),
        ('Unread + starred', f'is:unread is:starred -in:sent after:{one_day_ago}'),
        ('Just unread', f'is:unread -in:sent after:{one_day_ago}'),
        ('Just starred', f'is:starred -in:sent after:{one_day_ago}'),
        ('Unread in inbox', f'is:unread in:inbox after:{one_day_ago}'),
        ('Unread + (starred OR important)', f'is:unread (is:starred OR is:important) -in:sent after:{one_day_ago}'),
    ]
    
    print("=" * 80)
    print("GMAIL QUERY TESTING")
    print("=" * 80)
    print(f"Searching for emails after: {one_day_ago}")
    print()
    
    for description, query in queries:
        print(f"\n📧 Testing: {description}")
        print(f"   Query: {query}")
        print("-" * 80)
        
        try:
            results = service.users().messages().list(userId='me', q=query).execute()
            messages = results.get('messages', [])
            
            if messages:
                print(f"   ✅ Found {len(messages)} email(s)")
                
                # Get details of first 3 emails
                for i, msg in enumerate(messages[:3], 1):
                    message = service.users().messages().get(userId='me', id=msg['id']).execute()
                    
                    # Extract subject and sender
                    headers = message.get('payload', {}).get('headers', [])
                    subject = next((h['value'] for h in headers if h['name'].lower() == 'subject'), 'No Subject')
                    sender = next((h['value'] for h in headers if h['name'].lower() == 'from'), 'Unknown')
                    labels = message.get('labelIds', [])
                    
                    print(f"   {i}. Subject: {subject[:60]}")
                    print(f"      From: {sender[:60]}")
                    print(f"      Labels: {', '.join(labels)}")
                    print()
            else:
                print(f"   ❌ No emails found")
        
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 80)
    print("RECOMMENDATIONS:")
    print("=" * 80)
    print()
    print("If your email shows up in 'Unread + starred' but not 'Current query':")
    print("→ Gmail's 'important' marker is different from 'starred'")
    print("→ Update gmail_watcher.py query to use 'is:starred' instead")
    print()
    print("If your email shows up in 'Just unread':")
    print("→ The email might not be starred or marked important")
    print("→ Try starring it in Gmail and wait for next poll")
    print()
    print("If your email doesn't show up anywhere:")
    print("→ Check if email is older than 24 hours")
    print("→ Check if email is in Sent folder")
    print("→ Verify email is actually unread in Gmail")
    print()

if __name__ == "__main__":
    test_gmail_queries()
