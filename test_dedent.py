import textwrap

# Simulate CRLF card_html (as it exists in file with CRLF line endings)
card_html = "\r\n    <style>\r\n        .barber-card-1 {\r\n            background: red;\r\n        }\r\n    </style>\r\n    <div class=\"barber-card-1\">Test</div>\r\n    "

result = textwrap.dedent(card_html).strip()
print("Result repr (first 120 chars):", repr(result[:120]))
print()
print("Starts with <style>:", result.startswith("<style>"))
print("First 5 chars repr:", repr(result[:5]))
print()

# Also test what Streamlit CommonMark does with this
# If result starts with <style>, CommonMark should treat it as raw HTML block (Type 6)
# If result starts with \n<style>, the \n then <style> at col-0 still works as Type 6

# Now simulate what happens with the ACTUAL lines from the file
# (reading design_system.py and extracting the card_html)
with open("design_system.py", "r", newline="", encoding="utf-8-sig") as f:
    content = f.read()

idx = content.find("card_html = f\"\"\"")
# Extract the f-string content manually (we can't exec it but we can look at the raw bytes)
snippet = content[idx:idx+200]
print("Raw card_html definition start:")
print(repr(snippet))
print()

# The actual triple-quote opens then immediately has \r\n or \n ?
after_triple = content[idx + len('card_html = f"""'):]
first_chars = after_triple[:20]
print("First chars after triple-quote:", repr(first_chars))
