#!/usr/bin/env python3
from __future__ import annotations
import re
"""
Big0Time Project Sync Script

Scans the GitHub projects directory and updates the big0time index.html with:
- Pinned projects at the top
- Projects sorted by modification date (newest first)
- Grayed out text for projects without landing pages
- Fire icon (🔥) for recently active projects (modified in last 7 days)
- Copies under-construction.html to projects without landing pages
- Captures screenshots for pinned projects and uses them as blurred backgrounds
"""

import os
import shutil
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
import argparse

# Configuration
SCRIPT_DIR = Path(__file__).resolve().parent
big0time_DIR = SCRIPT_DIR
GITHUB_DIR = big0time_DIR.parent
UNDER_CONSTRUCTION = big0time_DIR / "under-construction.html"
INDEX_HTML = big0time_DIR / "index.html"
SCREENSHOT_DIR = big0time_DIR / "resources" / "screenshots"
RECENT_DAYS = 7  # Projects modified within this many days get fire icon
SCREENSHOT_EXPIRY_SECONDS = 24 * 60 * 60  # Screenshots expire after 24 hours

# Pinned projects
PINNED_PROJECTS = [
    "ButterPass",
    "security-adventure",
    "vax-console-sim",
    "kraemeverse-wiki",
    "tornado-cones",
    "satans-spreadsheet",
    "hackers-team",
    "sandrine-portfolio",
    "mobius-farm-II",
    "aetherstones-council-of-green-point",
    "touski",
    "neutral-zero",
    "pixel-duel-ii",
    "pixel-duel",
]

# Custom URLs for specific projects
CUSTOM_URLS = {
    "hackers-team": "https://polerix.github.io/hackers-team/frontend/",
    "sandrine-portfolio": "https://polerix.github.io/sandrine-portfolio/",
}

# Landing page patterns to check (in order of preference)
SEARCH_SUBDIRS = [".", "dist", "public", "frontend", "docs"]
LANDING_PAGES = [
    "index.html",
    "index.htm",
    "README.html",
    "main.html",
    "app.html",
]


def capture_screenshot(url: str, output_path: Path, force: bool = False):
    """Capture a website screenshot using headless Chrome, with expiry and force options"""
    if not url:
        return

    if output_path.exists() and not force:
        # Check if screenshot is expired
        modified_time = datetime.fromtimestamp(output_path.stat().st_mtime)
        if (datetime.now() - modified_time).total_seconds() < SCREENSHOT_EXPIRY_SECONDS:
            print(f"    Skipping screenshot for {url} (fresh enough).")
            return

    print(f"    Capturing screenshot of {url}...")
    try:
        chrome_path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
        if not Path(chrome_path).exists():
            print("    Google Chrome not found, skipping screenshot.")
            return

        subprocess.run(
            [
                chrome_path,
                "--headless",
                f"--screenshot={output_path}",
                "--window-size=1280,800",
                url,
            ],
            timeout=120,
            capture_output=True,
        )
        print(f"    Screenshot saved to {output_path}")
    except Exception as e:
        print(f"    Failed to capture screenshot for {url}: {e}")


def get_project_description(project_dir: Path) -> str:
    """Extract project description from README.md or package.json"""
    readme = project_dir / "README.md"
    if readme.exists():
        try:
            content = readme.read_text(encoding='utf-8', errors='ignore')
            lines = content.strip().split('\n')
            # Skip title line (# prefix) and get first non-empty line
            for line in lines[1:]:
                line = line.strip()
                if line and not line.startswith('#'):
                    # Clean up the description
                    desc = line.strip().lstrip('- ').lstrip('* ')
                    if len(desc) > 60:
                        desc = desc[:57] + "..."
                    return desc
        except Exception:
            pass

    # Try package.json
    pkg_json = project_dir / "package.json"
    if pkg_json.exists():
        try:
            import json
            pkg = json.loads(pkg_json.read_text(encoding='utf-8', errors='ignore'))
            desc = pkg.get("description", "")
            if desc and len(desc) > 60:
                desc = desc[:57] + "..."
            return desc
        except Exception:
            pass

    return ""


