from pathlib import Path
from config import PlatinumConfig

c = PlatinumConfig()
print(f'Vault path: {c.vault_path}')
print(f'Absolute: {c.vault_path.absolute()}')

scan_path = c.vault_path / 'Needs_Action' / 'email'
print(f'Scan path: {scan_path}')
print(f'Exists: {scan_path.exists()}')
print(f'JSON Files: {list(scan_path.glob("*.json"))}')
print(f'MD Files: {list(scan_path.glob("*.md"))}')
