# Agile Directory Organization Standard

## Purpose
Define and enforce consistent organization for the entire agile documentation system.

## Organizational Issues Identified (2025-10-10)

### Current Problems
1. **Too Many Root Files**: 15+ documentation files directly in root
2. **Backup Files**: 6 .backup_* files in subdirectories
3. **Unclear Categorization**: Hard to find specific documentation
4. **Redundant Summaries**: Multiple overview/summary files
5. **Inconsistent Naming**: Mix of CAPS and lowercase files

## Standard Agile Directory Structure

```
docs/agile/
├── README.md                          # Main agile system overview
├── daily_standup.md                   # Active daily standup (root for quick access)
│
├── overview/                          # High-level documentation
│   ├── AGILE_OVERVIEW.md
│   ├── COMPREHENSIVE_AGILE_MANUAL.md
│   ├── HOW_TO_WORK_WITH_AGILE.md
│   ├── META_DOCUMENTATION_INDEX.md
│   ├── ORGANIZATION_SUMMARY.md
│   ├── comprehensive_user_stories_overview.md
│   └── AGILE_IMPLEMENTATION_SUMMARY.md
│
├── core/                              # Core agile rules and systems
│   ├── agile_cursor_rules.md
│   ├── agile_meeting_rules.md
│   ├── agile_workflow.md
│   ├── AGILE_COORDINATION_SYSTEM.md
│   ├── AGILE_KEYWORD_SYSTEM.md
│   ├── definition_of_done.md
│   └── ...
│
├── sprints/                           # Sprint-specific documentation
│   ├── current_sprint.md
│   ├── README.md
│   ├── SPRINT_ORGANIZATION_STANDARD.md
│   ├── sprint_0/
│   ├── sprint_1/
│   └── ...
│
├── catalogs/                          # Tracking catalogs
│   ├── USER_STORY_CATALOG.md
│   ├── EPIC_CATALOG.md
│   ├── TASK_CATALOG.md
│   ├── CURRENT_BACKLOG.md
│   ├── SPRINT_SUMMARY.md
│   └── CROSS_SPRINT_TRACKING.md
│
├── epics/                             # Epic definitions
│   ├── EPIC_CATALOG.md
│   ├── epic-0-*.md
│   └── ...
│
├── user_stories/                      # Cross-sprint user stories
│   ├── US-*.md
│   └── completion/                    # Completed user stories
│
├── backlog/                           # Product backlog items
│   └── ...
│
├── planning/                          # Planning artifacts
│   ├── product_backlog.md
│   ├── epic-breakdown.md
│   └── ...
│
├── execution/                         # Execution tracking
│   ├── velocity_tracking.md
│   ├── continuous_integration.md
│   ├── blocker_resolution_report.md
│   └── ...
│
├── metrics/                           # Metrics and analytics
│   ├── metrics_dashboard.md
│   ├── velocity_tracking_current.md
│   ├── cross_sprint_velocity_analysis.md
│   ├── performance_indicators.md
│   ├── quality_gates.md
│   └── SPEED_OPTIMIZATION_SUMMARY.md
│
├── achievements/                      # Achievement tracking
│   ├── SYSTEMATIC_EXCELLENCE_ACHIEVEMENTS.md
│   ├── CURRENT_SPRINT_ACHIEVEMENTS_SUMMARY.md
│   └── ...
│
├── retrospectives/                    # Cross-sprint retrospectives
│   └── ...
│
├── lessons_learned/                   # Lessons learned
│   └── ...
│
├── teams/                             # Team structures
│   ├── EXPERT_TEAM_STAFFING_FRAMEWORK.md
│   └── ...
│
├── frameworks/                        # Framework definitions
│   ├── SPEED_OPTIMIZED_AGILE_FRAMEWORK.md
│   └── ...
│
├── automation/                        # Automation systems
│   ├── AUTOMATION_SYSTEM_OVERVIEW.md
│   ├── automation_framework.md
│   └── ...
│
├── templates/                         # Templates for artifacts
│   └── ...
│
├── validation/                        # Validation reports
│   ├── AUTOMATIC_ARTIFACT_MAINTENANCE_VALIDATION.md
│   └── ...
│
├── analysis/                          # Analysis and strategy
│   ├── LINK_ANALYSIS_REPORT.md
│   ├── NAMING_CONVENTION_CLEANUP_PLAN.md
│   └── ...
│
├── design/                            # Design documents
│   └── ...
│
├── compliance/                        # Compliance audits
│   └── ...
│
├── health/                            # Project health
│   └── ...
│
├── reports/                           # Various reports
│   └── ...
│
├── requirements/                      # Requirements docs
│   └── ...
│
├── rules/                             # Rule definitions
│   └── ...
│
└── strategy/                          # Strategic docs
    └── ...
```

