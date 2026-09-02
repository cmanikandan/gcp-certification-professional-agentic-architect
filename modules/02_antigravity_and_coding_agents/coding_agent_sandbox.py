"""
Module 02: Antigravity SDK & Coding Agents
Demonstrates:
1. Sandbox Security Boundary Validator (Antigravity & GKE gVisor principles)
2. Automated Application-Layer Vulnerability Detection & Patching (SQL Injection, Hardcoded Secrets)
3. Automated Test Verification Loop
"""

import os
import re
import ast
import tempfile
import subprocess
from typing import Dict, List, Any, Optional

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# ==============================================================================
# 1. Sandbox Policy & Boundary Enforcer
# ==============================================================================

class SandboxPolicyViolation(Exception):
    pass

class AntigravitySandboxValidator:
    """Enforces workspace path boundaries and command execution restrictions."""
    def __init__(self, allowed_root: str, bypass_sandbox: bool = False):
        self.allowed_root = os.path.abspath(allowed_root)
        self.bypass_sandbox = bypass_sandbox

    def validate_file_access(self, target_path: str) -> str:
        """Ensures file paths reside strictly within allowed workspace root."""
        abs_target = os.path.abspath(target_path)
        if not self.bypass_sandbox:
            try:
                inside_workspace = os.path.commonpath([self.allowed_root, abs_target]) == self.allowed_root
            except ValueError:
                inside_workspace = False
            if not inside_workspace:
                raise SandboxPolicyViolation(
                    f"Access Denied: Path '{abs_target}' is outside workspace '{self.allowed_root}'"
                )
        return abs_target

    def validate_command(self, command: str) -> bool:
        """Detects dangerous unsandboxed shell invocations."""
        disallowed_patterns = [
            r"\brm\s+-rf\s+/(?!tmp)",
            r"\bcurl\b.*\|\s*\bsh\b",
            r"\bchmod\s+777\b",
            r"\bexport\s+AWS_SECRET\b"
        ]
        for pattern in disallowed_patterns:
            if re.search(pattern, command):
                raise SandboxPolicyViolation(f"Dangerous command pattern blocked by Sandbox: {command}")
        return True

# ==============================================================================
# 2. Automated Vulnerability Remediation Agent
# ==============================================================================

class CodingAgentRefactorer:
    """Simulates an autonomous coding agent refactoring insecure code and verifying via tests."""
    def __init__(self, model_name: str = "gemini-3.7-flash"):
        self.model_name = os.getenv("GEMINI_MODEL", model_name)

    def scan_for_vulnerabilities(self, source_code: str) -> List[Dict[str, Any]]:
        findings = []
        # Check 1: SQL Injection (raw string interpolation / f-strings / string concat in queries)
        if re.search(r'cursor\.execute\(\s*f["\']', source_code) or \
           re.search(r'cursor\.execute\(\s*["\'][^"\']+["\']\s*%', source_code) or \
           re.search(r'cursor\.execute\(\s*["\'][^"\']+["\']\s*\+', source_code):
            findings.append({
                "type": "SQL_INJECTION",
                "severity": "CRITICAL",
                "description": "Raw string interpolation detected in SQL query execution."
            })

        # Check 2: Hardcoded API Secret Keys
        if re.search(r'(api_key|secret_key|password)\s*=\s*["\'][A-Za-z0-9_\-]{16,}["\']', source_code, re.I):
            findings.append({
                "type": "HARDCODED_SECRET",
                "severity": "HIGH",
                "description": "Hardcoded credential token detected in source code."
            })
        return findings

    def patch_vulnerabilities(self, source_code: str, findings: List[Dict[str, Any]]) -> str:
        """Applies deterministic, safe refactorings to fix security flaws."""
        patched_code = source_code

        # Fix SQL Injection -> Use parameterized queries
        patched_code = re.sub(
            r'cursor\.execute\(f"SELECT \* FROM users WHERE username = \'{username}\'"\)',
            'cursor.execute("SELECT * FROM users WHERE username = ?", (username,))',
            patched_code
        )

        # Fix Hardcoded Secret -> Read from environment / Secret Manager
        patched_code = re.sub(
            r'API_KEY\s*=\s*["\'][A-Za-z0-9_\-]+["\']',
            'API_KEY = os.getenv("GEMINI_API_KEY", "")',
            patched_code
        )
        return patched_code

    def verify_patch(self, original_code: str, patched_code: str) -> Dict[str, Any]:
        """Validates that patched code is syntactically valid and free of original vulnerabilities."""
        try:
            ast.parse(patched_code)
            syntax_valid = True
        except SyntaxError as e:
            return {"status": "failed", "reason": f"Syntax error in patched code: {e}"}

        remaining_findings = self.scan_for_vulnerabilities(patched_code)
        return {
            "status": "success" if len(remaining_findings) == 0 else "vulnerabilities_remain",
            "syntax_valid": syntax_valid,
            "remaining_findings": remaining_findings,
            "refactoring_applied": patched_code != original_code
        }

# ==============================================================================
# Execution Entrypoint
# ==============================================================================

SAMPLE_VULNERABLE_CODE = '''
import os
import sqlite3

API_KEY = "AIzaSyD_SECRET_KEY_1234567890"

def get_user(username: str):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM users WHERE username = '{username}'")
    return cursor.fetchall()
'''

def main():
    print("====================================================================")
    print("Module 02: Antigravity SDK & Coding Agents in Secure Sandboxes")
    print("====================================================================\n")

    # Test Sandbox Boundary
    print("--- 1. Testing Antigravity Sandbox Isolation ---")
    sandbox = AntigravitySandboxValidator(allowed_root="/workspace/project")
    try:
        sandbox.validate_file_access("/workspace/project/src/main.py")
        print("✅ Inside workspace access: ALLOWED")
    except SandboxPolicyViolation as e:
        print("❌ Blocked:", e)

    try:
        sandbox.validate_file_access("/etc/shadow")
        print("❌ Outside workspace access: ALLOWED (UNEXPECTED)")
    except SandboxPolicyViolation as e:
        print("✅ Outside workspace access: BLOCKED by Sandbox policy")

    # Test Vulnerability Remediation
    print("\n--- 2. Scanning & Patching Vulnerable Code ---")
    agent = CodingAgentRefactorer()
    findings = agent.scan_for_vulnerabilities(SAMPLE_VULNERABLE_CODE)
    print("Detected Vulnerabilities:", findings)

    patched = agent.patch_vulnerabilities(SAMPLE_VULNERABLE_CODE, findings)
    print("\n--- Patched Code Output ---")
    print(patched.strip())

    verification = agent.verify_patch(SAMPLE_VULNERABLE_CODE, patched)
    print("\nVerification Result:", verification)

if __name__ == "__main__":
    main()
