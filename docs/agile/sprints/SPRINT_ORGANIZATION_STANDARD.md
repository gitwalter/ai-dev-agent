# Sprint Directory Organization Standard

## Purpose
Define and enforce consistent organization across all sprint directories to ensure maintainability, findability, and clarity.

## Standard Sprint Directory Structure

```
sprints/
├── current_sprint.md              # Pointer/dashboard to active sprint
├── README.md                      # Overview of sprint system
├── templates/                     # Reusable sprint templates
│   ├── sprint_backlog_template.md
│   ├── sprint_planning_template.md
│   ├── sprint_progress_template.md
│   ├── sprint_retrospective_template.md
│   └── sprint_review_template.md
│
└── sprint_N/                      # Individual sprint directories
    ├── README.md                  # Sprint overview and quick reference
    ├── planning/                  # Sprint planning artifacts
    │   ├── sprint_N_planning.md
    │   ├── sprint_N_goals.md
    │   └── capacity_planning.md
    │
    ├── execution/                 # Active sprint work
    │   ├── backlog.md            # Sprint backlog
    │   ├── progress.md           # Daily progress tracking
    │   └── blockers.md           # Active blockers and impediments
    │
    ├── user_stories/             # User story documents
    │   ├── US-XXX-YYY.md         # Individual user stories
    │   └── ...
    │
    ├── tasks/                    # Technical tasks
    │   ├── task_name.md
    │   └── ...
    │
    ├── daily_standups/           # Daily standup notes
    │   ├── standup_YYYY-MM-DD.md
    │   └── ...
    │
    ├── review/                   # Sprint review artifacts
    │   ├── sprint_N_review.md
    │   └── demo_notes.md
    │
    ├── retrospective/            # Sprint retrospective
    │   ├── sprint_N_retrospective.md
    │   └── action_items.md
    │
    ├── metrics/                  # Sprint metrics and analytics
    │   ├── sprint_N_metrics.md
    │   └── velocity_analysis.md
    │
    ├── analysis/                 # Technical analysis documents
    │   ├── architecture_decisions.md
    │   └── research_findings.md
    │
    ├── completion/               # Sprint completion artifacts
    │   ├── sprint_N_closure.md
    │   ├── completion_summaries/
    │   └── final_status.md
    │
    └── archive/                  # Archived/historical content
        └── ...
```

## Organizational Principles

### 1. Consistent Naming Conventions
- **Sprint directories**: `sprint_N` (lowercase, underscore)
- **User stories**: `US-EPIC-NNN.md` or `US-CATEGORY-NNN.md`
- **Tasks**: `descriptive_task_name.md` (lowercase, underscores)
- **Daily standups**: `standup_YYYY-MM-DD.md`
- **Artifacts**: `sprint_N_artifact_type.md`

### 2. File Placement Rules
- **Planning docs** → `planning/`
- **Active work** → `execution/`
- **User stories** → `user_stories/`
- **Daily updates** → `daily_standups/`
- **Retrospectives** → `retrospective/`
- **Reviews** → `review/`
- **Metrics** → `metrics/`
- **Analysis** → `analysis/`
- **Completion** → `completion/`
- **Old content** → `archive/`

### 3. Lifecycle Management
- **Active Sprint**: Current sprint uses `execution/` for live work
- **Sprint Closure**: Move final artifacts to `completion/`
- **Historical Sprint**: Entire sprint becomes read-only archive
- **Backup Files**: Never commit .backup_* files - use git history

### 4. Link Management
- **Always use relative paths** from docs/agile/sprints/
- **Example**: `../../core/agile_cursor_rules.md`
- **Run link healing** before moving files
- **Update `current_sprint.md`** when sprint changes

## Migration Plan

### Phase 1: Cleanup (Current)
1. Remove all `.backup_*` files
2. Identify and move misplaced files
3. Create missing subdirectories
4. Standardize file naming

### Phase 2: Standardization
1. Apply consistent structure to all sprints
2. Update README.md in each sprint
3. Consolidate similar artifacts
4. Move archived content appropriately

### Phase 3: Link Healing
1. Run link healing system
2. Fix broken references to old `current/` directory
3. Update all inter-sprint links
4. Validate all documentation links

### Phase 4: Documentation
1. Update sprint READMEs
2. Document organization standards
3. Create navigation aids
4. Update agile cursor rules

## Enforcement

### Automation
- File organization enforcement rule (active)
- Pre-commit hooks validate structure
- Link healing system prevents broken links

### Manual Reviews
- Sprint planning checklist includes structure validation
- Sprint closure includes organization check
- Monthly audit of sprint directory organization

## Current Sprint Organization Issues

### Identified Problems (2025-10-10)
1. ✅ Redundant `current/` and `sprint_current/` directories (RESOLVED)
2. 🔄 Backup files (*.backup_*) committed to repository
3. 🔄 Inconsistent subdirectory structure across sprints
4. 🔄 Files directly in sprint roots that should be in subdirectories
5. 🔄 1293 broken links (many to old `current/` directory)
6. 🔄 Multiple retrospective/review files in some sprints
7. 🔄 Inconsistent naming conventions

### Priority Actions
1. **HIGH**: Remove all .backup_* files
2. **HIGH**: Fix broken links to `current/` directory
3. **MEDIUM**: Standardize subdirectory structure
4. **MEDIUM**: Move misplaced root-level files
5. **LOW**: Consolidate duplicate artifacts

## Success Criteria
- ✅ Zero .backup_* files in repository
- ✅ Zero broken links in sprints directory
- ✅ All sprints follow standard structure
- ✅ All files in correct subdirectories
- ✅ Link healing system validates clean

## References
- Current Sprint: `current_sprint.md`
- Agile Rules: `../../core/agile_cursor_rules.md`
- Link Healing: `../../../scripts/link_healing_system.py`
- File Organization Rule: `../../../.cursor/rules/core/file_organization_enforcement.mdc`

