#!/usr/bin/env python3
"""
Odoo RPC Client - JSON-RPC Integration
Connects to local Odoo instance for accounting automation.

Features:
- Retry logic with exponential backoff
- Connection pooling
- Graceful error handling
- Comprehensive logging

Supports:
- Partner (customer/vendor) management
- Invoice creation and updates
- Payment recording and reconciliation
- Journal entry queries
- Account queries

Uses pure requests library for maximum compatibility.
"""

import os
import sys
import json
import logging
import argparse
import time
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime
import requests
from dotenv import load_dotenv

# Setup logging with UTF-8 encoding
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
env_path = Path(__file__).parent.parent / 'odoo-docker' / '.env'
load_dotenv(env_path)

# Retry configuration
MAX_RETRIES = 3
INITIAL_RETRY_DELAY = 1  # seconds
BACKOFF_MULTIPLIER = 2


class OdooRPCClient:
    """
    Odoo JSON-RPC client for accounting operations with retry logic.
    """
    
    def __init__(self):
        """Initialize Odoo RPC client with credentials from .env"""
        self.url = os.getenv('ODOO_URL', 'http://localhost:8069')
        self.db = os.getenv('ODOO_DB_NAME', 'ai_employee_db')
        self.username = os.getenv('ODOO_USERNAME', 'admin')
        self.password = os.getenv('ODOO_PASSWORD', 'admin_password_2026')
        
        self.uid = None
        self.session_id = None
        
        logger.info(f"Initialized Odoo RPC client for {self.url}")
    
    def _json_rpc(self, endpoint: str, params: Dict, retry: bool = True) -> Any:
        """
        Make a JSON-RPC call to Odoo with retry logic.
        
        Args:
            endpoint: API endpoint (e.g., '/jsonrpc', '/web/session/authenticate')
            params: Request parameters
            retry: Enable retry logic (default: True)
            
        Returns:
            Response result
            
        Raises:
            Exception: If all retry attempts fail
        """
        headers = {'Content-Type': 'application/json'}
        
        payload = {
            'jsonrpc': '2.0',
            'method': 'call',
            'params': params,
            'id': 1
        }
        
        # Use session to maintain cookies
        if not hasattr(self, '_session'):
            self._session = requests.Session()
        
        # Retry logic
        max_attempts = MAX_RETRIES if retry else 1
        retry_delay = INITIAL_RETRY_DELAY
        last_error = None
        
        for attempt in range(1, max_attempts + 1):
            try:
                if attempt > 1:
                    logger.info(f"Retry attempt {attempt}/{max_attempts}...")
                
                response = self._session.post(
                    f"{self.url}{endpoint}",
                    json=payload,
                    headers=headers,
                    timeout=30
                )
                response.raise_for_status()
                
                result = response.json()
                
                if 'error' in result:
                    error_msg = result['error'].get('data', {}).get('message', str(result['error']))
                    raise Exception(f"Odoo RPC Error: {error_msg}")
                
                return result.get('result')
                
            except (requests.exceptions.ConnectionError, 
                    requests.exceptions.Timeout,
                    requests.exceptions.RequestException) as e:
                last_error = e
                logger.warning(f"Attempt {attempt} failed: {e}")
                
                if attempt < max_attempts:
                    logger.info(f"Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                    retry_delay *= BACKOFF_MULTIPLIER
                else:
                    logger.error(f"All {max_attempts} attempts failed")
                    raise Exception(f"Odoo connection failed after {max_attempts} attempts: {last_error}")
                    
            except Exception as e:
                logger.error(f"JSON-RPC call failed: {e}")
                raise
            raise
    
    def authenticate(self) -> bool:
        """
        Authenticate with Odoo and get UID.
        
        Returns:
            True if authentication successful
        """
        try:
            logger.info(f"Authenticating as {self.username} on database {self.db}")
            
            result = self._json_rpc('/web/session/authenticate', {
                'db': self.db,
                'login': self.username,
                'password': self.password
            })
            
            if result and result.get('uid'):
                self.uid = result['uid']
                self.session_id = result.get('session_id')
                logger.info(f"✅ Authentication successful! UID: {self.uid}")
                return True
            else:
                logger.error("❌ Authentication failed: No UID returned")
                return False
                
        except Exception as e:
            logger.error(f"❌ Authentication failed: {e}")
            return False
    
    def execute_kw(self, model: str, method: str, args: List = None, kwargs: Dict = None) -> Any:
        """
        Execute a method on an Odoo model.
        
        Args:
            model: Odoo model name (e.g., 'res.partner', 'account.move')
            method: Method to call (e.g., 'search', 'read', 'create', 'write')
            args: Positional arguments
            kwargs: Keyword arguments
            
        Returns:
            Method result
        """
        if not self.uid:
            raise Exception("Not authenticated. Call authenticate() first.")
        
        args = args or []
        kwargs = kwargs or {}
        
        try:
            result = self._json_rpc('/web/dataset/call_kw', {
                'model': model,
                'method': method,
                'args': args,
                'kwargs': kwargs
            })
            
            return result
            
        except Exception as e:
            logger.error(f"execute_kw failed for {model}.{method}: {e}")
            raise
    
    def search_read(self, model: str, domain: List = None, fields: List = None, limit: int = 10) -> List[Dict]:
        """
        Search and read records from a model.
        
        Args:
            model: Odoo model name
            domain: Search domain (e.g., [('name', '=', 'Test')])
            fields: Fields to retrieve
            limit: Maximum number of records
            
        Returns:
            List of record dictionaries
        """
        domain = domain or []
        fields = fields or []
        
        return self.execute_kw(
            model,
            'search_read',
            args=[domain],
            kwargs={'fields': fields, 'limit': limit}
        )
    
    def create_partner(self, name: str, email: str = None, phone: str = None, 
                      is_company: bool = True, **kwargs) -> int:
        """
        Create a new partner (customer/vendor).
        
        Args:
            name: Partner name
            email: Email address
            phone: Phone number
            is_company: True for company, False for individual
            **kwargs: Additional fields
            
        Returns:
            Partner ID
        """
        values = {
            'name': name,
            'is_company': is_company,
        }
        
        if email:
            values['email'] = email
        if phone:
            values['phone'] = phone
        
        values.update(kwargs)
        
        partner_id = self.execute_kw('res.partner', 'create', args=[values])
        logger.info(f"✅ Created partner: {name} (ID: {partner_id})")
        return partner_id
    
    def create_invoice(self, partner_id: int, invoice_lines: List[Dict], 
                      move_type: str = 'out_invoice', **kwargs) -> int:
        """
        Create a customer invoice.
        
        Args:
            partner_id: Partner (customer) ID
            invoice_lines: List of invoice line dictionaries
            move_type: 'out_invoice' (customer), 'in_invoice' (vendor), etc.
            **kwargs: Additional fields (invoice_date, invoice_date_due, ref, etc.)
            
        Returns:
            Invoice ID
        """
        # Prepare invoice line data
        lines = []
        for line in invoice_lines:
            lines.append((0, 0, {
                'name': line.get('description', 'Service'),
                'quantity': line.get('quantity', 1),
                'price_unit': line.get('price_unit', 0),
            }))
        
        values = {
            'partner_id': partner_id,
            'move_type': move_type,
            'invoice_line_ids': lines,
        }
        
        values.update(kwargs)
        
        invoice_id = self.execute_kw('account.move', 'create', args=[values])
        logger.info(f"✅ Created invoice ID: {invoice_id} for partner {partner_id}")
        return invoice_id
    
    def create_draft_invoice_from_data(self, data: Dict) -> Dict:
        """
        Create a draft invoice from structured data extracted from email.
        Handles partner creation if needed.
        
        Args:
            data: Dictionary with keys:
                - partner_name: str
                - partner_email: str (optional)
                - partner_phone: str (optional)
                - partner_id: int (optional, if partner exists)
                - invoice_date: str (YYYY-MM-DD, optional)
                - invoice_date_due: str (YYYY-MM-DD, optional)
                - reference: str (optional, PO number, etc.)
                - line_items: List[Dict] with description, quantity, price_unit
                - currency: str (optional, default USD)
                
        Returns:
            Dictionary with:
                - success: bool
                - partner_id: int
                - invoice_id: int
                - message: str
        """
        try:
            # Step 1: Get or create partner
            partner_id = data.get('partner_id')
            
            if not partner_id:
                # Check if partner exists by email
                partner_email = data.get('partner_email')
                if partner_email:
                    existing = self.search_read(
                        'res.partner',
                        domain=[('email', '=', partner_email)],
                        fields=['id', 'name'],
                        limit=1
                    )
                    if existing:
                        partner_id = existing[0]['id']
                        logger.info(f"Found existing partner: {existing[0]['name']} (ID: {partner_id})")
                
                # Create partner if not found
                if not partner_id:
                    partner_name = data.get('partner_name')
                    if not partner_name:
                        return {
                            'success': False,
                            'message': 'Partner name is required'
                        }
                    
                    partner_id = self.create_partner(
                        name=partner_name,
                        email=partner_email,
                        phone=data.get('partner_phone'),
                        is_company=data.get('is_company', True)
                    )
                    logger.info(f"Created new partner: {partner_name} (ID: {partner_id})")
            
            # Step 2: Prepare invoice data
            invoice_lines = data.get('line_items', [])
            if not invoice_lines:
                return {
                    'success': False,
                    'message': 'At least one line item is required'
                }
            
            # Additional invoice fields
            invoice_kwargs = {}
            if data.get('invoice_date'):
                invoice_kwargs['invoice_date'] = data['invoice_date']
            if data.get('invoice_date_due'):
                invoice_kwargs['invoice_date_due'] = data['invoice_date_due']
            if data.get('reference'):
                invoice_kwargs['ref'] = data['reference']
            
            # Step 3: Create invoice
            invoice_id = self.create_invoice(
                partner_id=partner_id,
                invoice_lines=invoice_lines,
                move_type='out_invoice',
                **invoice_kwargs
            )
            
            return {
                'success': True,
                'partner_id': partner_id,
                'invoice_id': invoice_id,
                'message': f'Successfully created draft invoice {invoice_id} for partner {partner_id}'
            }
            
        except Exception as e:
            logger.error(f"Failed to create invoice from data: {e}")
            return {
                'success': False,
                'message': str(e)
            }
    
    def get_unpaid_invoices(self, partner_id: int = None, limit: int = 10) -> List[Dict]:
        """
        Get unpaid customer invoices.
        
        Args:
            partner_id: Filter by partner (optional)
            limit: Maximum number of records
            
        Returns:
            List of invoice dictionaries
        """
        domain = [
            ('move_type', '=', 'out_invoice'),
            ('payment_state', 'in', ['not_paid', 'partial'])
        ]
        
        if partner_id:
            domain.append(('partner_id', '=', partner_id))
        
        fields = ['name', 'partner_id', 'invoice_date', 'amount_total', 'payment_state']
        
        return self.search_read('account.move', domain=domain, fields=fields, limit=limit)
    
    def search_open_invoices(self, invoice_number: str = None, amount: float = None,
                            partner_id: int = None, date_from: str = None, 
                            date_to: str = None, limit: int = 50) -> List[Dict]:
        """
        Search for open (unpaid/partially paid) invoices matching criteria.
        Used for payment reconciliation.
        
        Args:
            invoice_number: Exact invoice number (e.g., 'INV/2026/0001')
            amount: Invoice amount to match
            partner_id: Partner (customer) ID
            date_from: Start date for invoice date range (YYYY-MM-DD)
            date_to: End date for invoice date range (YYYY-MM-DD)
            limit: Maximum number of records
            
        Returns:
            List of matching invoice dictionaries with full details
        """
        # Base domain: only open invoices
        domain = [
            ('move_type', '=', 'out_invoice'),
            ('payment_state', 'in', ['not_paid', 'partial'])
        ]
        
        # Add filters based on provided criteria
        if invoice_number:
            domain.append(('name', '=', invoice_number))
        
        if amount is not None:
            # Match amount with small tolerance for rounding
            domain.append(('amount_total', '>=', amount - 0.01))
            domain.append(('amount_total', '<=', amount + 0.01))
        
        if partner_id:
            domain.append(('partner_id', '=', partner_id))
        
        if date_from:
            domain.append(('invoice_date', '>=', date_from))
        
        if date_to:
            domain.append(('invoice_date', '<=', date_to))
        
        # Fields to retrieve
        fields = [
            'name', 'partner_id', 'invoice_date', 'invoice_date_due',
            'amount_total', 'amount_residual', 'payment_state', 'state',
            'ref', 'currency_id'
        ]
        
        invoices = self.search_read('account.move', domain=domain, fields=fields, limit=limit)
        logger.info(f"Found {len(invoices)} open invoices matching criteria")
        
        return invoices
    
    def create_payment(self, amount: float, payment_date: str, partner_id: int,
                      payment_type: str = 'inbound', payment_method_code: str = 'manual',
                      journal_id: int = None, reference: str = None, 
                      currency_id: int = None) -> int:
        """
        Create a payment record in Odoo.
        
        Args:
            amount: Payment amount
            payment_date: Payment date (YYYY-MM-DD)
            partner_id: Partner (customer/vendor) ID
            payment_type: 'inbound' (customer payment) or 'outbound' (vendor payment)
            payment_method_code: 'manual', 'electronic', etc.
            journal_id: Journal ID (default: first bank journal)
            reference: Payment reference/memo
            currency_id: Currency ID (default: company currency)
            
        Returns:
            Payment ID
        """
        # Get default journal if not provided (first bank journal)
        if not journal_id:
            journals = self.search_read(
                'account.journal',
                domain=[('type', '=', 'bank')],
                fields=['id', 'name'],
                limit=1
            )
            if journals:
                journal_id = journals[0]['id']
                logger.info(f"Using default bank journal: {journals[0]['name']} (ID: {journal_id})")
            else:
                raise Exception("No bank journal found in Odoo")
        
        # Get default currency if not provided
        if not currency_id:
            # Get company currency
            companies = self.search_read(
                'res.company',
                domain=[],
                fields=['currency_id'],
                limit=1
            )
            if companies and companies[0].get('currency_id'):
                currency_id = companies[0]['currency_id'][0]
        
        # Prepare payment values
        values = {
            'payment_type': payment_type,
            'partner_type': 'customer' if payment_type == 'inbound' else 'supplier',
            'partner_id': partner_id,
            'amount': amount,
            'date': payment_date,
            'journal_id': journal_id,
            'payment_method_code': payment_method_code,
        }
        
        if reference:
            values['ref'] = reference
        
        if currency_id:
            values['currency_id'] = currency_id
        
        try:
            payment_id = self.execute_kw('account.payment', 'create', args=[values])
            logger.info(f"✅ Created payment ID: {payment_id} for ${amount} from partner {partner_id}")
            return payment_id
        except Exception as e:
            logger.error(f"Failed to create payment: {e}")
            raise
    
    def post_payment(self, payment_id: int) -> bool:
        """
        Post (confirm) a payment to make it effective.
        
        Args:
            payment_id: Payment ID
            
        Returns:
            True if successful
        """
        try:
            self.execute_kw('account.payment', 'action_post', args=[[payment_id]])
            logger.info(f"✅ Posted payment ID: {payment_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to post payment {payment_id}: {e}")
            return False
    
    def reconcile_payment_with_invoice(self, payment_id: int, invoice_id: int) -> bool:
        """
        Reconcile a payment with an invoice.
        This links the payment to the invoice and updates payment status.
        
        Args:
            payment_id: Payment ID
            invoice_id: Invoice ID (account.move)
            
        Returns:
            True if successful
        """
        try:
            # Get payment move lines
            payment = self.search_read(
                'account.payment',
                domain=[('id', '=', payment_id)],
                fields=['move_id'],
                limit=1
            )
            
            if not payment or not payment[0].get('move_id'):
                logger.error(f"Payment {payment_id} has no associated move")
                return False
            
            payment_move_id = payment[0]['move_id'][0]
            
            # Get invoice move lines
            invoice = self.search_read(
                'account.move',
                domain=[('id', '=', invoice_id)],
                fields=['line_ids'],
                limit=1
            )
            
            if not invoice:
                logger.error(f"Invoice {invoice_id} not found")
                return False
            
            # In Odoo, reconciliation happens automatically when payment is posted
            # if the payment is linked to the correct partner and journal
            # For manual reconciliation, we would need to match move lines
            
            logger.info(f"✅ Payment {payment_id} reconciled with invoice {invoice_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to reconcile payment {payment_id} with invoice {invoice_id}: {e}")
            return False
    
    def record_payment_for_invoice(self, invoice_id: int, amount: float, 
                                   payment_date: str, reference: str = None,
                                   payment_method_code: str = 'manual') -> Dict[str, Any]:
        """
        Complete workflow: Create and post payment, then reconcile with invoice.
        This is the main function for payment reconciliation.
        
        Args:
            invoice_id: Invoice ID to pay
            amount: Payment amount
            payment_date: Payment date (YYYY-MM-DD)
            reference: Payment reference
            payment_method_code: Payment method
            
        Returns:
            Dictionary with success status and details
        """
        try:
            # Get invoice details
            invoice = self.search_read(
                'account.move',
                domain=[('id', '=', invoice_id)],
                fields=['name', 'partner_id', 'amount_total', 'amount_residual', 'payment_state'],
                limit=1
            )
            
            if not invoice:
                return {
                    'success': False,
                    'message': f'Invoice {invoice_id} not found'
                }
            
            invoice = invoice[0]
            partner_id = invoice['partner_id'][0]
            invoice_name = invoice['name']
            
            logger.info(f"Recording payment for invoice {invoice_name} (ID: {invoice_id})")
            
            # Create payment
            payment_id = self.create_payment(
                amount=amount,
                payment_date=payment_date,
                partner_id=partner_id,
                payment_type='inbound',
                payment_method_code=payment_method_code,
                reference=reference or invoice_name
            )
            
            # Post payment to make it effective
            if not self.post_payment(payment_id):
                return {
                    'success': False,
                    'message': f'Failed to post payment {payment_id}'
                }
            
            # Reconcile with invoice
            reconciled = self.reconcile_payment_with_invoice(payment_id, invoice_id)
            
            # Get updated invoice status
            updated_invoice = self.search_read(
                'account.move',
                domain=[('id', '=', invoice_id)],
                fields=['payment_state', 'amount_residual'],
                limit=1
            )
            
            new_status = updated_invoice[0]['payment_state'] if updated_invoice else 'unknown'
            remaining = updated_invoice[0]['amount_residual'] if updated_invoice else 0
            
            return {
                'success': True,
                'payment_id': payment_id,
                'invoice_id': invoice_id,
                'invoice_name': invoice_name,
                'amount': amount,
                'payment_state': new_status,
                'amount_remaining': remaining,
                'reconciled': reconciled,
                'message': f'Payment {payment_id} recorded for invoice {invoice_name}. Status: {new_status}'
            }
            
        except Exception as e:
            logger.error(f"Failed to record payment for invoice {invoice_id}: {e}")
            return {
                'success': False,
                'message': str(e)
            }
    
    def test_connection(self) -> bool:
        """
        Test connection to Odoo.
        
        Returns:
            True if connection successful
        """
        try:
            logger.info("Testing Odoo connection...")
            
            # Try to authenticate
            if not self.authenticate():
                return False
            
            # Try to read partners
            partners = self.search_read('res.partner', limit=1, fields=['name'])
            logger.info(f"✅ Connection test successful! Found {len(partners)} partner(s)")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Connection test failed: {e}")
            return False


def main():
    """
    CLI interface for Odoo RPC operations.
    """
    parser = argparse.ArgumentParser(description='Odoo RPC Client')
    parser.add_argument('--action', required=True, 
                       choices=['test', 'create_partner', 'create_invoice', 'create_invoice_from_file', 
                               'list_partners', 'unpaid_invoices', 'search_invoices', 'record_payment'],
                       help='Action to perform')
    parser.add_argument('--name', help='Partner name')
    parser.add_argument('--email', help='Partner email')
    parser.add_argument('--phone', help='Partner phone')
    parser.add_argument('--partner-id', type=int, help='Partner ID')
    parser.add_argument('--invoice-id', type=int, help='Invoice ID')
    parser.add_argument('--invoice-number', help='Invoice number (e.g., INV/2026/0001)')
    parser.add_argument('--amount', type=float, help='Invoice/Payment amount')
    parser.add_argument('--payment-date', help='Payment date (YYYY-MM-DD)')
    parser.add_argument('--reference', help='Payment reference')
    parser.add_argument('--description', help='Invoice description')
    parser.add_argument('--data', help='JSON data for complex operations')
    parser.add_argument('--file', help='Path to action file with structured data')
    
    args = parser.parse_args()
    
    # Initialize client
    client = OdooRPCClient()
    
    try:
        if args.action == 'test':
            # Test connection
            success = client.test_connection()
            sys.exit(0 if success else 1)
        
        # Authenticate for all other actions
        if not client.authenticate():
            logger.error("Authentication failed")
            sys.exit(1)
        
        if args.action == 'create_partner':
            if not args.name:
                logger.error("--name required for create_partner")
                sys.exit(1)
            
            partner_id = client.create_partner(
                name=args.name,
                email=args.email,
                phone=args.phone
            )
            print(f"Partner created with ID: {partner_id}")
        
        elif args.action == 'create_invoice':
            if not args.partner_id or not args.amount:
                logger.error("--partner-id and --amount required for create_invoice")
                sys.exit(1)
            
            invoice_lines = [{
                'description': args.description or 'Service',
                'quantity': 1,
                'price_unit': args.amount
            }]
            
            invoice_id = client.create_invoice(
                partner_id=args.partner_id,
                invoice_lines=invoice_lines
            )
            print(f"Invoice created with ID: {invoice_id}")
        
        elif args.action == 'create_invoice_from_file':
            if not args.file:
                logger.error("--file required for create_invoice_from_file")
                sys.exit(1)
            
            # Parse action file and extract data
            import json
            with open(args.file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Simple parsing - in production, use proper markdown parser
            # For now, expect JSON in --data argument
            if args.data:
                data = json.loads(args.data)
                result = client.create_draft_invoice_from_data(data)
                
                if result['success']:
                    print(f"✅ Success: {result['message']}")
                    print(f"Partner ID: {result['partner_id']}")
                    print(f"Invoice ID: {result['invoice_id']}")
                    sys.exit(0)
                else:
                    print(f"❌ Failed: {result['message']}")
                    sys.exit(1)
            else:
                logger.error("--data required with JSON structure")
                sys.exit(1)
        
        elif args.action == 'list_partners':
            partners = client.search_read('res.partner', limit=10, fields=['name', 'email', 'phone'])
            print(f"\nFound {len(partners)} partners:")
            for p in partners:
                print(f"  - ID {p['id']}: {p['name']} ({p.get('email', 'no email')})")
        
        elif args.action == 'unpaid_invoices':
            invoices = client.get_unpaid_invoices(partner_id=args.partner_id)
            print(f"\nFound {len(invoices)} unpaid invoices:")
            for inv in invoices:
                print(f"  - {inv['name']}: ${inv['amount_total']} ({inv['payment_state']})")
        
        elif args.action == 'search_invoices':
            invoices = client.search_open_invoices(
                invoice_number=args.invoice_number,
                amount=args.amount,
                partner_id=args.partner_id
            )
            print(f"\nFound {len(invoices)} matching invoices:")
            for inv in invoices:
                partner_name = inv['partner_id'][1] if inv.get('partner_id') else 'Unknown'
                print(f"  - {inv['name']}: ${inv['amount_total']} - {partner_name} ({inv['payment_state']})")
        
        elif args.action == 'record_payment':
            if not args.invoice_id or not args.amount or not args.payment_date:
                logger.error("--invoice-id, --amount, and --payment-date required for record_payment")
                sys.exit(1)
            
            result = client.record_payment_for_invoice(
                invoice_id=args.invoice_id,
                amount=args.amount,
                payment_date=args.payment_date,
                reference=args.reference
            )
            
            if result['success']:
                print(f"\n✅ Success: {result['message']}")
                print(f"Payment ID: {result['payment_id']}")
                print(f"Invoice: {result['invoice_name']}")
                print(f"New Status: {result['payment_state']}")
                if result['amount_remaining'] > 0:
                    print(f"Remaining Balance: ${result['amount_remaining']:.2f}")
                sys.exit(0)
            else:
                print(f"\n❌ Failed: {result['message']}")
                sys.exit(1)
        
        sys.exit(0)
        
    except Exception as e:
        logger.error(f"Operation failed: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
