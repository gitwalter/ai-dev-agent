# Definition of Done (DoD)

**Purpose**: Ensure all work meets quality standards BEFORE declaring completion.

---

## Core Principle

**"Test, Verify, Then Report - Never Assume Success"**

Every task must pass ALL applicable checks before being considered complete.

---

## Universal DoD (All Tasks)

### ✅ **Before ANY Task is "Done":**

1. **Purpose Verification**
   - [ ] Understand EXACTLY what the user wants
   - [ ] Ask clarifying questions if ANY uncertainty exists
   - [ ] Confirm the expected outcome/behavior

2. **Implementation Verification**
   - [ ] Code/changes implement the ACTUAL requirement (not what I think they want)
   - [ ] Test the implementation with realistic scenarios
   - [ ] Verify edge cases are handled

3. **Output Verification**
   - [ ] Test the actual output/behavior
   - [ ] Verify it matches the user's stated goal
   - [ ] Check for unintended side effects

4. **Quality Checks**
   - [ ] No syntax errors
   - [ ] No logic errors
   - [ ] Follows project conventions
   - [ ] Documentation is accurate

5. **User Impact**
   - [ ] Does this actually solve the user's problem?
   - [ ] Are there any gotchas or limitations?
   - [ ] Is this the simplest solution that works?

---

## Task-Specific DoD

### 📝 **Code Changes**

- [ ] Code compiles/runs without errors
- [ ] Unit tests pass (or create if missing)
- [ ] Linter checks pass
- [ ] Type checks pass (if applicable)
- [ ] Integration tests pass (if applicable)
- [ ] Manual testing completed
- [ ] No regressions introduced
- [ ] Code follows SOLID principles
- [ ] No duplicate code (DRY)
- [ ] Error handling implemented
- [ ] Logging added where appropriate

**Verification Command**: Run the actual code/test before declaring success

### 🔧 **Configuration Changes**

- [ ] Configuration is syntactically valid (test parse it)
- [ ] Configuration achieves stated goal
- [ ] No conflicts with existing config
- [ ] Backwards compatible (if required)
- [ ] Environment variables documented
- [ ] Test with actual system (not just inspection)

**Verification Command**: Load and validate the config

### 📤 **API/Integration Work**

- [ ] Test the actual API/integration
- [ ] Verify data format matches expectations
- [ ] Test error conditions
- [ ] Check rate limits/quotas
- [ ] Verify authentication works
- [ ] Test with real data (not mocked)
- [ ] Document any limitations

**Verification Command**: Make real API calls, don't just inspect code

### 📚 **Documentation**

- [ ] Examples are tested and work
- [ ] Code snippets are copy-pasteable
- [ ] Links are valid
- [ ] Screenshots are current
- [ ] Instructions are complete
- [ ] Beginner-friendly language

**Verification Command**: Follow the docs as a new user would

### 🚀 **Deployments/Releases**

- [ ] All tests pass in target environment
- [ ] Deployment script tested
- [ ] Rollback plan exists
- [ ] Smoke tests pass
- [ ] Monitoring alerts configured
- [ ] Documentation updated
- [ ] Changelog updated

**Verification Command**: Deploy to staging first, verify, then production

### 📊 **Data/Prompt Management**

- [ ] Test pulling/using the data
- [ ] Verify format is correct
- [ ] Check metadata is accurate
- [ ] Test with actual system
- [ ] Verify no data corruption
- [ ] Check permissions/access

**Verification Command**: Pull and use the data, don't just push it

---

## The "3-Check Rule"

Before declaring ANY task complete, perform these 3 checks:

### 1️⃣ **Purpose Check**
"Does this accomplish what the user actually asked for?"
- Re-read the user's request
- Compare with what was implemented
- Confirm alignment

### 2️⃣ **Reality Check**
"Does it actually work in practice?"
- Test it for real (not just code inspection)
- Try to break it
- Check edge cases

### 3️⃣ **Impact Check**
"Are there any unintended consequences?"
- Did I break something else?
- Are there side effects?
- Is this the simplest solution?

---

## Anti-Patterns to Avoid

### ❌ **Assumption-Based Completion**
```
BAD:  "I wrote the code, so it must work"
GOOD: "I wrote and TESTED the code, verified output matches expectations"
```

### ❌ **Partial Testing**
```
BAD:  "I tested one scenario, that's enough"
GOOD: "I tested normal case, edge cases, error cases, and integration"
```

### ❌ **Documentation-Only Verification**
```
BAD:  "The docs say it should work this way"
GOOD: "I tested it and confirmed it actually works this way"
```

### ❌ **Code Inspection Instead of Execution**
```
BAD:  "The code looks right, so it's done"
GOOD: "I ran the code and verified the output"
```

### ❌ **Success Announcement Without Verification**
```
BAD:  "✅ Success!" (without testing)
GOOD: "Testing... [runs test] ... ✅ Verified working"
```

---

## Task Completion Template

Use this template when completing tasks:

```markdown
## Task: [Description]

### What was requested:
- [User's actual request]

### What was implemented:
- [What I actually did]

### Verification performed:
- [ ] Test 1: [specific test] → Result: [pass/fail]
- [ ] Test 2: [specific test] → Result: [pass/fail]
- [ ] Test 3: [specific test] → Result: [pass/fail]

### Edge cases checked:
- [ ] Case 1: [description] → Result: [pass/fail]
- [ ] Case 2: [description] → Result: [pass/fail]

### Known limitations:
- [Any limitations or caveats]

### Evidence:
[Command output, test results, screenshots, etc.]

### Confidence level:
[High/Medium/Low] - [Explanation]
```

---

## Improvement Process

### When Mistakes Happen:

1. **Acknowledge**: "I made a mistake because [reason]"
2. **Analyze**: Root cause analysis
3. **Document**: Add to lessons learned
4. **Prevent**: Update DoD to catch similar issues
5. **Improve**: Enhance verification process

### Continuous Improvement:

1. Track common failure patterns
2. Add checks to prevent recurring issues
3. Update DoD based on lessons learned
4. Review and refine process regularly

---

## Quick Reference Card

**Before saying "Done":**

1. ✅ Did I test it FOR REAL?
2. ✅ Does it solve the ACTUAL problem?
3. ✅ Are there any SIDE EFFECTS?
4. ✅ Did I verify the OUTPUT?
5. ✅ Can I PROVE it works?

**If ANY answer is "No" → It's NOT done!**

---

**Last Updated**: 2025-10-23
**Owner**: AI Development Agent Team
**Review Frequency**: After every major issue

