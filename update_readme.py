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
    try:
        m = re.match(r"^([\w\.-]+)(?:\s*\(([^)]+)\))?\s*:\s*(.+)$", line.strip())
        if not m:
            continue

        app_name, arch, version = m.groups()

        badge_version = version.replace("-", ".").replace(" ", "")
        link_version = version.replace(" ", "").replace("(", ".").replace(")", ".")

        # Find badge pattern:
        # Matches the whole Markdown link: [![Download-AppName](BadgeURL)](DownloadURL)
        if arch:
            pattern = rf"\[!\[Download-{re.escape(app_name)}\].*?-{re.escape(arch)}\.apk\)"
        else:
            pattern = rf"\[!\[Download-{re.escape(app_name)}\].*?\.apk\)"

        for match in re.finditer(pattern, readme, re.DOTALL | re.IGNORECASE):
            old_badge = match.group(0)

            # Split into [Start+Badge] and [DownloadLink] 
            parts = old_badge.split("](")

            if len(parts) >= 2:
                # 1. Update Badge URL
                # Matches -v...-gray
                parts[-2] = re.sub(
                    r"(-v).*?(-gray)", f"\\g<1>{badge_version}\\g<2>", parts[-2]
                )

                # 2. Update Download Link
                # Matches -v...-arm or -v...-all
                parts[-1] = re.sub(
                    r"(-v).*?(-(?:arm|all))", f"\\g<1>{link_version}\\g<2>", parts[-1]
                )
                parts[-1] = re.sub(r"download/\d+/", f"download/{tag}/", parts[-1])

                new_badge = "](".join(parts)
                readme = readme.replace(old_badge, new_badge)
    except Exception as e:
        print(f"Error processing line '{line.strip()}': {e}")
        continue

with open("README.md", "w", encoding="utf-8") as f:
    f.write(readme)

print("✓ README updated")
