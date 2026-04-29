# Skill 21: Security Isolation

## Purpose

Enforces strict security boundaries between Cloud and Local zones. Ensures secrets never leak to Cloud, validates environment configurations, and prevents unauthorized operations.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│           Security Isolation Layer                       │
│         (Validates all operations)                       │
└─────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  Cloud Zone  │    │   Secrets    │    │  Local Zone  │
│              │    │   Vault      │    │              │
│ ❌ No SMTP   │    │              │    │ ✅ Full      │
│ ❌ No WhatsApp│   │ (Protected)  │    │    Access    │
│ ❌ No Banking│    │              │    │              │
│ ✅ Read-only │    │              │    │ ✅ Write     │
└──────────────┘    └──────────────┘    └──────────────┘
```

---

## When to Use

- **Always**: Security validation runs on every operation
- **Startup**: Validate environment before starting agents
- **File access**: Validate before reading/writing files
- **API calls**: Validate before calling external services
- **Sync**: Validate before syncing Vault

## When NOT to Use

- Never bypass security checks
- Never disable validation in production

---

## Security Zones

### Cloud Zone (Restricted)

**Allowed Secrets:**
```env
# Cloud .env (read-only credentials)
ODOO_URL=https://cloud-odoo.example.com
ODOO_READONLY_USER=readonly_user
ODOO_READONLY_PASS=readonly_pass
OPENAI_API_KEY=sk-cloud-key
```

**Forbidden Secrets:**
```env
# NEVER in Cloud .env
SMTP_USER=...
SMTP_PASS=...
WHATSAPP_SESSION_PATH=...
BANKING_API_KEY=...
PAYMENT_TOKEN=...
LINKEDIN_SESSION=...
FACEBOOK_SESSION=...
```

### Local Zone (Full Access)

**Allowed Secrets:**
```env
# Local .env (full credentials)
SMTP_USER=user@example.com
SMTP_PASS=app_password
ODOO_URL=http://localhost:8069
ODOO_USERNAME=admin
ODOO_PASSWORD=admin_pass
WHATSAPP_SESSION_PATH=/local/whatsapp_session/
BANKING_API_KEY=bank_key_123
PAYMENT_TOKEN=pay_token_456
LINKEDIN_SESSION=/local/linkedin_session/
FACEBOOK_SESSION=/local/facebook_session/
OPENAI_API_KEY=sk-local-key
```

---

## Environment Validation

### Cloud Environment Validator

```python
import os
import logging
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)

class CloudEnvironmentValidator:
    """
    Validates Cloud environment has no forbidden secrets.
    """
    
    ALLOWED_VARS = [
        'ODOO_URL',
        'ODOO_READONLY_USER',
        'ODOO_READONLY_PASS',
        'OPENAI_API_KEY',
        'VAULT_PATH',
        'LOG_LEVEL'
    ]
    
    FORBIDDEN_VARS = [
        'SMTP_USER',
        'SMTP_PASS',
        'SMTP_SERVER',
        'SMTP_PORT',
        'WHATSAPP_SESSION',
        'WHATSAPP_SESSION_PATH',
        'BANKING_API_KEY',
        'BANKING_CREDS',
        'PAYMENT_TOKEN',
        'PAYMENT_API_KEY',
        'LINKEDIN_SESSION',
        'FACEBOOK_SESSION',
        'TWITTER_SESSION'
    ]
    
    def validate(self) -> Tuple[bool, List[str]]:
        """
        Validate Cloud environment.
        
        Returns:
            (is_valid, violations)
        """
        violations = []
        
        # 1. Check for forbidden variables
        for var in self.FORBIDDEN_VARS:
            if os.getenv(var):
                violations.append(f"Forbidden secret in Cloud: {var}")
        
        # 2. Check Odoo user is read-only
        odoo_user = os.getenv('ODOO_READONLY_USER', '')
        if odoo_user and not odoo_user.startswith('readonly_'):
            violations.append(f"Odoo user must be read-only: {odoo_user}")
        
        # 3. Check required variables exist
        required = ['ODOO_URL', 'ODOO_READONLY_USER', 'ODOO_READONLY_PASS']
        for var in required:
            if not os.getenv(var):
                violations.append(f"Missing required variable: {var}")
        
        is_valid = len(violations) == 0
        
        if is_valid:
            logger.info("✅ Cloud environment validated")
        else:
            logger.error(f"❌ Cloud environment validation failed: {violations}")
        
        return is_valid, violations
