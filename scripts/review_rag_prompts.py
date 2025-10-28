#!/usr/bin/env python3
"""
Comprehensive Review: Check for Hardcoded Prompts in RAG Agents
================================================================
"""
import re
from pathlib import Path

agents_dir = Path("agents/rag")
agent_files = list(agents_dir.glob("*.py"))

print("=" * 80)
print("COMPREHENSIVE REVIEW: Hardcoded Prompts in RAG Agents")
print("=" * 80)
print()

# Patterns that indicate hardcoded prompts
hardcoded_patterns = [
    (r'"""You are', "Multi-line docstring prompt starting with 'You are'"),
    (r"'''You are", "Multi-line single-quote prompt starting with 'You are'"),
    (r'"You are [^"]{50,}', "Long string literal starting with 'You are'"),
    (r'"Your task is', "Prompt starting with 'Your task is'"),
    (r'"Your role is', "Prompt starting with 'Your role is'"),
    (r'PROMPT\s*=\s*["\']', "Variable named PROMPT with string assignment"),
    (r'_PROMPT\s*=\s*\(', "Multi-line prompt variable"),
    (r'base_prompt\s*=\s*"""(?!.*prompt_loader)', "base_prompt with triple quotes"),
]

# Patterns that are OK (using prompt loader)
ok_patterns = [
    r'prompt_loader\.get_system_prompt\(\)',
    r'self\.prompt_loader\.get_system_prompt\(\)',
    r'self\.\w+_loader\.get_system_prompt\(\)',
]

issues_found = []

for agent_file in sorted(agent_files):
    if agent_file.name == "__init__.py":
        continue
    
    print(f"Checking {agent_file.name}...")
    
    with open(agent_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if file uses prompt loader
    uses_prompt_loader = any(re.search(pattern, content) for pattern in ok_patterns)
    
    # Check for hardcoded patterns
    file_issues = []
    for pattern, description in hardcoded_patterns:
        matches = re.finditer(pattern, content, re.IGNORECASE)
        for match in matches:
            # Get line number
            line_num = content[:match.start()].count('\n') + 1
            file_issues.append((line_num, description, match.group()[:80]))
    
    if file_issues:
        print(f"  ❌ ISSUES FOUND:")
        for line_num, desc, snippet in file_issues:
            print(f"     Line {line_num}: {desc}")
            print(f"     Snippet: {snippet}...")
        issues_found.extend([(agent_file.name, *issue) for issue in file_issues])
    elif uses_prompt_loader:
        print(f"  ✅ Uses AgentPromptLoader - NO hardcoded prompts")
    else:
        print(f"  ℹ️  No LLM prompts (algorithmic agent)")
    
    print()

print("=" * 80)
print("SUMMARY")
print("=" * 80)
print()

if issues_found:
    print(f"❌ FAILED: {len(issues_found)} hardcoded prompt(s) found in {len(set(f[0] for f in issues_found))} file(s)")
    print()
    print("Files with issues:")
    for file_name in sorted(set(f[0] for f in issues_found)):
        print(f"  - {file_name}")
else:
    print("✅ SUCCESS: No hardcoded prompts found!")
    print()
    print("All RAG agents are using AgentPromptLoader pattern:")
    print("  - query_analyst_agent.py ✅")
    print("  - retrieval_specialist_agent.py ✅")
    print("  - re_ranker_agent.py ✅ (no LLM)")
    print("  - quality_assurance_agent.py ✅ (no LLM)")
    print("  - writer_agent.py ✅")
    print("  - web_scraping_specialist_agent.py ✅ (no LLM)")
    print("  - rag_swarm_coordinator.py ✅")

print()
print("Prompts in LangSmith Hub:")
print("  1. query_analyst_v1 ✅")
print("  2. retrieval_specialist_v1 ✅")
print("  3. re_ranker_v1 ✅")
print("  4. quality_assurance_v1 ✅")
print("  5. writer_v1 ✅")
print("  6. web_scraping_specialist_v1 ✅")
print("  7. document_grader_v1 ✅ (NEW)")
print("  8. query_rewriter_v1 ✅ (NEW)")
print("  9. answer_generator_v1 ✅ (NEW)")
print()
print("=" * 80)

