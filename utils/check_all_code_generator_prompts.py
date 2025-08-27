import sqlite3

conn = sqlite3.connect('prompts/prompt_templates.db')
cursor = conn.cursor()

# Check all code_generator prompts
cursor.execute('SELECT * FROM prompt_templates WHERE name LIKE "%code%"')
results = cursor.fetchall()

print(f"Found {len(results)} code-related prompts:")
for i, result in enumerate(results):
    print(f"\nPrompt {i+1}:")
    print(f"  ID: {result[0]}")
    print(f"  Topic: {result[1]}")
    print(f"  Name: {result[2]}")
    print(f"  Purpose: {result[3]}")
    print(f"  Template preview: {result[4][:100]}...")
    print(f"  Use web search: {result[5]}")

conn.close()
