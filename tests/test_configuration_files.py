#!/usr/bin/env python3
"""
Test suite for configuration files and agent definitions.
Validates JSON schemas, YAML frontmatter, and file structure.
"""

import json
import sys
from pathlib import Path

# Use ASCII-safe symbols for Windows compatibility
PASS_SYMBOL = "[OK]"
FAIL_SYMBOL = "[XX]"


def test_pre_commit_validator_json():
    """Test 1: Validate pre-commit-validator.json structure"""
    print("\n[TEST 1] Pre-Commit Validator JSON Structure")
    print("-" * 50)
    
    json_file = Path(".github/hooks/pre-commit-validator.json")
    
    if not json_file.exists():
        print(f"{FAIL_SYMBOL} File not found: {json_file}")
        return False
    
    try:
        with open(json_file) as f:
            config = json.load(f)
        
        # Validate required structure
        checks = [
            ("hooks" in config, "Root 'hooks' key exists"),
            ("PreToolUse" in config.get("hooks", {}), "PreToolUse hook defined"),
            (isinstance(config["hooks"]["PreToolUse"], list), "PreToolUse is a list"),
            (len(config["hooks"]["PreToolUse"]) > 0, "PreToolUse has at least one entry"),
        ]
        
        first_hook = config["hooks"]["PreToolUse"][0] if config["hooks"]["PreToolUse"] else {}
        checks.extend([
            ("type" in first_hook, "Hook has 'type' field"),
            ("command" in first_hook, "Hook has 'command' field"),
            ("cwd" in first_hook, "Hook has 'cwd' field"),
            ("timeout" in first_hook, "Hook has 'timeout' field"),
            (first_hook.get("timeout", 0) > 0, "Timeout is positive"),
        ])
        
        passed = sum(1 for check, _ in checks if check)
        for check, desc in checks:
            symbol = PASS_SYMBOL if check else FAIL_SYMBOL
            print(f"{symbol} {desc}")
        
        if passed == len(checks):
            print(f"{PASS_SYMBOL} JSON structure validated")
            return True
        else:
            print(f"{FAIL_SYMBOL} {len(checks) - passed} validation(s) failed")
            return False
            
    except json.JSONDecodeError as e:
        print(f"{FAIL_SYMBOL} Invalid JSON: {e}")
        return False
    except Exception as e:
        print(f"{FAIL_SYMBOL} Error: {e}")
        return False


def test_agent_files_structure():
    """Test 2: Validate agent definition files"""
    print("\n[TEST 2] Agent Definition Files Structure")
    print("-" * 50)
    
    agent_files = [
        ".github/agents/analista-financiero.agent.md",
        ".github/agents/q-a-tester.agent.md",
    ]
    
    all_valid = True
    
    for agent_file in agent_files:
        file_path = Path(agent_file)
        
        if not file_path.exists():
            print(f"{FAIL_SYMBOL} {agent_file} - File not found")
            all_valid = False
            continue
        
        try:
            content = file_path.read_text(encoding='utf-8')
            
            # Check YAML frontmatter
            if not content.startswith("---"):
                print(f"{FAIL_SYMBOL} {agent_file} - Missing YAML frontmatter start")
                all_valid = False
                continue
            
            # Find closing ---
            parts = content.split("---", 2)
            if len(parts) < 3:
                print(f"{FAIL_SYMBOL} {agent_file} - Invalid YAML frontmatter (missing closing ---)")
                all_valid = False
                continue
            
            frontmatter = parts[1]
            body = parts[2]
            
            # Check frontmatter contains required fields
            frontmatter_checks = [
                ("description:" in frontmatter, "description field"),
                ("model:" in frontmatter, "model field"),
            ]
            
            # Check body has content
            body_checks = [
                (len(body.strip()) > 0, "Body has content"),
                ("#" in body, "Body has markdown headers"),
            ]
            
            file_valid = True
            for check, desc in frontmatter_checks + body_checks:
                if not check:
                    print(f"  {FAIL_SYMBOL} {agent_file} - Missing {desc}")
                    file_valid = False
            
            if file_valid:
                print(f"{PASS_SYMBOL} {agent_file}")
            else:
                all_valid = False
                
        except Exception as e:
            print(f"{FAIL_SYMBOL} {agent_file} - Error: {e}")
            all_valid = False
    
    return all_valid


