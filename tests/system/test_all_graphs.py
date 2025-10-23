"""Test all graphs in langgraph.json can be imported."""

import sys

# Test all agent graphs
test_imports = {
    'development': [
        'agents.development.requirements_analyst',
        'agents.development.architecture_designer',
        'agents.development.code_generator',
        'agents.development.code_reviewer',
        'agents.development.test_generator',
        'agents.development.documentation_generator',
    ],
    'security': [
        'agents.security.security_analyst',
    ],
    'rag': [
        'agents.rag.quality_assurance_agent',
        'agents.rag.query_analyst_agent',
        'agents.rag.re_ranker_agent',
        'agents.rag.retrieval_specialist_agent',
        'agents.rag.web_scraping_specialist_agent',
        'agents.rag.writer_agent',
    ],
    'research': [
        'agents.research.comprehensive_research_agent',
        'agents.research.content_parser_agent',
        'agents.research.query_planner_agent',
        'agents.research.synthesis_agent',
        'agents.research.verification_agent',
        'agents.research.web_search_agent',
        'agents.research.web_research_swarm',
    ],
    'management': [
        'agents.management.self_optimizing_validation_agent',
    ],
    'supervisor': [
        'agents.supervisor.base_supervisor',
    ],
    'mcp': [
        'agents.mcp.mcp_enhanced_agent',
    ],
    'swarm': [
        'agents.swarm.swarm_coordinator',
    ],
}

errors = []
success = 0
total = 0

for category, modules in test_imports.items():
    for module_path in modules:
        total += 1
        try:
            mod = __import__(module_path, fromlist=['graph'])
            if hasattr(mod, 'graph'):
                # Allow None for abstract classes
                if mod.graph is None and 'base_supervisor' not in module_path:
                    errors.append(f"{module_path}: graph is None")
                else:
                    success += 1
                    print(f"OK: {module_path}")
            else:
                errors.append(f"{module_path}: No graph attribute")
        except Exception as e:
            errors.append(f"{module_path}: {type(e).__name__}: {str(e)[:100]}")

print(f"\n{'='*60}")
print(f"Results: {success}/{total} graphs loaded successfully")
print(f"{'='*60}")

if errors:
    print(f"\nErrors ({len(errors)}):")
    for error in errors:
        print(f"  - {error}")
    sys.exit(1)
else:
    print("\nAll graphs loaded successfully!")
    sys.exit(0)

