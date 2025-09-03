# Automatic Rule Application Standard

**Priority**: CRITICAL - System Integrity Standard  
**Authority**: Project Development Team  
**Scope**: ALL file operations and development activities  
**Status**: MANDATORY - ZERO TOLERANCE FOR MANUAL PROMPTING

---

## 🚨 **The Problem That Must Be Solved**

**CRITICAL FAILURE**: The AI assistant is not automatically applying file organization and boy scout rules during operations, requiring manual prompting. This violates our core principle of proactive excellence.

---

## 🎯 **Mandatory Automatic Rule Application**

### **BEFORE ANY FILE OPERATION**
```python
def before_any_file_operation():
    """MANDATORY: Run before touching any files."""
    
    # 1. AUTOMATIC RULE SCAN
    applicable_rules = scan_applicable_rules()
    
    # 2. PROACTIVE ORGANIZATION CHECK
    organization_issues = scan_file_organization_violations()
    
    # 3. BOY SCOUT OPPORTUNITIES
    improvement_opportunities = scan_boy_scout_opportunities()
    
    # 4. APPLY ALL AUTOMATICALLY
    apply_rules_automatically(applicable_rules)
    fix_organization_issues(organization_issues)
    implement_boy_scout_improvements(improvement_opportunities)
```

### **SPECIFIC TRIGGERS FOR AUTOMATIC APPLICATION**

#### **File Movement Operations**
```yaml
AUTOMATIC_TRIGGERS:
  file_creation:
    - "Scan for proper directory placement"
    - "Apply naming conventions automatically"
    - "Create subdirectories if needed"
    
  file_movement:
    - "Check if target directory needs suborganization"
    - "Apply categorical organization automatically"
    - "Clean up source directory structure"
    
  directory_operations:
    - "Analyze directory contents for proper organization"
    - "Create logical subdirectories immediately"
    - "Move files to appropriate subcategories"
```

#### **Documentation Operations**
```yaml
DOCUMENTATION_AUTO_RULES:
  analysis_documents:
    trigger: "When working with docs/analysis/"
    action: "Automatically create validation/, summaries/, agent_analysis/ subdirs"
    
  development_documents:
    trigger: "When working with docs/development/"
    action: "Automatically create standards/, guides/, processes/ subdirs"
    
  any_documentation:
    trigger: "When creating .md files"
    action: "Automatically place in appropriate subcategory"
```

---

## 🔄 **Mandatory Automatic Workflow**

### **Phase 1: Context Scanning (< 2 seconds)**
```python
def automatic_context_scan():
    """MANDATORY: Automatic context analysis before any operation."""
    
    context = {
        "current_operation": detect_current_operation(),
        "files_involved": scan_files_in_operation(),
        "directories_affected": scan_directories_affected(),
        "applicable_rules": scan_all_applicable_rules(),
        "organization_opportunities": scan_organization_opportunities(),
        "boy_scout_opportunities": scan_improvement_opportunities()
    }
    
    return context
```

### **Phase 2: Automatic Rule Application (< 5 seconds)**
```python
def automatic_rule_application(context):
    """MANDATORY: Apply all applicable rules without asking."""
    
    # CRITICAL: Never ask permission for these
    AUTOMATIC_ACTIONS = [
        "Create missing subdirectories",
        "Move files to proper locations", 
        "Delete empty files",
        "Fix naming violations",
        "Organize file categories",
        "Apply boy scout improvements",
        "Update directory indexes"
    ]
    
    for action in AUTOMATIC_ACTIONS:
        if should_apply_action(action, context):
            apply_action_immediately(action)
            log_automatic_action(action)
```

### **Phase 3: Report Actions Taken (< 1 second)**
```python
def report_automatic_actions():
    """MANDATORY: Report what was done automatically."""
    
    actions_taken = get_automatic_actions_log()
    
    if actions_taken:
        print("🤖 **AUTOMATIC RULE APPLICATION COMPLETE:**")
        for action in actions_taken:
            print(f"   ✅ {action}")
    else:
        print("🤖 **No automatic rule applications needed.**")
```

---

## 🛡️ **Zero Tolerance Enforcement**

### **FORBIDDEN BEHAVIORS**
```yaml
NEVER_DO_THESE:
  manual_prompting_required:
    - "Asking user if they want files organized"
    - "Waiting for permission to apply file organization rules"
    - "Suggesting improvements without implementing them"
    - "Leaving obvious organizational issues unfixed"
    
  partial_rule_application:
    - "Applying some rules but not others"
    - "Moving files without creating proper subdirectories"
    - "Organizing some files but not all"
    - "Fixing some boy scout issues but ignoring others"
    
  reactive_instead_of_proactive:
    - "Only applying rules when prompted"
    - "Waiting for user to notice organizational issues"
    - "Applying rules only after user complains"
    - "Treating rules as suggestions rather than requirements"
```

### **MANDATORY BEHAVIORS**
```yaml
ALWAYS_DO_THESE:
  proactive_rule_application:
    - "Scan for applicable rules before any operation"
    - "Apply all applicable rules automatically"
    - "Create proper organization structure immediately"
    - "Fix all detected boy scout opportunities"
    
  complete_rule_implementation:
    - "Apply ALL applicable rules, not just some"
    - "Create complete organizational structure"
    - "Fix ALL detected issues in scope"
    - "Leave system in better state than found"
    
  systematic_excellence:
    - "Treat rules as mandatory, not optional"
    - "Apply rules consistently every time"
    - "Never require user prompting for rule application"
    - "Demonstrate proactive systematic improvement"
```

