# Sprint Documentation

This directory contains organized documentation for each sprint in the AI Development Agent project.

## Folder Structure

```
sprints/
├── README.md                    # This file - sprint documentation guide
├── templates/                   # Templates for creating new sprint folders
├── sprint_1/                    # Sprint 1 documentation
│   ├── backlog.md              # Sprint 1 backlog
│   ├── progress.md             # Sprint 1 progress tracking
│   ├── planning.md             # Sprint 1 planning documents
│   ├── review.md               # Sprint 1 review meeting notes
│   ├── retrospective.md        # Sprint 1 retrospective
│   └── daily_standups/         # Daily standup notes
├── sprint_2/                    # Sprint 2 documentation
│   └── (same structure as sprint_1)
└── sprint_N/                    # Future sprints follow same pattern
```

## Sprint Document Standards

Each sprint folder **MUST** contain the following documents:

### Core Documents
- **`backlog.md`** - Sprint backlog with user stories and tasks
- **`progress.md`** - Real-time progress tracking and status updates
- **`planning.md`** - Sprint planning meeting notes and decisions
- **`review.md`** - Sprint review meeting outcomes and demonstrations
- **`retrospective.md`** - Sprint retrospective insights and action items

### Supporting Documents
- **`daily_standups/`** - Daily standup meeting notes (optional but recommended)
- **`metrics.md`** - Sprint metrics and velocity tracking (if detailed)
- **`blockers.md`** - Active blockers and impediments tracking
- **`definition_of_done.md`** - Sprint-specific DoD criteria (if different from project)

## Document Naming Convention

### Required Format
- Use lowercase filenames with underscores for multi-word names
- Sprint folders: `sprint_N` where N is the sprint number
- Core documents: Use standard names listed above
- Daily standups: `YYYY-MM-DD.md` format in daily_standups/ folder

### Examples
```
✅ CORRECT:
- sprints/sprint_1/backlog.md
- sprints/sprint_2/daily_standups/2024-08-29.md
- sprints/sprint_3/retrospective.md

❌ INCORRECT:
- sprints/Sprint1/Backlog.md
- sprints/sprint_2/Daily Standup 29-08-2024.md
- sprints/sprint_3/retro.md
```

## Creating New Sprint Documentation

### Automated Creation
Use the sprint automation scripts to create new sprint folders:
```bash
python docs/agile/templates/sprint_planning/sprint_automation.py --create-sprint N
```

### Manual Creation
1. Copy the templates from `templates/` folder
2. Create new `sprint_N/` folder
3. Rename and customize template files
4. Update sprint-specific information

## Documentation Quality Standards

### Content Requirements
- **Real-time Updates**: All documents must reflect current status
- **Transparency**: All information must be visible to stakeholders
- **Accuracy**: Status and progress must be factual and verified
- **Completeness**: All sections of templates must be filled
- **Consistency**: Use standard terminology and formats

### Review Process
- Sprint documents reviewed in sprint planning
- Progress updates validated in daily standups
- Final review in sprint review and retrospective
- Continuous updates throughout sprint execution

## Integration with Agile Artifacts

### Product Backlog Integration
- Sprint backlogs reference product backlog items
- User story IDs maintained across all documents
- Acceptance criteria tracked from product to sprint level

### Velocity Tracking Integration
- Progress updates feed into velocity calculations
- Story points tracked consistently across documents
- Historical data maintained for trend analysis

### Definition of Done Integration
- All sprint work validated against project DoD
- Sprint-specific DoD criteria documented when applicable
- Completion status tracked in progress documents

## Automation and Tools

### Available Scripts
- **Sprint Creation**: Automated sprint folder and document creation
- **Progress Tracking**: Automated progress updates from development activity
- **Metrics Collection**: Automated velocity and burndown calculations
- **Report Generation**: Automated sprint review and retrospective reports

### Integration Points
- Git commit hooks update progress automatically
- CI/CD pipeline updates sprint status
- Development tools integrate with sprint tracking
- Quality gates enforce sprint completion criteria

## Archival and History

### Completed Sprints
- Keep all sprint documentation for historical reference
- Archive in same structure for future analysis
- Maintain links to deployment artifacts and releases
- Preserve lessons learned and improvement actions

### Sprint Retrospective Actions
- Track improvement actions across sprints
- Monitor implementation of retrospective commitments
- Maintain historical view of team growth and evolution
- Document process improvements and their effectiveness

## Compliance and Quality Assurance

### Agile Rule Compliance
This sprint documentation structure enforces:
- **Crystal Transparency Principle**: All work visible and tracked
- **Agile Artifact Maintenance**: Real-time updates and accuracy
- **Definition of Done Enforcement**: Proper completion validation
- **Sprint Goal Alignment**: All work tied to sprint objectives

### Quality Gates
- All documents must be complete before sprint closure
- Progress tracking must be current (updated within 24 hours)
- Retrospective actions must be documented and tracked
- Metrics must be calculated and validated

## Support and Resources

### Templates
- Use templates in `templates/` folder for consistent documentation
- Customize templates for project-specific needs
- Maintain template versioning for improvements

### Training and Guidelines
- Refer to agile development rules in `.cursor/rules/`
- Follow project documentation standards
- Consult with Scrum Master or Project Manager for guidance

### Tools and Integration
- Integrate with project management tools
- Use automation scripts for efficiency
- Leverage CI/CD integration for real-time updates

---

**Last Updated**: 2025-08-31  
**Version**: 1.0  
**Maintainer**: AI Development Agent Project Team