def test_instructions_files():
    """Test 3: Validate instruction files"""
    print("\n[TEST 3] Instruction Files Structure")
    print("-" * 50)
    
    instruction_files = [
        ".github/instructions/branch-protection.instructions.md",
        ".github/instructions/no-emojis.instructions.md",
        ".github/instructions/test-location.instructions.md",
    ]
    
    all_valid = True
    
    for inst_file in instruction_files:
        file_path = Path(inst_file)
        
        if not file_path.exists():
            print(f"{FAIL_SYMBOL} {inst_file} - File not found")
            all_valid = False
            continue
        
        try:
            content = file_path.read_text(encoding='utf-8')
            
            # Check YAML frontmatter
            if not content.startswith("---"):
                print(f"{FAIL_SYMBOL} {inst_file} - Missing YAML frontmatter start")
                all_valid = False
                continue
            
            # Find closing ---
            parts = content.split("---", 2)
            if len(parts) < 3:
                print(f"{FAIL_SYMBOL} {inst_file} - Invalid YAML frontmatter")
                all_valid = False
                continue
            
            frontmatter = parts[1]
            body = parts[2]
            
            # Check for applyTo field
            if "applyTo:" not in frontmatter:
                print(f"{FAIL_SYMBOL} {inst_file} - Missing 'applyTo' field")
                all_valid = False
                continue
            
            # Check body has content
            if len(body.strip()) < 20:
                print(f"{FAIL_SYMBOL} {inst_file} - Body too short or empty")
                all_valid = False
                continue
            
            print(f"{PASS_SYMBOL} {inst_file}")
            
        except Exception as e:
            print(f"{FAIL_SYMBOL} {inst_file} - Error: {e}")
            all_valid = False
    
    return all_valid


def test_hooks_readme():
    """Test 4: Validate hooks README"""
    print("\n[TEST 4] Hooks README Documentation")
    print("-" * 50)
    
    readme_file = Path(".github/hooks/README.md")
    
    if not readme_file.exists():
        print(f"{FAIL_SYMBOL} File not found: {readme_file}")
        return False
    
    try:
        content = readme_file.read_text(encoding='utf-8')
        
        checks = [
            (len(content) > 100, "README has substantial content"),
            ("#" in content, "README has markdown headers"),
            ("hook" in content.lower(), "README mentions hooks"),
            ("pre-commit" in content.lower(), "README mentions pre-commit"),
        ]
        
        passed = sum(1 for check, _ in checks if check)
        for check, desc in checks:
            symbol = PASS_SYMBOL if check else FAIL_SYMBOL
            print(f"{symbol} {desc}")
        
        return passed == len(checks)
        
    except Exception as e:
        print(f"{FAIL_SYMBOL} Error: {e}")
        return False


def main():
    """Run all tests"""
    print("=" * 60)
    print("CONFIGURATION FILES TEST SUITE")
    print("=" * 60)
    
    tests = [
        ("Pre-Commit Validator JSON", test_pre_commit_validator_json),
        ("Agent Definition Files", test_agent_files_structure),
        ("Instruction Files", test_instructions_files),
        ("Hooks README", test_hooks_readme),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            passed = test_func()
            results.append((test_name, passed))
        except Exception as e:
            print(f"\n{FAIL_SYMBOL} ERROR in {test_name}: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)
    
    for test_name, passed in results:
        status = "PASS" if passed else "FAIL"
        symbol = PASS_SYMBOL if passed else FAIL_SYMBOL
        print(f"{symbol} {test_name}: {status}")
    
    print(f"\nTotal: {passed_count}/{total_count} test groups passed")
    
    if passed_count == total_count:
        print(f"\n{PASS_SYMBOL} All configuration files validated successfully!")
        return 0
    else:
        print(f"\n{FAIL_SYMBOL} {total_count - passed_count} test group(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())

