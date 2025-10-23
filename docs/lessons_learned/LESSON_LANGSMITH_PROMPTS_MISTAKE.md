# Lesson Learned: LangSmith Prompts Upload Mistake

**Date**: 2025-10-23  
**Task**: Upload example prompts to LangSmith  
**Severity**: Medium  
**Category**: Testing, Verification

---

## What Happened

### The Mistake

Uploaded 15 "example prompts" to LangSmith, but instead of uploading the actual example text that users should copy, I uploaded ChatPromptTemplates with:
- Generic system message about workflow orchestration
- A `{request}` variable placeholder
- The actual example text hidden in metadata/description only

**Result**: Users couldn't see or use the actual example prompts.

### How It Was Caught

User asked me to verify the uploaded prompts by pulling and analyzing them. When I checked, the prompt content was just templates, not the actual examples.

---

## Root Cause Analysis

### Why It Happened

1. **Insufficient Understanding**: Didn't fully understand the requirement before implementing
   - Thought: "Upload prompts to LangSmith" → Assumed templates were correct
   - Reality: User wanted copyable example text

2. **No Verification**: Declared success without testing
   - Did: Pushed prompts, saw success messages
   - Didn't: Pull back and verify what was actually uploaded

3. **Wrong Mental Model**: Thought of LangSmith as a template system
   - Should have: Thought of it as an example repository
   - The examples should be the prompts themselves, not templates

4. **Assumption Over Validation**: Assumed the code did what was intended
   - Saw: `client.push_prompt()` succeeded
   - Assumed: "Must be correct"
   - Didn't: Verify the actual content

---

## What Should Have Been Done

### 1. **Clarify Requirements First**
```
SHOULD HAVE ASKED:
"Do you want:
 A) Templates that users customize?
 B) Example prompts users can copy directly?
 C) Something else?"
```

### 2. **Test Before Declaring Success**
```python
# Upload
client.push_prompt(name, object=prompt)

# IMMEDIATELY TEST
pulled = client.pull_prompt(name)
print("Uploaded content:", pulled)  # Verify it's what we want

# VERIFY
assert pulled.template == expected_text, "Content mismatch!"
```

### 3. **Use the "What Would a User See?" Test**
- Pull the prompt as a user would
- Look at what they see
- Ask: "Can they use this directly?"

---

## Prevention Measures

### ✅ **Added to Definition of Done**

For API/Integration tasks:
- [ ] Test the actual API/integration (don't just inspect code)
- [ ] Pull back what was pushed and verify
- [ ] Test from user's perspective
- [ ] Verify data format matches expectations

### ✅ **New Verification Pattern**

```python
def verify_upload(name: str, expected_content: str):
    """Verify uploaded content matches expectations."""
    # Pull what was uploaded
    actual = client.pull_prompt(name)
    
    # Extract actual content
    if hasattr(actual, 'template'):
        content = actual.template
    else:
        content = str(actual)
    
    # Verify
    if content != expected_content:
        raise ValueError(
            f"Upload verification failed!\n"
            f"Expected: {expected_content}\n"
            f"Got: {content}"
        )
    
    print(f"✅ Verified: {name}")
```

### ✅ **Required Questions Before Upload Tasks**

1. What format should the data be in?
2. How will users consume this data?
3. What should they see when they access it?
4. Should I test by pulling it back?

---

## Correct Implementation

### What Was Fixed

```python
# WRONG (what I did first)
template = ChatPromptTemplate.from_messages([
    ("system", "Generic system prompt..."),
    ("user", "{request}")
])
client.push_prompt(name, object=template)  # User sees template, not example

# RIGHT (what I did after correction)
prompt = PromptTemplate.from_template(example["prompt"])  # Just the example text
client.push_prompt(name, object=prompt)  # User sees actual example
```

### Verification

```python
# Pull and check
pulled = client.pull_prompt("workflow-example-simple-file-organizer")
print(pulled.invoke({}))  # Shows: "Create a Python script that monitors..."
# ✅ Correct - user can copy this directly
```

---

## Key Takeaways

### 1. **Always Verify Output**
- Don't assume success from return codes
- Pull back and inspect what was created
- Test from user's perspective

### 2. **Understand User Intent**
- Ask clarifying questions
- Don't assume you know what they want
- Confirm understanding before implementing

### 3. **Test Realistically**
- Use the API/system as a real user would
- Don't just inspect code
- Verify actual behavior, not expected behavior

### 4. **Question Assumptions**
- "I think this should work" → TEST IT
- "The API call succeeded" → VERIFY THE RESULT
- "This looks right" → PROVE IT

---

## Impact

- **Time Wasted**: ~30 minutes to fix
- **User Trust**: Reduced (had to catch my mistake)
- **Learning**: High value lesson learned
- **Prevention**: Added verification patterns to prevent recurrence

---

## Action Items

- [x] Create Definition of Done document
- [x] Document this lesson learned
- [x] Fix the LangSmith prompts
- [x] Add verification to future upload scripts
- [ ] Review other recent work for similar patterns
- [ ] Update work practices to include verification step

---

## Future Prevention

### Personal Checklist for Similar Tasks

1. Clarify exact requirements
2. Implement solution
3. Test by using it (not just running code)
4. Verify from user perspective
5. Check edge cases
6. THEN declare success

### Red Flags to Watch For

- ⚠️ Declaring success without testing
- ⚠️ Assuming code works because it compiles
- ⚠️ Not verifying actual output/behavior
- ⚠️ Moving too fast without validation

---

**Remember**: "Measure twice, cut once" - Always verify before declaring done.