## File Organization Rules

### 1. Root Directory
**Only These Files Allowed in Root:**
- `README.md` - Main agile system overview
- `daily_standup.md` - Active daily standup (quick access)

**Everything Else** must be in appropriate subdirectories.

### 2. Naming Conventions
- **Directories**: lowercase with underscores (`user_stories`, `lessons_learned`)
- **Files**: 
  - Framework/System docs: `CAPS_WITH_UNDERSCORES.md`
  - Working docs: `lowercase_with_underscores.md`
  - User stories: `US-CATEGORY-NNN.md`
  - Epics: `epic-N-descriptive-name.md`

### 3. File Placement by Type

| File Type | Target Directory |
|-----------|-----------------|
| Overview/Manual | `overview/` |
| Core system rules | `core/` |
| Sprint work | `sprints/sprint_N/` |
| User stories | `user_stories/` or `sprints/sprint_N/user_stories/` |
| Epics | `epics/` |
| Tracking catalogs | `catalogs/` |
| Metrics/Analytics | `metrics/` |
| Planning docs | `planning/` |
| Retrospectives | `retrospectives/` or `sprints/sprint_N/retrospective/` |
| Team structures | `teams/` |
| Frameworks | `frameworks/` |
| Automation | `automation/` |
| Templates | `templates/` |
| Validation | `validation/` |
| Analysis | `analysis/` |
| Lessons learned | `lessons_learned/` |
| Achievements | `achievements/` |

### 4. Backup File Policy
**NEVER commit .backup_* files**
- Use git history for backups
- Remove all .backup_* files from repository
- Configure .gitignore to exclude them

## Migration Plan

### Phase 1: Backup Cleanup
- [ ] Remove all .backup_* files from agile directory
- [ ] Update .gitignore to exclude *.backup_*

### Phase 2: Root File Organization
- [ ] Move overview files to `overview/`
- [ ] Move framework files to `frameworks/`
- [ ] Move team files to `teams/`
- [ ] Move automation files to `automation/`
- [ ] Move validation files to `validation/`
- [ ] Move metrics files to `metrics/`
- [ ] Move achievement files to `achievements/`

### Phase 3: Link Healing
- [ ] Run link healing system before moves
- [ ] Execute file moves with tracking
- [ ] Update all broken links
- [ ] Validate documentation links

### Phase 4: README Updates
- [ ] Update main README.md with new structure
- [ ] Add navigation guide
- [ ] Document organization standards
- [ ] Update agile cursor rules

## Files to Move (Identified)

### To `overview/`:
- AGILE_IMPLEMENTATION_SUMMARY.md
- AGILE_OVERVIEW.md
- COMPREHENSIVE_AGILE_MANUAL.md
- HOW_TO_WORK_WITH_AGILE.md
- META_DOCUMENTATION_INDEX.md
- ORGANIZATION_SUMMARY.md

### To `frameworks/`:
- SPEED_OPTIMIZED_AGILE_FRAMEWORK.md

### To `teams/`:
- EXPERT_TEAM_STAFFING_FRAMEWORK.md

### To `automation/`:
- AUTOMATION_SYSTEM_OVERVIEW.md

### To `validation/`:
- AUTOMATIC_ARTIFACT_MAINTENANCE_VALIDATION.md

### To `metrics/`:
- velocity_tracking_current.md
- SPEED_OPTIMIZATION_SUMMARY.md

### To `achievements/`:
- CURRENT_SPRINT_ACHIEVEMENTS_SUMMARY.md

### To `user_stories/completion/`:
- US-DOC-001_COMPLETION_SUMMARY.md

## Enforcement

### Automation
- File organization enforcement rule (active)
- Pre-commit hooks validate structure
- Link healing system prevents broken links
- Automated cleanup scripts

### Manual Reviews
- Monthly audit of agile directory organization
- Sprint retrospectives include organization check
- Code reviews check file placement

## Success Criteria
- ✅ Only README.md and daily_standup.md in root
- ✅ Zero .backup_* files in repository
- ✅ All files in correct subdirectories
- ✅ Zero broken links
- ✅ Clear navigation structure
- ✅ Consistent naming conventions

## References
- Sprint Organization: `sprints/SPRINT_ORGANIZATION_STANDARD.md`
- Link Healing: `../../scripts/link_healing_system.py`
- File Organization Rule: `../../.cursor/rules/core/file_organization_enforcement.mdc`
- Automation Enforcement: `../../.cursor/rules/enforcement/AUTOMATION_SCRIPT_ENFORCEMENT_RULE.mdc`

