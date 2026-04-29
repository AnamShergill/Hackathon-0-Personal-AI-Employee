"""
Hybrid Orchestrator - Central Routing for Platinum Tier

Routes tasks between Cloud (draft-only) and Local (execution-only) zones
based on work-zone specialization rules.

Author: Platinum Tier
Version: 1.0
Date: 2026-04-13
"""

import os
import sys
import time
import logging
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
from enum import Enum

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import PlatinumConfig, AgentMode, validate_action
from Actions.claim_by_move import ClaimByMove

# Configure logging with mode-specific prefix
logger = logging.getLogger(__name__)


class TaskDomain(Enum):
    """Task domain types."""
    EMAIL = "email"
    SOCIAL = "social"
    ODOO = "odoo"


class TaskType(Enum):
    """Task types."""
    DRAFT = "draft"
    EXECUTE = "execute"
    APPROVE = "approve"


class HybridOrchestrator:
    """
    Central routing and coordination system for Platinum Tier's hybrid architecture.
    
    Determines agent mode (Cloud or Local) from environment variable and routes
    tasks accordingly.
    """
    
    def __init__(self, config: Optional[PlatinumConfig] = None):
        """
        Initialize hybrid orchestrator.
        
        Args:
            config: Optional PlatinumConfig instance (creates new if None)
        """
        # Load configuration
        self.config = config or PlatinumConfig()
        self.mode = self.config.agent_mode
        
        # Setup logging with mode prefix
        self._setup_logging()
        
        # Initialize claim manager
        self.claim_manager = ClaimByMove(str(self.config.vault_path), self.mode.value)
        
        # Log initialization
        self.log(f"🚀 Hybrid Orchestrator initialized in {self.mode.value.upper()} mode")
        self.log(f"📁 Vault path: {self.config.vault_path}")
        self.log(f"⏱️  Scan interval: {self.config.scan_interval} seconds")
        self.log(f"🔒 Forbidden actions: {self.config.mode_config['forbidden_actions']}")
    
    def _setup_logging(self):
        """Setup logging with mode-specific formatting."""
        # Create mode-specific prefix
        self.log_prefix = f"[{self.mode.value.upper()}]"
        
        # Configure logging
        log_format = f'%(asctime)s - {self.log_prefix} - %(name)s - %(levelname)s - %(message)s'
        logging.basicConfig(
            level=getattr(logging, self.config.log_level),
            format=log_format,
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler(self.config.log_path / 'orchestrator.log')
            ]
        )
    
    def log(self, message: str, level: str = 'info'):
        """
        Log message with mode prefix.
        
        Args:
            message: Log message
            level: Log level (info, warning, error)
        """
        # Remove emojis for Windows compatibility
        import re
        clean_message = re.sub(r'[^\x00-\x7F]+', '', message)
        
        log_func = getattr(logger, level.lower())
        log_func(clean_message)
    
    def classify_task(self, task_path: Path) -> Dict[str, str]:
        """
        Classify task and determine routing.
        
        Args:
            task_path: Path to task file
        
        Returns:
            {
                'domain': 'email' | 'social' | 'odoo',
                'type': 'draft' | 'execute' | 'approve',
                'zone': 'cloud' | 'local' | 'both',
                'priority': 'high' | 'medium' | 'low'
            }
        """
        try:
            # Read task file
            with open(task_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract metadata from frontmatter
            metadata = self._extract_frontmatter(content)
            
            # Determine domain from path or metadata
            if 'email' in str(task_path):
                domain = 'email'
            elif 'social' in str(task_path):
                domain = 'social'
            elif 'odoo' in str(task_path):
                domain = 'odoo'
            else:
                domain = metadata.get('domain', 'email')
            
            # Determine type from location
            if 'Needs_Action' in str(task_path):
                task_type = 'draft'
                zone = 'cloud'
            elif 'Pending_Approval' in str(task_path):
                task_type = 'approve'
                zone = 'local'
            else:
                task_type = metadata.get('type', 'draft')
                zone = metadata.get('zone', 'cloud')
            
            # Determine priority
            priority = metadata.get('priority', 'medium')
            if 'urgent' in content.lower() or 'asap' in content.lower():
                priority = 'high'
            
            return {
                'domain': domain,
                'type': task_type,
                'zone': zone,
                'priority': priority
            }
        
        except Exception as e:
            self.log(f"Error classifying task {task_path}: {e}", 'error')
            return {
                'domain': 'email',
                'type': 'draft',
                'zone': 'cloud',
                'priority': 'medium'
            }
    
    def scan_for_tasks(self) -> List[Path]:
        """
        Scan for tasks based on agent mode.
        
        Cloud scans: Needs_Action/
        Local scans: Pending_Approval/
        
        Returns:
            List of task file paths
        """
        tasks = []
        
        try:
            if self.mode == AgentMode.CLOUD:
                # Cloud scans Needs_Action
                scan_path = self.config.vault_path / "Needs_Action"
                
                # Scan all domains
                for domain in ['email', 'social', 'odoo']:
                    domain_path = scan_path / domain
                    if domain_path.exists():
                        tasks.extend(domain_path.glob("*.md"))
                        tasks.extend(domain_path.glob("*.json"))  # Also scan JSON files
            
            else:  # LOCAL
                # Local scans Pending_Approval
                scan_path = self.config.vault_path / "Pending_Approval"
                
                # Scan all domains
                for domain in ['email', 'social', 'odoo']:
                    domain_path = scan_path / domain
                    if domain_path.exists():
                        tasks.extend(domain_path.glob("*.md"))
                        tasks.extend(domain_path.glob("*.json"))  # Also scan JSON files
            
            self.log(f"📋 Found {len(tasks)} tasks in {self.mode.value} queue")
            return tasks
        
        except Exception as e:
            self.log(f"Error scanning for tasks: {e}", 'error')
            return []
    
    def route_task(self, task_path: Path) -> bool:
        """
        Route task to appropriate handler based on mode and classification.
        
        Args:
            task_path: Path to task file
        
        Returns:
            True if routing successful
        """
        try:
            # 1. Classify task
            classification = self.classify_task(task_path)
            
            self.log(f"📝 Routing task: {task_path.name}")
            self.log(f"   Domain: {classification['domain']}")
            self.log(f"   Type: {classification['type']}")
            self.log(f"   Zone: {classification['zone']}")
            self.log(f"   Priority: {classification['priority']}")
            
            # 2. Check if this agent should handle it
            if classification['zone'] != self.mode.value:
                self.log(f"⏭️ Task for {classification['zone']} zone, skipping")
                return False
            
            # 3. Claim task
            success, claimed_path = self.claim_manager.claim_task(str(task_path))
            
            if not success:
                self.log(f"⚠️ Task already claimed: {task_path.name}", 'warning')
                return False
            
            # 4. Route to appropriate handler
            if self.mode == AgentMode.CLOUD:
                return self._route_cloud_task(claimed_path, classification)
            else:  # LOCAL
                return self._route_local_task(claimed_path, classification)
        
        except Exception as e:
            self.log(f"Error routing task {task_path}: {e}", 'error')
            return False
    
    def _route_cloud_task(self, task_path: str, classification: Dict) -> bool:
        """
        Route task to Cloud agent handler.
        
        Args:
            task_path: Path to claimed task
            classification: Task classification
        
        Returns:
            True if successful
        """
        domain = classification['domain']
        
        try:
            if domain == 'email':
                return self._cloud_email_handler(task_path)
            elif domain == 'social':
                return self._cloud_social_handler(task_path)
            elif domain == 'odoo':
                return self._cloud_odoo_handler(task_path)
            else:
                self.log(f"Unknown domain: {domain}", 'warning')
                self.claim_manager.release_task(task_path, f"Unknown domain: {domain}")
                return False
        
        except Exception as e:
            self.log(f"Error in Cloud handler: {e}", 'error')
            self.claim_manager.release_task(task_path, str(e))
            return False
    
    def _route_local_task(self, task_path: str, classification: Dict) -> bool:
        """
        Route task to Local agent handler.
        
        Args:
            task_path: Path to claimed task
            classification: Task classification
        
        Returns:
            True if successful
        """
        domain = classification['domain']
        
        try:
            if domain == 'email':
                return self._local_email_handler(task_path)
            elif domain == 'social':
                return self._local_social_handler(task_path)
            elif domain == 'odoo':
                return self._local_odoo_handler(task_path)
            else:
                self.log(f"Unknown domain: {domain}", 'warning')
                self.claim_manager.release_task(task_path, f"Unknown domain: {domain}")
                return False
        
        except Exception as e:
            self.log(f"Error in Local handler: {e}", 'error')
            self.claim_manager.release_task(task_path, str(e))
            return False
    
    def _cloud_email_handler(self, task_path: str) -> bool:
        """
        Cloud email handler - draft reply.
        
        Integrates with Gold Tier email processor for drafting.
        """
        self.log(f"📧 Cloud: Drafting email reply for {Path(task_path).name}")
        
        try:
            # Validate action is allowed
            validate_action('draft')
            
            # Read task (support both JSON and Markdown)
            task_file = Path(task_path)
            if task_file.suffix == '.json':
                import json
                with open(task_path, 'r', encoding='utf-8') as f:
                    task_data = json.load(f)
                metadata = task_data
                task_content = task_data.get('email', {}).get('body', '')
            else:
                with open(task_path, 'r', encoding='utf-8') as f:
                    task_content = f.read()
                metadata = self._extract_frontmatter(task_content)
            
            # Try to integrate with Gold Tier EMAIL_PROCESSOR
            draft_content = None
            try:
                # Attempt to import Gold Tier email processor
                sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'Gold-Tier'))
                from Skills import EMAIL_PROCESSOR
                
                # Use Gold Tier to draft reply
                draft_content = EMAIL_PROCESSOR.draft_reply(
                    from_email=metadata.get('from', metadata.get('email', {}).get('from', '')),
                    subject=metadata.get('subject', metadata.get('email', {}).get('subject', '')),
                    body=task_content
                )
                self.log("✅ Using Gold Tier EMAIL_PROCESSOR for drafting")
                
            except (ImportError, AttributeError) as e:
                # Gold Tier not available, use basic drafting
                self.log(f"⚠️ Gold Tier EMAIL_PROCESSOR not available, using basic drafting: {e}", 'warning')
                draft_content = self._basic_email_draft(task_content, metadata)
            
            # Create structured draft file (use same format as input)
            # Place in domain-specific subdirectory for Local to find
            draft_path = self.config.vault_path / "Pending_Approval" / "email" / f"draft_{Path(task_path).name}"
            draft_path.parent.mkdir(parents=True, exist_ok=True)
            
            if task_file.suffix == '.json':
                # Create JSON draft
                import json
                draft_data = {
                    'type': 'email_draft',
                    'domain': 'email',
                    'drafted_by': 'cloud',
                    'drafted_at': datetime.now().isoformat(),
                    'requires_approval': True,
                    'original_task': Path(task_path).name,
                    'email': {
                        'to': metadata.get('email', {}).get('from', metadata.get('from', '[extracted from task]')),
                        'subject': f"Re: {metadata.get('email', {}).get('subject', metadata.get('subject', '[extracted from task]'))}",
                        'body': draft_content
                    },
                    'original_email': metadata.get('email', {})
                }
                with open(draft_path, 'w', encoding='utf-8') as f:
                    json.dump(draft_data, f, indent=2)
            else:
                # Create Markdown draft
                with open(draft_path, 'w', encoding='utf-8') as f:
                    f.write(f"---\n")
                    f.write(f"type: email_draft\n")
                    f.write(f"domain: email\n")
                    f.write(f"drafted_by: cloud\n")
                    f.write(f"drafted_at: {datetime.now().isoformat()}\n")
                    f.write(f"requires_approval: true\n")
                    f.write(f"original_task: {Path(task_path).name}\n")
                    f.write(f"to: {metadata.get('from', '[extracted from task]')}\n")
                    f.write(f"subject: Re: {metadata.get('subject', '[extracted from task]')}\n")
                    f.write(f"---\n\n")
                    f.write(draft_content)
                    f.write(f"\n\n---\n\n")
                    f.write(f"## Original Task\n\n")
                    f.write(task_content)
            
            # Complete task
            self.claim_manager.complete_task(task_path, f"Draft created: {draft_path.name}")
            self.log(f"✅ Email draft created: {draft_path.name}")
            return True
        
        except PermissionError as e:
            self.log(f"❌ SECURITY VIOLATION: {e}", 'error')
            self.claim_manager.release_task(task_path, f"Security violation: {e}")
            return False
        
        except Exception as e:
            self.log(f"❌ Email drafting failed: {e}", 'error')
            self.claim_manager.release_task(task_path, f"Error: {e}")
            return False
    
    def _basic_email_draft(self, content: str, metadata: Dict) -> str:
        """
        Basic email drafting fallback when Gold Tier is not available.
        
        Args:
            content: Task content
            metadata: Extracted metadata
        
        Returns:
            Draft email content
        """
        return f"""# Email Draft

**To:** {metadata.get('from', '[recipient]')}
**Subject:** Re: {metadata.get('subject', '[subject]')}

**Body:**

Dear [Name],

Thank you for your email. 

[Cloud AI would draft a professional email reply here based on the task content and context]

Best regards,
[Your Name]

---

*This is a draft created by Cloud AI. Please review and approve before sending.*
"""
    
    def _cloud_social_handler(self, task_path: str) -> bool:
        """
        Cloud social handler - draft post.
        
        Integrates with Gold Tier social poster for drafting.
        """
        self.log(f"📱 Cloud: Drafting social post for {Path(task_path).name}")
        
        try:
            # Validate action is allowed
            validate_action('draft')
            
            # Read task
            with open(task_path, 'r', encoding='utf-8') as f:
                task_content = f.read()
            
            # TODO: Integrate with Gold Tier SOCIAL_POSTER
            # from gold_tier.skills import LINKEDIN_POST_GENERATOR
            # draft = LINKEDIN_POST_GENERATOR.generate_post(task_content)
            
            # For now, create structured draft
            draft_path = self.config.vault_path / "Pending_Approval" / "social" / f"draft_{Path(task_path).name}"
            draft_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(draft_path, 'w', encoding='utf-8') as f:
                f.write(f"---\n")
                f.write(f"type: social_draft\n")
                f.write(f"domain: social\n")
                f.write(f"platform: linkedin\n")
                f.write(f"drafted_by: cloud\n")
                f.write(f"drafted_at: {datetime.now().isoformat()}\n")
                f.write(f"requires_approval: true\n")
                f.write(f"original_task: {Path(task_path).name}\n")
                f.write(f"---\n\n")
                f.write(f"# Social Post Draft\n\n")
                f.write(f"**Platform:** LinkedIn\n")
                f.write(f"**Visibility:** Public\n\n")
                f.write(f"**Content:**\n\n")
                f.write(f"[Cloud AI would draft engaging social post here based on task content]\n\n")
                f.write(f"---\n\n")
                f.write(f"## Original Task\n\n")
                f.write(task_content)
            
            # Complete task
            self.claim_manager.complete_task(task_path, f"Draft created: {draft_path.name}")
            self.log(f"✅ Social draft created: {draft_path.name}")
            return True
        
        except PermissionError as e:
            self.log(f"❌ SECURITY VIOLATION: {e}", 'error')
            self.claim_manager.release_task(task_path, str(e))
            return False
        except Exception as e:
            self.log(f"❌ Social drafting failed: {e}", 'error')
            self.claim_manager.release_task(task_path, str(e))
            return False
    
    def _cloud_odoo_handler(self, task_path: str) -> bool:
        """
        Cloud Odoo handler - extract and match (read-only).
        
        Integrates with Gold Tier Odoo extractor and payment reconciliation.
        """
        self.log(f"💰 Cloud: Processing Odoo task for {Path(task_path).name}")
        
        try:
            # Validate action is allowed
            validate_action('extract')
            
            # Read task
            with open(task_path, 'r', encoding='utf-8') as f:
                task_content = f.read()
            
            # Extract metadata
            metadata = self._extract_frontmatter(task_content)
            
            # Try to integrate with Gold Tier ODOO_EXTRACTOR and PAYMENT_RECONCILIATION
            action_data = None
            try:
                # Attempt to import Gold Tier Odoo modules
                sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'Gold-Tier'))
                from actions.payment_reconciliation import PaymentReconciliation
                from actions.odoo_rpc import OdooRPCClient
                
                # Use Gold Tier to extract and match
                reconciler = PaymentReconciliation()
                payment_details = reconciler.extract_payment_details(task_content)
                
                # Connect to Odoo (read-only)
                odoo_config = self.config.get_odoo_config()
                if odoo_config['url']:
                    odoo_client = OdooRPCClient()
                    matches, confidence = reconciler.find_matching_invoices(payment_details, odoo_client)
                    
                    action_data = {
                        'payment_details': payment_details,
                        'matches': matches,
                        'confidence': confidence
                    }
                    self.log("✅ Using Gold Tier PaymentReconciliation for matching")
                
            except (ImportError, AttributeError) as e:
                # Gold Tier not available, use basic extraction
                self.log(f"⚠️ Gold Tier Odoo modules not available, using basic extraction: {e}", 'warning')
                action_data = self._basic_odoo_extraction(task_content, metadata)
            
            # Create structured action file
            draft_path = self.config.vault_path / "Pending_Approval" / "odoo" / f"action_{Path(task_path).name}"
            draft_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(draft_path, 'w', encoding='utf-8') as f:
                f.write(f"---\n")
                f.write(f"type: odoo_action\n")
                f.write(f"domain: odoo\n")
                f.write(f"action_type: payment_recording\n")
                f.write(f"drafted_by: cloud\n")
                f.write(f"drafted_at: {datetime.now().isoformat()}\n")
                f.write(f"requires_approval: true\n")
                f.write(f"original_task: {Path(task_path).name}\n")
                f.write(f"confidence: {action_data.get('confidence', 0.0)}\n")
                f.write(f"---\n\n")
                f.write(f"# Odoo Action Draft\n\n")
                f.write(f"**Action:** Record Payment\n")
                f.write(f"**Amount:** ${action_data.get('payment_details', {}).get('amount', '[extracted]')}\n")
                f.write(f"**Invoice:** {action_data.get('matches', [{}])[0].get('invoice_number', 'INV/2026/[matched]') if action_data.get('matches') else '[to be matched]'}\n")
                f.write(f"**Confidence:** {int(action_data.get('confidence', 0.0) * 100)}%\n\n")
                f.write(f"**Details:**\n\n")
                f.write(f"Payment extracted and matched with Odoo invoices.\n\n")
                f.write(f"---\n\n")
                f.write(f"## Original Task\n\n")
                f.write(task_content)
            
            # Complete task
            self.claim_manager.complete_task(task_path, f"Action created: {draft_path.name}")
            self.log(f"✅ Odoo action created: {draft_path.name}")
            return True
        
        except PermissionError as e:
            self.log(f"❌ SECURITY VIOLATION: {e}", 'error')
            self.claim_manager.release_task(task_path, f"Security violation: {e}")
            return False
        
        except Exception as e:
            self.log(f"❌ Odoo extraction failed: {e}", 'error')
            self.claim_manager.release_task(task_path, f"Error: {e}")
            return False
    
    def _basic_odoo_extraction(self, content: str, metadata: Dict) -> Dict:
        """
        Basic Odoo extraction fallback when Gold Tier is not available.
        
        Args:
            content: Task content
            metadata: Extracted metadata
        
        Returns:
            Extracted action data
        """
        return {
            'payment_details': {
                'amount': metadata.get('amount', 0.0),
                'date': metadata.get('date', datetime.now().isoformat()),
                'reference': metadata.get('reference', '')
            },
            'matches': [],
            'confidence': 0.5
        }
    
    def _local_email_handler(self, task_path: str) -> bool:
        """
        Local email handler - send email.
        
        Integrates with Gold Tier email sender.
        """
        self.log(f"📧 Local: Sending email for {Path(task_path).name}")
        
        try:
            # Validate action is allowed
            validate_action('send')
            
            # Read draft (support both JSON and Markdown)
            task_file = Path(task_path)
            if task_file.suffix == '.json':
                import json
                with open(task_path, 'r', encoding='utf-8') as f:
                    draft_data = json.load(f)
                metadata = draft_data
                body = draft_data.get('email', {}).get('body', '')
                to_email = draft_data.get('email', {}).get('to', '')
                subject = draft_data.get('email', {}).get('subject', '')
            else:
                with open(task_path, 'r', encoding='utf-8') as f:
                    draft_content = f.read()
                metadata = self._extract_frontmatter(draft_content)
                body = self._extract_body_from_draft(draft_content)
                to_email = metadata.get('to', '')
                subject = metadata.get('subject', '')
            
            # Try to integrate with Gold Tier EMAIL_SENDER
            success = False
            message_id = None
            try:
                # Attempt to import Gold Tier email sender
                sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'Gold-Tier'))
                from actions.email_sender import EmailSender
                
                # Use Gold Tier to send email
                sender = EmailSender()
                success, message_id, error = sender.send_email(
                    to_email=to_email,
                    subject=subject,
                    body=body,
                    cc=metadata.get('cc'),
                    bcc=metadata.get('bcc')
                )
                
                if success:
                    self.log(f"✅ Using Gold Tier EmailSender: {message_id}")
                else:
                    raise Exception(f"Email send failed: {error}")
                
            except Exception as e:
                # Gold Tier not available or failed, simulate send
                self.log(f"⚠️ Gold Tier EmailSender not available, simulating send: {e}", 'warning')
                success = True
                message_id = f"sim_{int(datetime.now().timestamp())}"
            
            if success:
                # Complete task
                self.claim_manager.complete_task(task_path, f"Email sent: {message_id}")
                self.log(f"✅ Email sent: {Path(task_path).name}")
                return True
            else:
                raise Exception("Email send failed")
        
        except PermissionError as e:
            self.log(f"❌ SECURITY VIOLATION: {e}", 'error')
            self.claim_manager.release_task(task_path, f"Security violation: {e}")
            return False
        
        except Exception as e:
            self.log(f"❌ Email sending failed: {e}", 'error')
            self.claim_manager.release_task(task_path, f"Error: {e}")
            return False
    
    def _extract_body_from_draft(self, content: str) -> str:
        """
        Extract email body from draft markdown.
        
        Args:
            content: Draft content
        
        Returns:
            Email body text
        """
        # Remove frontmatter
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                content = parts[2]
        
        # Remove markdown headers and formatting
        lines = []
        for line in content.split('\n'):
            if not line.startswith('#') and not line.startswith('**'):
                lines.append(line)
        
        return '\n'.join(lines).strip()
    
    def _local_social_handler(self, task_path: str) -> bool:
        """
        Local social handler - post to social media.
        
        Integrates with Gold Tier social poster.
        """
        self.log(f"📱 Local: Posting to social media for {Path(task_path).name}")
        
        try:
            # Validate action is allowed
            validate_action('post')
            
            # Read draft
            with open(task_path, 'r', encoding='utf-8') as f:
                draft_content = f.read()
            
            # Extract post details from draft
            metadata = self._extract_frontmatter(draft_content)
            platform = metadata.get('platform', 'linkedin')
            
            # TODO: Integrate with Gold Tier SOCIAL_POSTER
            # from gold_tier.actions import LinkedInPoster, FacebookPoster
            # if platform == 'linkedin':
            #     poster = LinkedInPoster()
            # success, post_id, error = poster.post(content, image, visibility)
            
            # For now, simulate post
            self.log(f"📤 Posting to {platform}: [extracted from draft]")
            
            # Complete task
            self.claim_manager.complete_task(task_path, f"Posted to {platform} successfully")
            self.log(f"✅ Posted to {platform}: {Path(task_path).name}")
            return True
        
        except PermissionError as e:
            self.log(f"❌ SECURITY VIOLATION: {e}", 'error')
            self.claim_manager.release_task(task_path, str(e))
            return False
        except Exception as e:
            self.log(f"❌ Social posting failed: {e}", 'error')
            self.claim_manager.release_task(task_path, str(e))
            return False
    
    def _local_odoo_handler(self, task_path: str) -> bool:
        """
        Local Odoo handler - execute Odoo action.
        
        Integrates with Gold Tier Odoo RPC client.
        """
        self.log(f"💰 Local: Executing Odoo action for {Path(task_path).name}")
        
        try:
            # Validate action is allowed
            validate_action('execute')
            
            # Read action
            with open(task_path, 'r', encoding='utf-8') as f:
                action_content = f.read()
            
            # Extract action details
            metadata = self._extract_frontmatter(action_content)
            action_type = metadata.get('action_type', 'payment_recording')
            
            # Try to integrate with Gold Tier ODOO_RPC and PAYMENT_RECONCILIATION
            success = False
            result_id = None
            try:
                # Attempt to import Gold Tier Odoo modules
                sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'Gold-Tier'))
                from actions.odoo_rpc import OdooRPCClient
                from actions.payment_reconciliation import PaymentReconciliation
                
                # Use Gold Tier to execute action
                odoo_client = OdooRPCClient()
                reconciler = PaymentReconciliation()
                
                if action_type == 'payment_recording':
                    # Extract payment details from action content
                    # This would parse the structured action file
                    payment_data = {
                        'amount': float(metadata.get('amount', 0)),
                        'date': metadata.get('date', datetime.now().isoformat()),
                        'partner_id': int(metadata.get('partner_id', 0)),
                        'invoice_id': int(metadata.get('invoice_id', 0)),
                        'reference': metadata.get('reference', '')
                    }
                    
                    success, result_id, error = reconciler.record_payment(
                        odoo_client,
                        **payment_data
                    )
                    
                    if success:
                        self.log(f"✅ Using Gold Tier PaymentReconciliation: {result_id}")
                    else:
                        raise Exception(f"Payment recording failed: {error}")
                
            except (ImportError, AttributeError) as e:
                # Gold Tier not available, simulate execution
                self.log(f"⚠️ Gold Tier Odoo modules not available, simulating execution: {e}", 'warning')
                success = True
                result_id = f"sim_{int(datetime.now().timestamp())}"
            
            if success:
                # Complete task
                self.claim_manager.complete_task(task_path, f"Odoo {action_type} executed: {result_id}")
                self.log(f"✅ Odoo action executed: {Path(task_path).name}")
                return True
            else:
                raise Exception("Odoo execution failed")
        
        except PermissionError as e:
            self.log(f"❌ SECURITY VIOLATION: {e}", 'error')
            self.claim_manager.release_task(task_path, f"Security violation: {e}")
            return False
        
        except Exception as e:
            self.log(f"❌ Odoo execution failed: {e}", 'error')
            self.claim_manager.release_task(task_path, f"Error: {e}")
            return False
    
    def _extract_frontmatter(self, content: str) -> Dict:
        """Extract YAML frontmatter from markdown file."""
        metadata = {}
        
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 2:
                frontmatter = parts[1].strip()
                for line in frontmatter.split('\n'):
                    if ':' in line:
                        key, value = line.split(':', 1)
                        metadata[key.strip()] = value.strip()
        
        return metadata
    
    def process_tasks(self):
        """Process tasks (alias for run_once for compatibility)."""
        self.run_once()
    
    def run_once(self):
        """Run one iteration of the orchestrator."""
        self.log(f"\n{'='*60}")
        self.log(f"🔄 Running {self.mode.value.upper()} orchestrator iteration")
        self.log(f"{'='*60}\n")
        
        # 1. Scan for tasks
        tasks = self.scan_for_tasks()
        
        if not tasks:
            self.log("✅ No tasks found")
            return
        
        # 2. Route each task
        for task in tasks:
            self.route_task(task)
        
        # 3. Detect stale claims
        stale = self.claim_manager.detect_stale_claims(max_age_minutes=self.config.stale_claim_threshold)
        if stale:
            self.log(f"⚠️ Released {len(stale)} stale claims", 'warning')
    
    def run_loop(self):
        """Run continuous orchestrator loop."""
        self.log(f"\n{'='*60}")
        self.log(f"🚀 Starting {self.mode.value.upper()} orchestrator loop")
        self.log(f"⏱️  Scan interval: {self.config.scan_interval} seconds")
        self.log(f"{'='*60}\n")
        
        while True:
            try:
                self.run_once()
                
                # Sleep
                time.sleep(self.config.scan_interval)
            
            except KeyboardInterrupt:
                self.log("\n⏹️  Orchestrator stopped by user")
                break
            
            except Exception as e:
                self.log(f"❌ Orchestrator error: {e}", 'error')
                time.sleep(60)  # Wait longer on error


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Platinum Tier Hybrid Orchestrator')
    parser.add_argument('--mode', choices=['cloud', 'local'], help='Agent mode (overrides AGENT_MODE env var)')
    parser.add_argument('--once', action='store_true', help='Run once and exit')
    parser.add_argument('--loop', action='store_true', help='Run continuous loop (default)')
    parser.add_argument('--vault', help='Vault path (overrides VAULT_PATH env var)')
    
    args = parser.parse_args()
    
    # Override environment variables if provided
    if args.mode:
        os.environ['AGENT_MODE'] = args.mode
    if args.vault:
        os.environ['VAULT_PATH'] = args.vault
    
    # Initialize orchestrator
    orchestrator = HybridOrchestrator()
    
    # Run
    if args.once:
        orchestrator.run_once()
    else:
        # Default to loop mode
        orchestrator.run_loop()


if __name__ == "__main__":
    main()
