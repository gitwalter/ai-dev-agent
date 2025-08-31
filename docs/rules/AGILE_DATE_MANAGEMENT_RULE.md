# Agile Date Management Rule

**CRITICAL**: All keyword subagents must follow realistic date practices when creating or updating agile artifacts.

## Core Date Principles

### **1. Realistic Date Requirements**
- **NO FUTURE DATES** beyond 90 days from current date
- **NO PAST DATES** beyond 1 year from current date (unless historical)
- **CONSISTENT TIMELINES** across related artifacts
- **APPROPRIATE CONTEXT** - creation dates in past, due dates in near future

### **2. Standard Date Format**
**MANDATORY**: Use ISO 8601 format: `YYYY-MM-DD`
- ✅ Correct: `2025-01-28`
- ❌ Wrong: `28.01.2025`, `01/28/2025`, `Jan 28, 2025`

### **3. Date Context Guidelines**

#### **Creation Dates**
- User stories: Recent past (1-30 days ago)
- Sprint artifacts: Sprint start date
- Documentation: When actually created

#### **Update Dates**
- Always use current date when making changes
- Update whenever significant modifications occur

#### **Due/End Dates**
- Sprint end dates: 7-14 days from current date for active sprints
- Story completion: Within current sprint timeframe
- Planning dates: Near future (7-30 days)

#### **Sprint Dating**
- Sprint 1: Completed (ended ~16 days ago)
- Sprint 2: Current (started ~14 days ago, ending in ~7 days)
- Future sprints: Plan 14-day cycles from Sprint 2 end

### **4. Validation Rules**

#### **Before Creating/Updating Agile Artifacts**
```python
def validate_agile_dates(content: str) -> bool:
    current_date = datetime.now()
    
    # Extract all dates from content
    dates = extract_dates_from_content(content)
    
    for date_obj, context in dates:
        # Check if date is reasonable
        days_diff = (date_obj - current_date).days
        
        if "Created" in context or "Start" in context:
            # Creation/start dates should be in past
            if days_diff > 0:
                return False
                
        elif "Updated" in context:
            # Update dates should be current
            if abs(days_diff) > 1:
                return False
                
        elif "End" in context or "Due" in context:
            # Due dates should be near future
            if days_diff < 0 or days_diff > 90:
                return False
    
    return True
```

### **5. Subagent Integration Requirements**

#### **ALL Keyword Subagents MUST**
1. **Validate dates** before creating any agile artifact
2. **Use current date** for update timestamps
3. **Calculate realistic dates** based on sprint context
4. **Check date consistency** across related artifacts
5. **Apply standard format** (YYYY-MM-DD) always

#### **Specific Subagent Responsibilities**

**@agile subagents:**
- Validate ALL dates in sprint planning artifacts
- Ensure sprint dates follow 14-day cycles
- Check story dates align with sprint timelines

**@architect subagents:**
- Verify architectural decision dates are realistic
- Ensure design timeline dates are achievable

**@developer subagents:**
- Set realistic implementation dates
- Update completion dates accurately

**@tester subagents:**
- Plan realistic testing timelines
- Update test completion dates promptly

**@documenter subagents:**
- Use current date for documentation updates
- Set realistic documentation completion dates

### **6. Automatic Date Management**

#### **Template System**
```python
AGILE_DATE_TEMPLATES = {
    "current_date": lambda: datetime.now().strftime("%Y-%m-%d"),
    "sprint_2_start": lambda: (datetime.now() - timedelta(days=14)).strftime("%Y-%m-%d"),
    "sprint_2_end": lambda: (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d"),
    "sprint_3_start": lambda: (datetime.now() + timedelta(days=8)).strftime("%Y-%m-%d"),
    "sprint_3_end": lambda: (datetime.now() + timedelta(days=21)).strftime("%Y-%m-%d"),
    "recent_past": lambda days=7: (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d"),
    "near_future": lambda days=14: (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")
}
```

### **7. Error Prevention**

#### **Common Date Errors to Avoid**
- Future creation dates
- Past due dates for active items
- Inconsistent sprint timelines
- Wrong date formats
- Unrealistic planning horizons

#### **Validation Checklist**
- [ ] All dates use YYYY-MM-DD format
- [ ] Creation dates are in reasonable past
- [ ] Update dates are current
- [ ] Due dates are in near future
- [ ] Sprint dates follow logical sequence
- [ ] No dates beyond 90-day planning horizon

### **8. Implementation in Subagent DNA**

```python
class BaseSubagent:
    def __init__(self):
        self.date_rules = AgileDateRules()
        
    def validate_agile_content(self, content: str) -> bool:
        return self.date_rules.validate_all_dates(content)
        
    def get_current_date(self) -> str:
        return datetime.now().strftime("%Y-%m-%d")
        
    def calculate_sprint_date(self, sprint_num: int, position: str) -> str:
        # Calculate realistic sprint dates
        base_date = datetime.now()
        if sprint_num == 2:
            if position == "start":
                return (base_date - timedelta(days=14)).strftime("%Y-%m-%d")
            else:  # end
                return (base_date + timedelta(days=7)).strftime("%Y-%m-%d")
        # Add logic for other sprints
```

### **9. Enforcement**

This rule is **MANDATORY** for all subagents and will be:
- Embedded in subagent DNA as core principles
- Validated automatically before artifact creation
- Checked during artifact updates
- Enforced through systematic validation

### **10. Continuous Monitoring**

The Agile Date Correction Team will:
- Monitor for date violations daily
- Auto-fix simple date errors
- Report persistent violations
- Update rules based on patterns

## Remember

**"Realistic dates build realistic plans."**
**"Current dates for current work."**
**"Consistent timelines enable reliable delivery."**

This rule ensures all agile artifacts maintain realistic, consistent, and meaningful dates that support effective project management and team coordination.