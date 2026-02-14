import re
import sys
import json

if len(sys.argv) < 2:
    sys.exit(0)
tag = sys.argv[1]

with open("build.md", encoding="utf-8") as f:
    build = f.read()
with open("build.json", encoding="utf-8") as f:
    build_data = json.load(f)
with open("README.md", encoding="utf-8") as f:
    readme = f.read()

for line in build.splitlines():
    line = line.strip()
    if not line or line.startswith(("Patches:", "Skipped:", "[Changelog]")):
        continue
    
    m = re.match(r"^(\S+)(?:\s*\(([^)]+)\))?\s*:\s*(.+)$", line)
    if not m:
        continue
    app_name, arch, version = m.groups()

    badge_version = version.replace("-", ".").replace(" ", "")
    link_version = re.sub(r"\.+", ".", re.sub(r"[^a-zA-Z0-9@+\-_.]", ".", version.replace(" ", "")))
    summary_pattern = rf'<summary id="{app_name}"[^>]*>.*?</summary>'
    matches = list(re.finditer(summary_pattern, readme, re.IGNORECASE))
    
    if not matches:
        continue
    
    # Update all badges
    for match in matches:
        old_summary = match.group(0)
        new_summary = re.sub(r'(href="[^"]*?/download/)\d+/', rf'\g<1>{tag}/', old_summary)
        
        if arch:
            new_summary = re.sub(rf'(href="[^"]*?-v)\d[^"]*?(-{re.escape(arch)}\.(?:apk|zip))', rf'\g<1>{link_version}\g<2>', new_summary)
        else:
            new_summary = re.sub(r'(href="[^"]*?-v)\d[^"]*?(-(arm64-v8a|arm-v7a|all)\.(?:apk|zip))', rf'\g<1>{link_version}\g<2>', new_summary)
        
        new_summary = re.sub(r'(src="[^"]*?-v)\d[^"]*?(-gray\?)', rf'\g<1>{badge_version}\g<2>', new_summary)
        
        if new_summary != old_summary:
            readme = readme.replace(old_summary, new_summary)
    
    # Update blockquote from JSON
    if app_name not in build_data:
        continue
    first_match = next(re.finditer(summary_pattern, readme, re.IGNORECASE), None)
    if not first_match:
        continue
    blockquote_match = next(re.finditer(r'<blockquote>\s*\n(.*?)\n</blockquote>', readme[first_match.end():], re.DOTALL), None)
    if not blockquote_match:
        continue
    blockquote_start = first_match.end() + blockquote_match.start()
    blockquote_end = first_match.end() + blockquote_match.end()
    
    app_info = build_data[app_name]
    new_content = f"\n\nPatch date: {app_info['patch_date']}<br>\nPatches: {app_info['patches']}\n[Changelog]({app_info['changelog']})"
    
    if "applied_patches" in app_info and app_info["applied_patches"]:
        for patch in app_info["applied_patches"]:
            if patch.strip():
                new_content += f"\n- {patch.strip()}"
    
    readme = readme[:blockquote_start] + f"<blockquote>{new_content}\n</blockquote>" + readme[blockquote_end:]

with open("README.md", "w", encoding="utf-8") as f:
    f.write(readme)

print("✓ README updated")
