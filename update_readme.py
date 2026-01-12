import re
import sys

if len(sys.argv) < 2:
    sys.exit(0)
tag = sys.argv[1]

with open("build.md", encoding="utf-8") as f:
    build = f.read()
with open("README.md", encoding="utf-8") as f:
    readme = f.read()

# Parse each line: "AppName: version" or "AppName (arch): version"
for line in build.splitlines():
    m = re.match(r"^([\w\.-]+)(?:\s*\(([^)]+)\))?\s*:\s*([\d\.]+)$", line.strip())
    if not m:
        continue

    app_name, arch, version = m.groups()

    # Find badge pattern:
    if arch:
        pattern = rf"\[!\[Download-{re.escape(app_name)}\].*?-{re.escape(arch)}\.apk\)"
    else:
        pattern = rf"\[!\[Download-{re.escape(app_name)}\].*?\.apk\)"

    for match in re.finditer(pattern, readme, re.DOTALL):
        old_badge = match.group(0)
        # Replace version: -vX.X.X- → -v{new_version}-
        new_badge = re.sub(r"-v[\d.]+-", f"-v{version}-", old_badge)
        # Replace tag: download/old_tag/ → download/{new_tag}/
        new_badge = re.sub(r"download/\d+/", f"download/{tag}/", new_badge)

        readme = readme.replace(old_badge, new_badge)

with open("README.md", "w", encoding="utf-8") as f:
    f.write(readme)

print("✓ README updated")