```

### Local Environment Validator

```python
class LocalEnvironmentValidator:
    """
    Validates Local environment has all required secrets.
    """
    
    REQUIRED_VARS = [
        'SMTP_USER',
        'SMTP_PASS',
        'ODOO_URL',
        'ODOO_USERNAME',
        'ODOO_PASSWORD',
        'OPENAI_API_KEY'
    ]
    
    OPTIONAL_VARS = [
        'WHATSAPP_SESSION_PATH',
        'BANKING_API_KEY',
        'PAYMENT_TOKEN',
        'LINKEDIN_SESSION',
        'FACEBOOK_SESSION'
    ]
    
    def validate(self) -> Tuple[bool, List[str]]:
        """
        Validate Local environment.
        
        Returns:
            (is_valid, violations)
        """
        violations = []
        
        # 1. Check required variables exist
        for var in self.REQUIRED_VARS:
            if not os.getenv(var):
                violations.append(f"Missing required variable: {var}")
        
        # 2. Validate SMTP credentials
        smtp_user = os.getenv('SMTP_USER', '')
        if smtp_user and '@' not in smtp_user:
            violations.append(f"Invalid SMTP_USER format: {smtp_user}")
        
        # 3. Validate Odoo credentials
        odoo_user = os.getenv('ODOO_USERNAME', '')
        if odoo_user == 'readonly_user':
            violations.append("Local must use full Odoo access, not readonly")
        
        is_valid = len(violations) == 0
        
        if is_valid:
            logger.info("✅ Local environment validated")
        else:
            logger.error(f"❌ Local environment validation failed: {violations}")
        
        return is_valid, violations
```

---

## File Access Control

### Cloud File Access Validator

```python
import fnmatch
from pathlib import Path

class CloudFileAccessValidator:
    """
    Validates Cloud agent can only access allowed files.
    """
    
    ALLOWED_PATHS = [
        'Vault/Needs_Action/**/*',
        'Vault/Plans/**/*',
        'Vault/Pending_Approval/**/*',
        'Vault/In_Progress/cloud/**/*',
        'Vault/Updates/**/*',
        'Vault/Signals/**/*',
        'Vault/Briefings/**/*',
        'Vault/Done/**/*',
        'Logs/cloud/**/*'
    ]
    
    FORBIDDEN_PATHS = [
        '*.env',
        '.env.*',
        '*_secrets.json',
        'credentials.json',
        'tokens/**/*',
        '*_session/**/*',
        '*.session',
        'banking_creds/**/*',
        'payment_tokens/**/*',
        'Dashboard.md',
        'local_state.json',
        'Vault/In_Progress/local/**/*',  # Local's working directory
        'Logs/local/**/*'
    ]
    
    def validate_read(self, filepath: str) -> Tuple[bool, str]:
        """
        Validate Cloud can read file.
        
        Returns:
            (is_allowed, reason)
        """
        # Check forbidden patterns
        for pattern in self.FORBIDDEN_PATHS:
            if fnmatch.fnmatch(filepath, pattern):
                return False, f"Cloud cannot read forbidden file: {filepath}"
        
        # Check allowed patterns
        for pattern in self.ALLOWED_PATHS:
            if fnmatch.fnmatch(filepath, pattern):
                return True, "Allowed"
        
        # Default deny
        return False, f"Cloud can only access Vault/: {filepath}"
    
    def validate_write(self, filepath: str) -> Tuple[bool, str]:
        """
        Validate Cloud can write file.
        
        Returns:
            (is_allowed, reason)
        """
        # Cloud cannot write to In_Progress/local/
        if 'In_Progress/local/' in filepath:
            return False, "Cloud cannot write to Local's working directory"
        
        # Cloud cannot write to Done/ (only move)
        if filepath.startswith('Vault/Done/') and not filepath.endswith('.md'):
            return False, "Cloud can only move tasks to Done/"
        
        # Otherwise same as read validation
        return self.validate_read(filepath)
```

### Local File Access Validator

```python
class LocalFileAccessValidator:
    """
    Validates Local agent file access.
    """
    
    READONLY_PATHS = [
        'Vault/In_Progress/cloud/**/*',  # Cloud's working directory
    ]
    
    def validate_read(self, filepath: str) -> Tuple[bool, str]:
        """
        Validate Local can read file.
        
        Local has full read access.
        """
        return True, "Local has full read access"
    
    def validate_write(self, filepath: str) -> Tuple[bool, str]:
        """
        Validate Local can write file.
        
        Returns:
            (is_allowed, reason)
        """
        # Local cannot write to Cloud's working directory
        for pattern in self.READONLY_PATHS:
            if fnmatch.fnmatch(filepath, pattern):
                return False, f"Local cannot write to Cloud's working directory: {filepath}"
        
        # Otherwise full access
        return True, "Allowed"