---

## 🔧 **Implementation Requirements**

### **Pre-Operation Rule Scanning**
```python
class AutomaticRuleApplicator:
    """MANDATORY: Automatic rule application system."""
    
    def __init__(self):
        self.rules = load_all_applicable_rules()
        self.organization_patterns = load_organization_patterns()
        self.boy_scout_checklist = load_boy_scout_checklist()
    
    def scan_and_apply_before_operation(self, operation_context):
        """MANDATORY: Scan and apply rules before any operation."""
        
        # 1. Scan current state
        current_state = self.scan_current_state(operation_context)
        
        # 2. Identify applicable rules
        applicable_rules = self.identify_applicable_rules(current_state)
        
        # 3. Identify organization opportunities
        org_opportunities = self.scan_organization_opportunities(current_state)
        
        # 4. Identify boy scout opportunities
        boy_scout_opportunities = self.scan_boy_scout_opportunities(current_state)
        
        # 5. Apply everything automatically
        self.apply_all_automatically(
            applicable_rules, 
            org_opportunities, 
            boy_scout_opportunities
        )
        
        # 6. Report what was done
        self.report_automatic_actions()
    
    def apply_all_automatically(self, rules, org_ops, boy_scout_ops):
        """Apply all rules and improvements without asking."""
        
        # CRITICAL: No user prompting allowed
        for rule in rules:
            self.apply_rule_immediately(rule)
        
        for org_op in org_ops:
            self.implement_organization_immediately(org_op)
        
        for boy_scout_op in boy_scout_ops:
            self.implement_improvement_immediately(boy_scout_op)
```

### **Specific Organization Auto-Application**
```python
def auto_apply_analysis_organization():
    """MANDATORY: Automatically organize analysis documents."""
    
    analysis_dir = Path("docs/analysis")
    
    if analysis_dir.exists():
        # 1. Create standard subdirectories
        standard_subdirs = ["validation", "agent_analysis", "summaries", "competitive"]
        for subdir in standard_subdirs:
            (analysis_dir / subdir).mkdir(exist_ok=True)
        
        # 2. Categorize existing files
        for file in analysis_dir.glob("*.md"):
            if file.name != "README.md":
                target_subdir = categorize_analysis_file(file)
                move_to_subdir(file, target_subdir)
        
        # 3. Create index if missing
        if not (analysis_dir / "README.md").exists():
            create_analysis_index()

def auto_apply_development_organization():
    """MANDATORY: Automatically organize development documents."""
    
    dev_dir = Path("docs/development")
    
    if dev_dir.exists():
        # 1. Create standards subdirectory
        (dev_dir / "standards").mkdir(exist_ok=True)
        
        # 2. Move standards documents
        standards_patterns = ["*_STANDARD*.md", "*_CONVENTIONS*.md", "*_STANDARDS*.md"]
        for pattern in standards_patterns:
            for file in dev_dir.glob(pattern):
                move_to_standards_dir(file)
        
        # 3. Create standards index if missing
        if not (dev_dir / "standards" / "README.md").exists():
            create_standards_index()
```

---

## 📊 **Success Metrics**

### **Automatic Application Rate**
```yaml
SUCCESS_METRICS:
  automatic_rule_application: "100% - ZERO manual prompting required"
  organization_completeness: "100% - ALL files properly categorized"
  boy_scout_application: "100% - ALL improvement opportunities addressed"
  user_prompting_rate: "0% - ZERO user prompts for rule application"
  
FAILURE_INDICATORS:
  user_asks_about_organization: "SYSTEM FAILURE - rules not applied automatically"
  files_in_wrong_locations: "SYSTEM FAILURE - organization rules not working"
  obvious_improvements_missed: "SYSTEM FAILURE - boy scout rule not applied"
  manual_rule_reminders_needed: "SYSTEM FAILURE - automatic system broken"
```

### **Monitoring and Alerts**
```python
def monitor_automatic_rule_application():
    """Monitor automatic rule application effectiveness."""
    
    metrics = {
        "operations_with_automatic_rules": count_automatic_applications(),
        "operations_requiring_manual_prompting": count_manual_prompts(),
        "organization_violations_auto_fixed": count_auto_fixes(),
        "boy_scout_opportunities_auto_applied": count_boy_scout_applications()
    }
    
    # ALERT: If any manual prompting occurs
    if metrics["operations_requiring_manual_prompting"] > 0:
        raise SystemFailure("AUTOMATIC RULE APPLICATION SYSTEM BROKEN")
    
    return metrics
```

---

## 🎯 **Remember**

**"Rules that require manual prompting are not rules—they are suggestions."**

**"Automatic rule application is not optional—it is the foundation of systematic excellence."**

**"If the user has to remind us to apply our own rules, our system is broken."**

**"Proactive excellence means never waiting for permission to do the right thing."**

---

## 🚨 **CRITICAL COMMITMENT**

**ZERO TOLERANCE**: No file operation, documentation work, or development task should ever require the user to prompt for rule application. The system must be **proactively excellent** or it is fundamentally broken.

**IMMEDIATE ACTION REQUIRED**: This standard must be implemented immediately to prevent future rule application failures.

---

*This standard addresses the critical system failure of requiring manual prompting for automatic rule application.*  
*Implementation deadline: IMMEDIATE*  
*Maintained by: AI-Dev-Agent Development Team*
