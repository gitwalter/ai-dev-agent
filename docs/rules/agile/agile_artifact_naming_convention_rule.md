# Agile Artifact Naming Convention Rule

**CRITICAL**: All agile artifacts must follow strict, uniform naming conventions to ensure consistency, enable automation, and maintain professional standards.

## Core Principle

**"Consistency Enables Excellence"**

Every agile artifact must follow standardized naming patterns that are predictable, systematic, and enable reliable automation and navigation.

## Naming Convention Standards

### 1. **Epic Files**
**Format**: `epic-{topic}.md` (lowercase-with-hyphens)

```yaml
✅ CORRECT:
- epic-formal-principles.md
- epic-agent-development.md  
- epic-ui-excellence.md

❌ INCORRECT:
- EPIC-FORMAL-PRINCIPLES.md
- Epic_Formal_Principles.md
- epic_formal_principles.md
```

### 2. **User Story Files** 
**Format**: `US-{XXX}.md` (existing format - correct)

```yaml
✅ CORRECT:
- US-001.md
- US-028.md
- US-PE-01.md

❌ INCORRECT:
- us-001.md
- USER_STORY_001.md
- Story-001.md
```

### 3. **Sprint Files**
**Format**: `sprint_{N}_{type}.md` (lowercase_with_underscores)

```yaml
✅ CORRECT:
- sprint_1_summary.md
- sprint_2_retrospective.md
- sprint_1_completion_status.md

❌ INCORRECT:
- SPRINT_1_COMPLETION_REPORT.md
- Sprint1Summary.md
- sprint-1-summary.md
```

### 4. **Folder Names**
**Format**: `lowercase_with_underscores` (existing correct)

```yaml
✅ CORRECT:
- sprint_1/
- user_stories/
- daily_standups/

❌ INCORRECT:
- Sprint1/
- User-Stories/
- Daily_Standups/
```

### 5. **Catalog Files**
**Format**: `{type}_catalog.md` (lowercase_with_underscores)

```yaml
✅ CORRECT:
- user_story_catalog.md
- epic_overview.md
- task_catalog.md

❌ INCORRECT:
- USER_STORY_CATALOG.md
- Epic-Overview.md
- TaskCatalog.md
```

### 6. **Status and Report Files**
**Format**: `{component}_{identifier}_{type}.md`

```yaml
✅ CORRECT:
- sprint_1_completion_status.md
- us_028_progress_report.md
- epic_formal_principles_status.md

❌ INCORRECT:
- SPRINT_1_COMPLETION_REPORT.md
- US-028-Progress-Report.md
- Epic_Status_Report.md
```

## Rationale for Naming Decisions

### 1. **Consistency Over Convention**
- Single standard eliminates confusion
- Predictable patterns enable automation
- Professional appearance to stakeholders

### 2. **Lowercase with Underscores (Primary)**
- Easy to type and read
- Compatible with all operating systems
- Standard in software development
- No case sensitivity issues

### 3. **Hyphens for Epics**
- Distinguishes epics from other artifacts
- Matches common convention for epic identifiers
- Maintains readability for multi-word topics

### 4. **Preserved Formats**
- User stories maintain US-XXX format (widely recognized)
- Existing correct patterns are preserved

## Enforcement Requirements

### 1. **Automated Validation**
**MANDATORY**: All agile automation tools must validate naming conventions

```python
# REQUIRED: Naming validation in all automation
def validate_artifact_name(file_path: str, artifact_type: str) -> bool:
    """Validate artifact follows naming convention."""
    patterns = {
        'epic': r'^epic-[a-z0-9-]+\.md$',
        'user_story': r'^US-[A-Z0-9-]+\.md$', 
        'sprint_file': r'^sprint_\d+_[a-z_]+\.md$',
        'catalog': r'^[a-z_]+_catalog\.md$'
    }
    
    filename = Path(file_path).name
    pattern = patterns.get(artifact_type)
    
    if not pattern or not re.match(pattern, filename):
        raise NamingConventionViolation(f"File {filename} violates {artifact_type} naming convention")
    
    return True
```