def get_github_url(project_dir: Path) -> str:
    try:
        result = subprocess.run(["git", "remote", "get-url", "origin"], cwd=project_dir, capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            url = result.stdout.strip()
            if url.endswith(".git"): url = url[:-4]
            if "git@github.com:" in url: url = url.replace("git@github.com:", "https://github.com/")
            return url
    except: pass
    return f"https://github.com/polerix/{project_dir.name}"


def find_landing_page(project_dir: Path) -> tuple[str, str] | None:
    project_name = project_dir.name
    if project_name in CUSTOM_URLS: return CUSTOM_URLS[project_name], ""
    try:
        result = subprocess.run(["git", "remote", "get-url", "origin"], cwd=project_dir, capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            remote_url = result.stdout.strip().replace(".git", "")
            repo_name = remote_url.split("/")[-1]
            base_url = f"https://polerix.github.io/{repo_name}"
        else: base_url = f"https://polerix.github.io/{project_name}"
    except: base_url = f"https://polerix.github.io/{project_name}"
    for subdir in SEARCH_SUBDIRS:
        target_dir = project_dir / subdir
        if not target_dir.exists(): continue
        # 1. Check for index.html at root FIRST if searching root
        if subdir == ".":
            for f in ["index.html", "index.htm"]:
                if (target_dir / f).exists(): return f"{base_url}/", str(target_dir / f)
        # 2. Try exact matches from LANDING_PAGES list
        for landing in LANDING_PAGES:
            landing_path = target_dir / landing
            if landing_path.exists():
                url_suffix = "" if subdir == "." else f"{subdir}/"
                file_suffix = "" if landing in ["index.html", "index.htm"] else landing
                return f"{base_url}/{url_suffix}{file_suffix}", str(landing_path)
        # 3. Try flexible matching (index*.html) - SKIP if it is under-construction
        try:
            for item in target_dir.glob("index*.html"):
                if "under-construction" in item.name: continue
                url_suffix = "" if subdir == "." else f"{subdir}/"
                return f"{base_url}/{url_suffix}{item.name}", str(item)
        except: pass
    return None
def get_deployed_url(project_name: str) -> str | None:
    project_dir = GITHUB_DIR / project_name
    found = find_landing_page(project_dir)
    return found[0] if found else None


def get_project_modification_date(project_dir: Path) -> datetime:
    latest_date = datetime(1970, 1, 1)
    git_dir = project_dir / ".git"
    if git_dir.exists():
        try:
            result = subprocess.run(["git", "log", "-1", "--format=%ct"], cwd=project_dir, capture_output=True, text=True, timeout=5)
            if result.returncode == 0 and result.stdout.strip():
                return datetime.fromtimestamp(int(result.stdout.strip()))
        except: pass
    check_paths = [project_dir, project_dir / "src", project_dir / "public", project_dir / "frontend"]
    for path in check_paths:
        if path.exists():
            try:
                for item in path.iterdir():
                    if item.is_file() and not item.name.startswith("."): 
                        mtime = datetime.fromtimestamp(item.stat().st_mtime)
                        latest_date = max(latest_date, mtime)
            except: pass
    return latest_date


def is_recently_modified(project_dir: Path) -> bool:
    """Check if project was modified in the last RECENT_DAYS days"""
    mod_date = get_project_modification_date(project_dir)
    return datetime.now() - mod_date < timedelta(days=RECENT_DAYS)


def has_landing_page(project_dir: Path) -> bool:
    """Check if project has a landing page"""
    if project_dir.name in CUSTOM_URLS:
        return True
    for landing in LANDING_PAGES:
        if (project_dir / landing).exists():
            return True
    return False


def copy_under_construction(project_name: str) -> str:
    """Copy under-construction.html to a project directory"""
    project_dir = GITHUB_DIR / project_name
    dest = project_dir / "under-construction.html"

    if not dest.exists():
        os.makedirs(project_dir, exist_ok=True) # Ensure the project directory exists
        shutil.copy2(UNDER_CONSTRUCTION, dest)
        print(f"  Copied under-construction.html to {project_name}")

    return "under-construction.html"


def get_commit_count_last_7_days(project_dir: Path) -> int:
    """Get number of commits in the last 7 days"""
    try:
        result = subprocess.run(
            ["git", "rev-list", "--count", "--since", "7 days ago", "HEAD"],
            cwd=project_dir,
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            return int(result.stdout.strip())
    except Exception:
        pass
    return 0


def generate_project_html(project_name: str, project_dir: Path, pinned: bool = False, force_screenshot: bool = False) -> str:
    landing_found = find_landing_page(project_dir)
    has_landing = landing_found is not None
    description = get_project_description(project_dir)
    description = re.sub(r"<[^>]+>", "", description)
    description = description.replace("**", "").replace("\\u", "").strip()
    if len(description) > 80: description = description[:77] + "..."
    if has_landing:
        open_url = landing_found[0]
    else:
        copy_under_construction(project_name)
        open_url = f"https://polerix.github.io/{project_name}/under-construction.html"
    github_url = get_github_url(project_dir)
    
    style = ""
    if pinned:
        screenshot_path = SCREENSHOT_DIR / f"{project_name.lower()}.png"
        capture_screenshot(open_url, screenshot_path, force=force_screenshot)
        if screenshot_path.exists():
            style = f'style="--bg-image: url(resources/screenshots/{project_name.lower()}.png);"'


    # Determine the status icon
    if pinned:
        status_icon = "🥇 "
    elif not has_landing:
        status_icon = "🛠️ "
    else:
        recent_commits = get_commit_count_last_7_days(project_dir)
        if recent_commits >= 3:
            status_icon = "🔥🔥 "
        elif recent_commits >= 1:
            status_icon = "🔥 "
        else:
            status_icon = ""

    # Generate the HTML (bubble style)
    muted_class = " muted" if not has_landing else ""
    pinned_class = " pinned" if pinned else ""

    html = f'''      <div class="bubble{muted_class}{pinned_class}" data-name="{project_name}" {style}>
        <div class="name">{status_icon}{project_name}</div>
        <div class="desc">{description}</div>
        <div class="actions">
          <a href="{open_url}" target="_blank" rel="noopener noreferrer"><button>Open</button></a>
          <a href="{github_url}" target="_blank" rel="noopener noreferrer"><button>Repo</button></a>
        </div>
      </div>'''

    return html


def get_all_projects() -> list[tuple[Path, datetime]]:
    """Get all project directories sorted by modification date"""
    projects = []

    for item in GITHUB_DIR.iterdir():
        if not item.is_dir():
            continue
        # Skip hidden directories and special dirs
        if item.name.startswith('.') or item.name.startswith('clawd'):
            continue
        # Skip big0time itself
        if item.name == "big0time":
            continue

        mod_date = get_project_modification_date(item)
        projects.append((item, mod_date))

    # Sort by modification date (newest first)
    projects.sort(key=lambda x: x[1], reverse=True)

    return projects


def update_index_html(force_screenshot: bool = False):
    """Update the index.html with current project list"""

    print("Scanning projects...")
    os.makedirs(SCREENSHOT_DIR, exist_ok=True)
    all_projects = get_all_projects()
    
    # Separate pinned projects
    pinned_projs = [p for p in all_projects if p[0].name in PINNED_PROJECTS]
    other_projs = [p for p in all_projects if p[0].name not in PINNED_PROJECTS]
    
    # Sort pinned projects according to the PINNED_PROJECTS list
    pinned_projs.sort(key=lambda x: PINNED_PROJECTS.index(x[0].name))

    print(f"Found {len(all_projects)} projects ({len(pinned_projs)} pinned).")

    # Generate pinned project HTML
    pinned_entries = []
    if pinned_projs:
        pinned_entries.append('<div class="grid-title">Pinned</div>')
        for project_dir, mod_date in pinned_projs:
            project_name = project_dir.name
            print(f"  - {project_name} (pinned)")
            html = generate_project_html(project_name, project_dir, pinned=True, force_screenshot=force_screenshot)
            pinned_entries.append(html)

    # Generate other project HTML
    other_entries = []
    if other_projs:
        other_entries.append('<div class="grid-title">All Projects</div>')
        for project_dir, mod_date in other_projs:
            project_name = project_dir.name
            print(f"  - {project_name}")
            html = generate_project_html(project_name, project_dir, force_screenshot=force_screenshot)
            other_entries.append(html)

    # Read the template
    template = INDEX_HTML.read_text(encoding='utf-8')

    # Find the menu start and end markers
    menu_start = '<!-- MENU START -->'
    menu_end = '<!-- MENU END -->'

    start_idx = template.find(menu_start)
    end_idx = template.find(menu_end)

    if start_idx == -1 or end_idx == -1:
        print("ERROR: Could not find menu markers in index.html")
        return

    # Build new template
    grid_html = '\n'.join(pinned_entries) + '\n' + '\n'.join(other_entries)
    
    new_template = (
        template[:start_idx + len(menu_start)] +
        f'\n    <div class="grid">\n{grid_html}\n    </div>' +
        template[end_idx:]
    )

    # Update the index
    INDEX_HTML.write_text(new_template, encoding='utf-8')

    print(f"\nUpdated {INDEX_HTML}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Big0Time Project Sync Script")
    parser.add_argument("--force-screenshot", action="store_true", help="Force new screenshots to be captured, even if recent.")
    args = parser.parse_args()

    print("=" * 50)
    print("Big0Time Project Sync")
    print("=" * 50)

    # Verify paths exist
    if not GITHUB_DIR.exists():
        print(f"ERROR: GitHub directory not found: {GITHUB_DIR}")
        return

    if not big0time_DIR.exists():
        print(f"ERROR: big0time directory not found: {big0time_DIR}")
        return

    if not UNDER_CONSTRUCTION.exists():
        print(f"ERROR: under-construction.html not found: {UNDER_CONSTRUCTION}")
        return

    update_index_html(force_screenshot=args.force_screenshot)

    print("\nSync complete!")


if __name__ == "__main__":
    main()
