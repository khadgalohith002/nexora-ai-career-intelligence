import re

# Read the file
with open(
    r"c:\Users\user\OneDrive\Documents\GitHub\universal ai resume analyzer\app.py",
    "r",
    encoding="utf-8",
) as f:
    content = f.read()

# Remove excessive blank lines (more than 2 consecutive blank lines)
content = re.sub(r"\n\n\n+", "\n\n", content)

# Write the file back
with open(
    r"c:\Users\user\OneDrive\Documents\GitHub\universal ai resume analyzer\app.py",
    "w",
    encoding="utf-8",
) as f:
    f.write(content)

print("File indentation cleaned successfully!")