```

---

## Operation Validation

### Cloud Operation Validator

```python
class CloudOperationValidator:
    """
    Validates Cloud agent operations.
    """
    
    ALLOWED_OPERATIONS = [
        'read',
        'draft',
        'analyze',
        'extract',
        'match',
        'generate',
        'triage',
        'classify'
    ]
    
    FORBIDDEN_OPERATIONS = [
        'send',
        'post',
        'execute',
        'payment',
        'write_odoo',
        'delete',
        'whatsapp',
        'banking'
    ]
    
    def validate_operation(self, operation: str) -> Tuple[bool, str]:
        """
        Validate Cloud can perform operation.
        
        Returns:
            (is_allowed, reason)
        """
        if operation in self.FORBIDDEN_OPERATIONS:
            return False, f"Cloud cannot perform: {operation}"
        
        if operation in self.ALLOWED_OPERATIONS:
            return True, "Allowed"
        
        # Default deny
        return False, f"Unknown operation: {operation}"
    
    def validate_email_send(self) -> Tuple[bool, str]:
        """Cloud cannot send emails."""
        return False, "Cloud cannot send emails - Local only"
    
    def validate_social_post(self) -> Tuple[bool, str]:
        """Cloud cannot post to social media."""
        return False, "Cloud cannot post to social media - Local only"
    
    def validate_odoo_write(self) -> Tuple[bool, str]:
        """Cloud cannot write to Odoo."""
        return False, "Cloud cannot write to Odoo - Local only"
    
    def validate_payment_execute(self) -> Tuple[bool, str]:
        """Cloud cannot execute payments."""
        return False, "Cloud cannot execute payments - Local only"
```

### Local Operation Validator

```python
class LocalOperationValidator:
    """
    Validates Local agent operations.
    """
    
    ALLOWED_OPERATIONS = [
        'send',
        'post',
        'execute',
        'payment',
        'write_odoo',
        'approve',
        'whatsapp',
        'banking',
        'dashboard_update'
    ]
    
    DISCOURAGED_OPERATIONS = [
        'draft',  # Cloud should do this
        'triage',  # Cloud should do this
        'analyze'  # Cloud should do this
    ]
    
    def validate_operation(self, operation: str) -> Tuple[bool, str]:
        """
        Validate Local can perform operation.
        
        Returns:
            (is_allowed, reason)
        """
        if operation in self.ALLOWED_OPERATIONS:
            return True, "Allowed"
        
        if operation in self.DISCOURAGED_OPERATIONS:
            return True, f"Warning: {operation} should be done by Cloud"
        
        # Local has full access
        return True, "Local has full access"
```

---

## API Access Control

### Odoo Access Control

```python
class OdooAccessControl:
    """
    Controls Odoo access based on zone.
    """
    
    @staticmethod
    def get_cloud_client():
        """
        Get Odoo client for Cloud (read-only).
        """
        from gold_tier.actions import OdooRPCClient
        
        # Validate environment
        validator = CloudEnvironmentValidator()
        is_valid, violations = validator.validate()
        
        if not is_valid:
            raise SecurityError(f"Cloud environment invalid: {violations}")
        
        # Create read-only client
        client = OdooRPCClient()
        client.username = os.getenv('ODOO_READONLY_USER')
        client.password = os.getenv('ODOO_READONLY_PASS')
        
        # Validate read-only
        if not client.username.startswith('readonly_'):
            raise SecurityError("Cloud must use readonly Odoo user")
        
        logger.info("✅ Cloud Odoo client (read-only)")
        return client
    
    @staticmethod
    def get_local_client():
        """
        Get Odoo client for Local (full access).
        """
        from gold_tier.actions import OdooRPCClient
        
        # Validate environment
        validator = LocalEnvironmentValidator()
        is_valid, violations = validator.validate()
        
        if not is_valid:
            raise SecurityError(f"Local environment invalid: {violations}")
        
        # Create full-access client
        client = OdooRPCClient()
        client.username = os.getenv('ODOO_USERNAME')
        client.password = os.getenv('ODOO_PASSWORD')
        
        logger.info("✅ Local Odoo client (full access)")
        return client
