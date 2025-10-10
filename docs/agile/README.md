# Agile Documentation

**Last Updated**: 2025-10-10
**Status**: ✅ Organized and Clean

## Quick Navigation

### Active Work
- **Daily Standup**: [`daily_standup.md`](./daily_standup.md)
- **Current Sprint**: [`sprints/current_sprint.md`](./sprints/current_sprint.md)

### Core Documentation
- **Overview**: [`overview/`](./overview/) - System overview and manuals
- **Core Rules**: [`core/`](./core/) - Agile rules and workflows
- **Catalogs**: [`catalogs/`](./catalogs/) - Tracking catalogs (stories, epics, tasks)

### Sprint Work
- **Sprints**: [`sprints/`](./sprints/) - All sprint documentation
- **User Stories**: [`user_stories/`](./user_stories/) - Cross-sprint user stories
- **Epics**: [`epics/`](./epics/) - Epic definitions
- **Backlog**: [`backlog/`](./backlog/) - Product backlog items

### Planning & Execution
- **Planning**: [`planning/`](./planning/) - Planning artifacts
- **Execution**: [`execution/`](./execution/) - Execution tracking
- **Metrics**: [`metrics/`](./metrics/) - Metrics and velocity tracking

### Team & Process
- **Teams**: [`teams/`](./teams/) - Team structures and staffing
- **Frameworks**: [`frameworks/`](./frameworks/) - Agile frameworks
- **Retrospectives**: [`retrospectives/`](./retrospectives/) - Cross-sprint retrospectives
- **Lessons Learned**: [`lessons_learned/`](./lessons_learned/) - Lessons and improvements

### System Support
- **Templates**: [`templates/`](./templates/) - Templates for artifacts
- **Automation**: [`automation/`](./automation/) - Automation systems
- **Validation**: [`validation/`](./validation/) - Validation reports
- **Analysis**: [`analysis/`](./analysis/) - Analysis and strategy

### Tracking
- **Achievements**: [`achievements/`](./achievements/) - Achievement tracking
- **Health**: [`health/`](./health/) - Project health assessments
- **Compliance**: [`compliance/`](./compliance/) - Compliance audits

## Organization Standards
- **Sprint Organization**: [`sprints/SPRINT_ORGANIZATION_STANDARD.md`](./sprints/SPRINT_ORGANIZATION_STANDARD.md)
- **Agile Directory Organization**: [`AGILE_DIRECTORY_ORGANIZATION_STANDARD.md`](./AGILE_DIRECTORY_ORGANIZATION_STANDARD.md)

## Key Principles
1. **Clean Root**: Only README.md and daily_standup.md in root
2. **Organized Subdirectories**: Everything in its proper place
3. **No Backup Files**: Use git history, not .backup_* files
4. **Link Integrity**: Automated link healing for file moves
5. **Current Only**: Remove obsolete/historical noise

## Getting Started
1. Check [`daily_standup.md`](./daily_standup.md) for today's focus
2. Review [`sprints/current_sprint.md`](./sprints/current_sprint.md) for active sprint
3. Check [`catalogs/USER_STORY_CATALOG.md`](./catalogs/USER_STORY_CATALOG.md) for stories
4. Review [`core/agile_cursor_rules.md`](./core/agile_cursor_rules.md) for commands

## Maintenance
- Run `python scripts/cleanup_agile_directory.py` for cleanup
- Run `python scripts/link_healing_system.py` for link validation
- Run `python scripts/organize_sprints_directory.py` for sprint organization

Last cleanup: 2025-10-10