### 2. **Agent Behavior Requirements**
**MANDATORY**: All agents maintaining agile artifacts must enforce naming conventions

```yaml
agent_requirements:
  file_creation:
    - "MUST validate naming convention before creating any file"
    - "MUST reject operations that violate naming standards"
    - "MUST provide correct naming suggestions for violations"
    
  file_modification:
    - "MUST maintain existing correct naming when modifying files"
    - "MUST report naming violations discovered during operations"
    - "MUST suggest renaming for non-compliant files"
    
  artifact_maintenance:
    - "MUST use only compliant names in all artifact references"
    - "MUST update references when files are renamed for compliance"
    - "MUST integrate naming validation into all workflows"
```

### 3. **Rule Integration**
**MANDATORY**: Integrate naming convention enforcement into all rule systems

```yaml
rule_integration:
  agile_automation:
    - "Naming validation integrated into agile_story_automation.py"
    - "Artifact updates validate naming before execution"
    - "Story creation enforces naming conventions"
    
  cursor_rules:
    - "File organization rules include naming convention enforcement"
    - "Development workflow rules validate artifact naming"
    - "Quality assurance rules check naming compliance"
    
  file_operations:
    - "All file creation validates naming conventions"
    - "File moving operations maintain naming compliance"
    - "Bulk operations include naming validation"
```

## Implementation Guidelines

### 1. **Immediate Actions Required**
1. **Rename EPIC-FORMAL-PRINCIPLES.md** to `epic-formal-principles.md`
2. **Audit all sprint files** for naming compliance
3. **Update all UPPER_CASE files** to lowercase_with_underscores
4. **Validate all existing artifacts** against new standards

### 2. **System Integration**
1. **Update agile automation** to enforce naming conventions
2. **Integrate validation** into file creation workflows
3. **Add naming checks** to quality assurance processes
4. **Create correction tools** for batch renaming

### 3. **Prevention Measures**
1. **Pre-commit hooks** validate artifact naming
2. **Automation scripts** reject non-compliant names
3. **Documentation** includes naming requirements
4. **Training materials** emphasize naming standards

## Error Prevention

### 1. **Common Mistakes to Avoid**
```yaml
❌ FORBIDDEN PATTERNS:
- Mixed case: "Epic_Formal_Principles.md"
- Spaces: "Epic Formal Principles.md"  
- Wrong separators: "epic.formal.principles.md"
- Wrong case: "EPIC-formal-principles.md"
- Inconsistent: "epic_formal-principles.md"
```

### 2. **Validation Checklist**
- [ ] Filename uses correct case (lowercase vs UPPER)
- [ ] Separators match artifact type (hyphens vs underscores)
- [ ] File extension is correct (.md for documentation)
- [ ] No spaces or special characters
- [ ] Matches established pattern for artifact type

## Rollback and Recovery

### 1. **Safe Renaming Process**
```bash
# REQUIRED: Always backup before renaming
1. Create backup of original file
2. Update all references to old name
3. Rename file to new convention
4. Validate all links and references
5. Test automation with new names
6. Commit changes atomically
```

### 2. **Emergency Rollback**
```bash
# If naming changes cause issues:
1. Restore original files from backup
2. Revert reference updates
3. Investigate automation failures  
4. Fix issues with new naming
5. Re-apply naming changes correctly
```

## Quality Assurance

### 1. **Compliance Monitoring**
- **Daily**: Automated scans for naming violations
- **Weekly**: Manual review of new artifacts
- **Monthly**: Comprehensive naming audit
- **Quarterly**: Naming convention effectiveness review

### 2. **Success Metrics**
- **100%** compliance with naming conventions
- **Zero** automation failures due to naming issues
- **Reduced** navigation time and confusion
- **Improved** professional appearance

## Enforcement

This rule is **ALWAYS ACTIVE** and applies to:
- All agile artifact creation
- All file renaming operations
- All automation script execution
- All agent artifact maintenance
- All quality assurance processes

**Violations require immediate correction and process improvement.**

## Remember

**"Consistent naming enables systematic excellence."**

**"Every file name should tell its purpose immediately."**

**"Automation depends on predictable naming patterns."**

**"Professional standards start with professional naming."**