```

### SMTP Access Control

```python
class SMTPAccessControl:
    """
    Controls SMTP access (Local only).
    """
    
    @staticmethod
    def get_cloud_client():
        """
        Cloud cannot access SMTP.
        """
        raise SecurityError("Cloud cannot access SMTP - Local only")
    
    @staticmethod
    def get_local_client():
        """
        Get SMTP client for Local.
        """
        from gold_tier.actions import EmailSender
        
        # Validate environment
        validator = LocalEnvironmentValidator()
        is_valid, violations = validator.validate()
        
        if not is_valid:
            raise SecurityError(f"Local environment invalid: {violations}")
        
        # Create SMTP client
        sender = EmailSender()
        
        logger.info("✅ Local SMTP client")
        return sender
```

---

## Secret Scanning

### Scan for Secrets

```python
import re

class SecretScanner:
    """
    Scans files for accidentally exposed secrets.
    """
    
    SECRET_PATTERNS = {
        'password': r'password\s*[=:]\s*["\']([^"\']+)["\']',
        'api_key': r'api[_-]?key\s*[=:]\s*["\']([^"\']+)["\']',
        'token': r'token\s*[=:]\s*["\']([^"\']+)["\']',
        'secret': r'secret\s*[=:]\s*["\']([^"\']+)["\']',
        'openai_key': r'sk-[a-zA-Z0-9]{32,}',
        'github_token': r'ghp_[a-zA-Z0-9]{36}',
        'aws_key': r'AKIA[0-9A-Z]{16}',
        'private_key': r'-----BEGIN (RSA |)PRIVATE KEY-----'
    }
    
    def scan_file(self, filepath: str) -> List[Dict]:
        """
        Scan file for secrets.
        
        Returns:
            List of violations
        """
        violations = []
        
        try:
            with open(filepath, 'r') as f:
                content = f.read()
            
            for secret_type, pattern in self.SECRET_PATTERNS.items():
                matches = re.findall(pattern, content, re.IGNORECASE)
                
                if matches:
                    violations.append({
                        'file': filepath,
                        'type': secret_type,
                        'matches': len(matches)
                    })
        
        except Exception as e:
            logger.error(f"Error scanning {filepath}: {e}")
        
        return violations
    
    def scan_directory(self, dirpath: str) -> List[Dict]:
        """
        Scan directory for secrets.
        
        Returns:
            List of violations
        """
        all_violations = []
        
        for root, dirs, files in os.walk(dirpath):
            # Skip .git
            if '.git' in dirs:
                dirs.remove('.git')
            
            for file in files:
                if file.endswith(('.md', '.json', '.txt', '.py')):
                    filepath = os.path.join(root, file)
                    violations = self.scan_file(filepath)
                    all_violations.extend(violations)
        
        return all_violations
```

### Pre-Commit Hook

```python
def pre_commit_secret_scan():
    """
    Scan staged files for secrets before commit.
    """
    scanner = SecretScanner()
    
    # Get staged files
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only"],
        capture_output=True,
        text=True
    )
    
    staged_files = result.stdout.strip().split('\n')
    
    violations = []
    for filepath in staged_files:
        if os.path.exists(filepath):
            file_violations = scanner.scan_file(filepath)
            violations.extend(file_violations)
    
    if violations:
        logger.error(f"❌ Secrets detected in staged files: {violations}")
        print("\n⚠️  COMMIT BLOCKED: Secrets detected!")
        print("Please remove secrets before committing.\n")
        for v in violations:
            print(f"  - {v['file']}: {v['type']} ({v['matches']} matches)")
        return False
    
    logger.info("✅ No secrets detected in staged files")
    return True
```

---

## Audit Logging

### Security Audit Logger

```python
class SecurityAuditLogger:
    """
    Logs all security-relevant events.
    """
    
    def __init__(self, zone: str):
        self.zone = zone
        self.log_file = f"Logs/{zone}/security_audit.log"
    
    def log_access(self, operation: str, resource: str, allowed: bool, reason: str):
        """
        Log access attempt.
        """
        entry = {
            'timestamp': datetime.now().isoformat(),
            'zone': self.zone,
            'operation': operation,
            'resource': resource,
            'allowed': allowed,
            'reason': reason
        }
        
        with open(self.log_file, 'a') as f:
            f.write(json.dumps(entry) + '\n')
        
        if not allowed:
            logger.warning(f"⚠️ Access denied: {operation} on {resource} - {reason}")
    
    def log_secret_access(self, secret_name: str, allowed: bool):
        """
        Log secret access attempt.
        """
        self.log_access('secret_access', secret_name, allowed, 
                       'Allowed' if allowed else 'Forbidden in this zone')
    
    def log_file_access(self, filepath: str, operation: str, allowed: bool, reason: str):
        """
        Log file access attempt.
        """
        self.log_access(f'file_{operation}', filepath, allowed, reason)
