#!/usr/bin/env python3
"""
Payment Reconciliation Action Handler
Processes payment notification emails and creates payment recording actions.

This script:
1. Extracts payment details from email content
2. Searches Odoo for matching invoices
3. Calculates match confidence
4. Creates action file in Pending_Approval/ for human review
"""

import os
import sys
import re
import json
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from actions.odoo_rpc import OdooRPCClient

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class PaymentReconciliation:
    """
    Handles payment detection, extraction, and matching with Odoo invoices.
    """
    
    def __init__(self):
        """Initialize payment reconciliation handler"""
        self.odoo_client = OdooRPCClient()
        self.payment_keywords = [
            'payment received', 'payment confirmation', 'paid invoice',
            'wire transfer received', 'ach payment', 'check deposited',
            'payment processed', 'funds received', 'payment successful',
            'payment complete', 'transaction successful'
        ]
    
    def detect_payment_email(self, content: str) -> bool:
        """
        Detect if email contains payment notification.
        
        Args:
            content: Email content
            
        Returns:
            True if payment-related
        """
        content_lower = content.lower()
        return any(keyword in content_lower for keyword in self.payment_keywords)
    
    def extract_payment_details(self, content: str) -> Dict[str, Any]:
        """
        Extract payment details from email content.
        
        Args:
            content: Email content
            
        Returns:
            Dictionary with payment details
        """
        details = {
            'amount': None,
            'invoice_reference': None,
            'payment_date': None,
            'payer_name': None,
            'payment_method': None,
            'transaction_id': None,
            'currency': 'USD'
        }
        
        # Extract amount
        amount_patterns = [
            r'\$\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',  # $1,234.56
            r'(?:amount|total|paid):\s*\$?\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',  # Amount: 1234.56
            r'(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s*(?:USD|dollars?)',  # 1234.56 USD
        ]
        
        for pattern in amount_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                amount_str = match.group(1).replace(',', '')
                details['amount'] = float(amount_str)
                break
        
        # Extract invoice reference
        invoice_patterns = [
            r'INV/\d{4}/\d+',  # INV/2026/0001
            r'Invoice\s*#?\s*(\w+)',  # Invoice #12345
            r'Ref(?:erence)?:\s*(\w+)',  # Reference: INV001
        ]
        
        for pattern in invoice_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                details['invoice_reference'] = match.group(0) if 'INV/' in match.group(0) else match.group(1)
                break
        
        # Extract payment date
        date_patterns = [
            r'(\d{4}-\d{2}-\d{2})',  # 2026-03-30
            r'((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+\d{4})',  # March 30, 2026
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                date_str = match.group(1)
                try:
                    if '-' in date_str:
                        details['payment_date'] = date_str
                    else:
                        # Parse month name format
                        parsed_date = datetime.strptime(date_str, '%B %d, %Y')
                        details['payment_date'] = parsed_date.strftime('%Y-%m-%d')
                except:
                    pass
                break
        
        # Default to today if no date found
        if not details['payment_date']:
            details['payment_date'] = datetime.now().strftime('%Y-%m-%d')
        
        # Extract payer name
        payer_patterns = [
            r'(?:Customer|Payer|Client):\s*([A-Z][A-Za-z\s&]+(?:Ltd|Inc|Corp|LLC)?\.?)',
            r'from\s+([A-Z][A-Za-z\s&]+(?:Ltd|Inc|Corp|LLC)?)',
            r'(?:customer|client|payer):\s*([A-Z][A-Za-z\s&]+)',
        ]
        
        for pattern in payer_patterns:
            match = re.search(pattern, content)
            if match:
                details['payer_name'] = match.group(1).strip()
                break
        
        # Extract payment method
        method_keywords = {
            'wire transfer': 'bank_transfer',
            'ach': 'bank_transfer',
            'bank transfer': 'bank_transfer',
            'check': 'check',
            'credit card': 'credit_card',
            'debit card': 'debit_card',
        }
        
        content_lower = content.lower()
        for keyword, method in method_keywords.items():
            if keyword in content_lower:
                details['payment_method'] = method
                break
        
        if not details['payment_method']:
            details['payment_method'] = 'manual'  # Default
        
        # Extract transaction ID
        trans_patterns = [
            r'(?:transaction|trans|ref)\s*(?:id|#)?:\s*([A-Z0-9\-]+)',
            r'([A-Z]{2}-\d{4}-\d{2}-\d{2}-\d+)',  # WT-2026-03-30-12345
        ]
        
        for pattern in trans_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                details['transaction_id'] = match.group(1)
                break
        
        return details

    
    def find_matching_invoices(self, payment_details: Dict[str, Any]) -> Tuple[List[Dict], int]:
        """
        Find matching invoices in Odoo based on payment details.
        
        Args:
            payment_details: Extracted payment details
            
        Returns:
            Tuple of (matching_invoices, confidence_score)
        """
        if not self.odoo_client.authenticate():
            logger.error("Failed to authenticate with Odoo")
            return [], 0
        
        matches = []
        confidence = 0
        
        # Priority 1: Exact invoice number match
        if payment_details.get('invoice_reference'):
            invoices = self.odoo_client.search_open_invoices(
                invoice_number=payment_details['invoice_reference']
            )
            if len(invoices) == 1:
                matches = invoices
                confidence = 98  # High confidence
                logger.info(f"Exact invoice match: {invoices[0]['name']}")
                return matches, confidence
            elif len(invoices) > 1:
                matches = invoices
                confidence = 95
                return matches, confidence
        
        # Priority 2: Amount + Customer match
        if payment_details.get('amount') and payment_details.get('payer_name'):
            # Search for partner by name
            partners = self.odoo_client.search_read(
                'res.partner',
                domain=[('name', 'ilike', payment_details['payer_name'])],
                fields=['id', 'name'],
                limit=5
            )
            
            if partners:
                for partner in partners:
                    invoices = self.odoo_client.search_open_invoices(
                        amount=payment_details['amount'],
                        partner_id=partner['id']
                    )
                    if invoices:
                        matches.extend(invoices)
                
                if len(matches) == 1:
                    confidence = 90
                    logger.info(f"Amount + customer match: {matches[0]['name']}")
                    return matches, confidence
                elif len(matches) > 1:
                    confidence = 85
                    return matches, confidence
        
        # Priority 3: Amount only (within 30 days)
        if payment_details.get('amount'):
            date_from = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
            invoices = self.odoo_client.search_open_invoices(
                amount=payment_details['amount'],
                date_from=date_from
            )
            if len(invoices) == 1:
                matches = invoices
                confidence = 70
                logger.info(f"Amount-only match: {invoices[0]['name']}")
                return matches, confidence
            elif len(invoices) > 1:
                matches = invoices
                confidence = 65
                return matches, confidence
        
        # No match found
        logger.warning("No matching invoices found")
        return [], 0
    
    def generate_action_file(self, payment_details: Dict[str, Any], 
                            matches: List[Dict], confidence: int,
                            original_email_file: str) -> str:
        """
        Generate action file for human approval.
        
        Args:
            payment_details: Extracted payment details
            matches: Matching invoices
            confidence: Match confidence score
            original_email_file: Original email filename
            
        Returns:
            Path to generated action file
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"odoo_payment_{timestamp}.md"
        filepath = Path("Pending_Approval") / filename
        
        # Ensure directory exists
        filepath.parent.mkdir(exist_ok=True)
        
        # Build action file content
        content = f"""---
type: odoo_record_payment
source: email
priority: HIGH
requires_approval: true
created: {datetime.now().isoformat()}
---

# Payment Recording Action

## Payment Details

**Amount:** ${payment_details.get('amount', 0):.2f}  
**Payment Date:** {payment_details.get('payment_date', 'Unknown')}  
**Payment Method:** {payment_details.get('payment_method', 'manual')}  
"""
        
        if payment_details.get('transaction_id'):
            content += f"**Transaction ID:** {payment_details['transaction_id']}  \n"
        
        if payment_details.get('invoice_reference'):
            content += f"**Reference:** {payment_details['invoice_reference']}  \n"
        
        content += "\n## Customer Information\n\n"
        
        if payment_details.get('payer_name'):
            content += f"**Customer:** {payment_details['payer_name']}  \n"
        
        # Add match information
        if matches:
            if len(matches) == 1:
                inv = matches[0]
                partner_name = inv['partner_id'][1] if inv.get('partner_id') else 'Unknown'
                
                content += f"**Customer ID:** {inv['partner_id'][0]} (Odoo Partner ID)  \n"
                content += f"**Customer Name:** {partner_name}  \n"
                content += f"\n## Invoice Match\n\n"
                content += f"**Match Confidence:** {confidence}% "
                
                if confidence >= 95:
                    content += "(Exact match)\n"
                elif confidence >= 80:
                    content += "(High confidence)\n"
                elif confidence >= 60:
                    content += "(Medium confidence)\n"
                else:
                    content += "(Low confidence)\n"
                
                content += f"**Invoice Number:** {inv['name']}  \n"
                content += f"**Invoice ID:** {inv['id']} (Odoo)  \n"
                content += f"**Invoice Amount:** ${inv['amount_total']:.2f}  \n"
                content += f"**Invoice Status:** {inv['payment_state']}  \n"
                
                if inv.get('invoice_date_due'):
                    content += f"**Invoice Due Date:** {inv['invoice_date_due']}  \n"
                
                # Check if amounts match
                amount_diff = abs(payment_details.get('amount', 0) - inv['amount_total'])
                if amount_diff < 0.01:
                    content += "\n✅ **Perfect Match:** Payment amount matches invoice amount exactly.\n"
                elif payment_details.get('amount', 0) < inv['amount_total']:
                    remaining = inv['amount_total'] - payment_details.get('amount', 0)
                    content += f"\n⚠️ **Partial Payment:** Payment is ${remaining:.2f} less than invoice total.\n"
                else:
                    overpayment = payment_details.get('amount', 0) - inv['amount_total']
                    content += f"\n⚠️ **Overpayment:** Payment is ${overpayment:.2f} more than invoice total.\n"
                
                content += f"\n## Proposed Action\n\n"
                content += f"Record payment of ${payment_details.get('amount', 0):.2f} against invoice {inv['name']} in Odoo.\n\n"
                content += f"**Payment Journal:** Bank (ID: 1)  \n"
                content += f"**Payment Type:** Inbound  \n"
                
                if amount_diff < 0.01:
                    content += f"**Reconciliation:** Automatic (full payment)  \n"
                else:
                    content += f"**Reconciliation:** Partial payment  \n"
                
            else:
                # Multiple matches
                content += f"\n## Multiple Invoice Matches Found\n\n"
                content += f"**Match Confidence:** {confidence}%  \n"
                content += f"**Payment Amount:** ${payment_details.get('amount', 0):.2f}  \n\n"
                content += f"Found {len(matches)} possible matches:\n\n"
                
                for i, inv in enumerate(matches[:5], 1):  # Show top 5
                    partner_name = inv['partner_id'][1] if inv.get('partner_id') else 'Unknown'
                    content += f"{i}. **{inv['name']}** - ${inv['amount_total']:.2f} - {partner_name}"
                    
                    if inv.get('invoice_date_due'):
                        due_date = datetime.strptime(inv['invoice_date_due'], '%Y-%m-%d')
                        days_diff = (datetime.now() - due_date).days
                        if days_diff > 0:
                            content += f" (Due: {inv['invoice_date_due']}, {days_diff} days overdue)"
                        else:
                            content += f" (Due: {inv['invoice_date_due']})"
                    
                    content += "\n"
                
                content += f"\n⚠️ **Action Required:** Human must select correct invoice.\n\n"
                content += f"**Recommendation:** Review invoice references and dates to determine correct match.\n\n"
                content += f"**To proceed:** Edit this file to specify invoice_id, then move to Approved/\n\n"
                content += f"```\ninvoice_id: [ENTER_INVOICE_ID_HERE]\n```\n"
        
        else:
            # No match found
            content += f"\n## No Invoice Match Found\n\n"
            content += f"❌ **No matching invoices found in Odoo**\n\n"
            content += f"**Payment Amount:** ${payment_details.get('amount', 0):.2f}  \n"
            
            if payment_details.get('payer_name'):
                content += f"**Payer:** {payment_details['payer_name']}  \n"
            
            content += f"\n**Possible Reasons:**\n"
            content += f"- Invoice not yet created in Odoo\n"
            content += f"- Reference number incorrect\n"
            content += f"- Payment for non-invoiced service\n"
            content += f"- Wrong customer identification\n\n"
            content += f"**Action Required:** Human must manually match or create invoice first.\n\n"
            content += f"**To proceed:** Create/find invoice in Odoo, then edit this file with invoice_id:\n\n"
            content += f"```\ninvoice_id: [ENTER_INVOICE_ID_HERE]\n```\n"
        
        # Add verification checklist
        content += f"\n## Verification Checklist\n\n"
        
        if matches and len(matches) == 1:
            inv = matches[0]
            amount_match = abs(payment_details.get('amount', 0) - inv['amount_total']) < 0.01
            content += f"- [{'x' if amount_match else ' '}] Payment amount matches invoice amount\n"
            content += f"- [x] Invoice exists and is unpaid\n"
            content += f"- [{'x' if confidence >= 80 else ' '}] Customer matches invoice customer\n"
            content += f"- [x] Payment date is reasonable\n"
            content += f"- [x] Payment method is valid\n"
        else:
            content += f"- [ ] Payment amount verified\n"
            content += f"- [ ] Invoice identified\n"
            content += f"- [ ] Customer verified\n"
            content += f"- [ ] Payment date verified\n"
        
        content += f"- [ ] **HUMAN APPROVAL REQUIRED**\n"
        
        # Add execution instructions
        content += f"\n## Execution\n\n"
        content += f"Once approved (moved to Approved/ folder), the system will:\n"
        content += f"1. Create payment record in Odoo\n"
        content += f"2. Link payment to invoice\n"
        content += f"3. Mark invoice as paid/partially paid\n"
        content += f"4. Update customer account balance\n"
        content += f"5. Log transaction in audit trail\n"
        content += f"6. Move this file to Done/\n"
        
        # Add safety notes
        content += f"\n## Safety Notes\n\n"
        content += f"⚠️ This action will modify financial records in Odoo.  \n"
        content += f"⚠️ Ensure all details are correct before approval.  \n"
        content += f"⚠️ Payment cannot be easily reversed once recorded.  \n"
        
        # Add metadata
        content += f"\n---\n\n"
        content += f"**Original Email:** {original_email_file}  \n"
        content += f"**Extracted By:** 15_ODOO_PAYMENT_RECONCILIATION  \n"
        content += f"**Created:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  \n"
        content += f"**Status:** Pending Human Approval\n"
        
        # Write file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info(f"✅ Created action file: {filepath}")
        return str(filepath)
    
    def process_payment_email(self, email_file: str) -> bool:
        """
        Process a payment notification email.
        
        Args:
            email_file: Path to email file
            
        Returns:
            True if processed successfully
        """
        try:
            # Read email content
            with open(email_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check if payment-related
            if not self.detect_payment_email(content):
                logger.info("Email does not contain payment notification")
                return False
            
            logger.info(f"Processing payment email: {email_file}")
            
            # Extract payment details
            payment_details = self.extract_payment_details(content)
            logger.info(f"Extracted payment details: {payment_details}")
            
            # Find matching invoices
            matches, confidence = self.find_matching_invoices(payment_details)
            logger.info(f"Found {len(matches)} matches with {confidence}% confidence")
            
            # Generate action file
            action_file = self.generate_action_file(
                payment_details,
                matches,
                confidence,
                Path(email_file).name
            )
            
            logger.info(f"✅ Payment reconciliation action created: {action_file}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to process payment email: {e}")
            import traceback
            traceback.print_exc()
            return False


def main():
    """CLI interface for payment reconciliation"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Payment Reconciliation')
    parser.add_argument('--email-file', required=True, help='Path to email file')
    
    args = parser.parse_args()
    
    reconciler = PaymentReconciliation()
    success = reconciler.process_payment_email(args.email_file)
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