```

---

## Startup Validation

### Cloud Startup

```python
def validate_cloud_startup():
    """
    Validate Cloud environment on startup.
    """
    logger.info("Validating Cloud startup...")
    
    # 1. Validate environment
    env_validator = CloudEnvironmentValidator()
    is_valid, violations = env_validator.validate()
    
    if not is_valid:
        logger.error(f"❌ Cloud startup failed: {violations}")
        raise SecurityError(f"Cloud environment invalid: {violations}")
    
    # 2. Validate .gitignore
    from platinum_tier.skills import VaultSyncManager
    sync_manager = VaultSyncManager()
    
    if not sync_manager.validate_gitignore():
        raise SecurityError(".gitignore validation failed")
    
    # 3. Scan for secrets
    scanner = SecretScanner()
    violations = scanner.scan_directory("Vault/")
    
    if violations:
        logger.error(f"❌ Secrets found in Vault: {violations}")
        raise SecurityError(f"Secrets detected in Vault: {violations}")
    
    # 4. Test Odoo connection (read-only)
    try:
        odoo_client = OdooAccessControl.get_cloud_client()
        if not odoo_client.test_connection():
            raise SecurityError("Odoo connection failed")
    except Exception as e:
        raise SecurityError(f"Odoo validation failed: {e}")
    
    logger.info("✅ Cloud startup validated")
    return True
```

### Local Startup

```python
def validate_local_startup():
    """
    Validate Local environment on startup.
    """
    logger.info("Validating Local startup...")
    
    # 1. Validate environment
    env_validator = LocalEnvironmentValidator()
    is_valid, violations = env_validator.validate()
    
    if not is_valid:
        logger.error(f"❌ Local startup failed: {violations}")
        raise SecurityError(f"Local environment invalid: {violations}")
    
    # 2. Test SMTP connection
    try:
        smtp_client = SMTPAccessControl.get_local_client()
        # Test connection (don't send email)
    except Exception as e:
        logger.warning(f"⚠️ SMTP validation failed: {e}")
    
    # 3. Test Odoo connection (full access)
    try:
        odoo_client = OdooAccessControl.get_local_client()
        if not odoo_client.test_connection():
            raise SecurityError("Odoo connection failed")
    except Exception as e:
        raise SecurityError(f"Odoo validation failed: {e}")
    
    # 4. Check WhatsApp session (optional)
    whatsapp_session = os.getenv('WHATSAPP_SESSION_PATH')
    if whatsapp_session and not os.path.exists(whatsapp_session):
        logger.warning(f"⚠️ WhatsApp session not found: {whatsapp_session}")
    
    logger.info("✅ Local startup validated")
    return True
```

---

## Testing

### Test Cloud Restrictions

```python
def test_cloud_restrictions():
    """
    Test that Cloud cannot access forbidden resources.
    """
    validator = CloudOperationValidator()
    
    # Test forbidden operations
    assert not validator.validate_email_send()[0]
    assert not validator.validate_social_post()[0]
    assert not validator.validate_odoo_write()[0]
    assert not validator.validate_payment_execute()[0]
    
    # Test allowed operations
    assert validator.validate_operation('draft')[0]
    assert validator.validate_operation('analyze')[0]
    
    print("✅ Cloud restrictions test passed")
```

### Test Local Access

```python
def test_local_access():
    """
    Test that Local has full access.
    """
    validator = LocalOperationValidator()
    
    # Test all operations allowed
    assert validator.validate_operation('send')[0]
    assert validator.validate_operation('post')[0]
    assert validator.validate_operation('execute')[0]
    assert validator.validate_operation('payment')[0]
    
    print("✅ Local access test passed")
```

---

## Success Indicators

✅ Cloud cannot access forbidden secrets  
✅ Local has all required secrets  
✅ File access control enforced  
✅ Operation validation working  
✅ No secrets in Git repository  
✅ Audit logging complete  
✅ Startup validation passes  
✅ Security tests pass  

---

**Skill Status:** ✅ Active  
**Last Updated:** 2026-04-13  
**Owner:** Platinum Tier Security  
**Dependencies:** All Platinum Tier skills  
**Safety Level:** 🔴 CRITICAL (Core security)  
**Critical:** YES (Protects entire system)
