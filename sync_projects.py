#!/usr/bin/env python3
"""
Big0Time Project Sync Script

Scans the GitHub projects directory and updates the big0time index.html with:
- Projects sorted by modification date (newest first)
- Grayed out text for projects without landing pages
- Fire icon (🔥) for recently active projects (modified in last 7 days)
- Lightning icon (⚡) for GitHub Actions workflow-deployed projects
- Globe icon (🌐) for static GitHub Pages deployed projects
- Copies under-construction.html to projects without landing pages
- Supports both static direct hosting and GitHub Actions workflow hosting
"""

import os
import re
import json
import shutil
import subprocess
from pathlib import Path
from datetime import datetime, timedelta

# Configuration
SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_GITHUB = Path("/Volumes/Clay/GitHub")
GITHUB_DIR = DEFAULT_GITHUB if DEFAULT_GITHUB.exists() else SCRIPT_DIR.parent
big0time_DIR = SCRIPT_DIR
UNDER_CONSTRUCTION = big0time_DIR / "under-construction.html"
INDEX_HTML = big0time_DIR / "index.html"
RECENT_DAYS = 7  # Projects modified within this many days get fire icon

# Landing page patterns to check (in order of preference)
LANDING_PAGES = [
    "index.html",
    "index.htm",
    "README.html",
    "main.html",
    "app.html",
    "public/index.html",
]

# Pinned projects configuration (name, screenshot relative path if any)
PINNED_PROJECTS = [
    ("ButterPass", "resources/screenshots/butterpass.png", "https://polerix.github.io/ButterPass-95/"),
    ("security-adventure", "resources/screenshots/security-adventure.png", "https://polerix.github.io/security-adventure/"),
    ("vax-console-sim", "resources/screenshots/vax-console-sim.png", "https://polerix.github.io/vax-console-sim/"),
    ("kraemeverse-wiki", "resources/screenshots/kraemeverse-wiki.png", "https://polerix.github.io/kraemeverse-wiki/"),
    ("tornado-cones", "resources/screenshots/tornado-cones.png", "https://polerix.github.io/tornado-cones/"),
    ("satans-spreadsheet", "resources/screenshots/satans-spreadsheet.png", "https://polerix.github.io/satans-spreadsheet/"),
    ("hackers-team", "resources/screenshots/hackers-team.png", "https://polerix.github.io/hackers-team/"),
    ("sandrine-portfolio", "resources/screenshots/sandrine-portfolio.png", "https://polerix.github.io/sandrine-portfolio/"),
    ("mobius-farm-II", "resources/screenshots/mobius-farm-ii.png", "https://polerix.github.io/mobius-farm-ii/"),
    ("aetherstones-council-of-green-point", "resources/screenshots/aetherstones-council-of-green-point.png", "https://polerix.github.io/aetherstones-council-of-green-point/"),
    ("touski", "resources/screenshots/touski.png", "https://polerix.github.io/touski/"),
    ("neutral-zero", "resources/screenshots/neutral-zero.png", "https://polerix.github.io/neutral-zero/"),
    ("pixel-duel-ii", "resources/screenshots/pixel-duel-ii.png", "https://polerix.github.io/pixel-duel-ii/"),
    ("pixel-duel", "resources/screenshots/pixel-duel.png", "https://polerix.github.io/pixel-duel/"),
]


def get_project_description(project_dir: Path) -> str:
    """Extract project description from README.md or package.json"""
    readme = project_dir / "README.md"
    if readme.exists():
        try:
            content = readme.read_text(encoding='utf-8', errors='ignore')
            lines = content.strip().split('\n')
            for line in lines[1:]:
                line = line.strip()
                if line and not line.startswith('#'):
                    desc = line.strip().lstrip('- ').lstrip('* ')
                    if len(desc) > 60:
                        desc = desc[:57] + "..."
                    return desc
        except Exception:
            pass

    pkg_json = project_dir / "package.json"
    if pkg_json.exists():
        try:
            pkg = json.loads(pkg_json.read_text(encoding='utf-8', errors='ignore'))
            desc = pkg.get("description", "")
            if desc and len(desc) > 60:
                desc = desc[:57] + "..."
            return desc
        except Exception:
            pass

    return ""


def get_github_url(project_name: str) -> str:
    """Generate GitHub URL from project name"""
    if project_name == "ButterPass":
        return "https://github.com/polerix/ButterPass-95"
    return f"https://github.com/polerix/{project_name}"


def get_hosting_info(project_name: str, project_dir: Path) -> dict:
    """
    Inspect project directory and GitHub API to determine hosting type:
    - active_pages (legacy or workflow)
    - has_static_landing
    - has_workflow_build
    """
    has_static = False
    for landing in LANDING_PAGES:
        if (project_dir / landing).exists():
            has_static = True
            break

    wf_dir = project_dir / ".github" / "workflows"
    has_workflow = wf_dir.exists() and any(wf_dir.iterdir())
    has_pkg = (project_dir / "package.json").exists()

    pages_data = None
    try:
        res = subprocess.run(
            ["gh", "api", f"repos/polerix/{project_name}/pages"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if res.returncode == 0 and res.stdout.strip():
            pages_data = json.loads(res.stdout)
    except Exception:
        pass

    if pages_data:
        btype = pages_data.get("build_type", "legacy")
        url = pages_data.get("html_url") or f"https://polerix.github.io/{project_name}/"
        return {
            "has_landing": True,
            "hosting_type": btype, # 'legacy' or 'workflow'
            "deployed_url": url,
            "is_active": True
        }
    elif has_static:
        return {
            "has_landing": True,
            "hosting_type": "legacy",
            "deployed_url": f"https://polerix.github.io/{project_name}/",
            "is_active": True
        }
    elif has_workflow or has_pkg:
        return {
            "has_landing": True,
            "hosting_type": "workflow",
            "deployed_url": f"https://polerix.github.io/{project_name}/",
            "is_active": True
        }
    else:
        copy_under_construction(project_name)
        return {
            "has_landing": False,
            "hosting_type": "none",
            "deployed_url": f"https://polerix.github.io/{project_name}/under-construction.html",
            "is_active": False
        }


def get_project_modification_date(project_dir: Path) -> datetime:
    """Get the most recent modification date via git or stat"""
    latest_date = datetime(1970, 1, 1)

    git_dir = project_dir / ".git"
    if git_dir.exists():
        try:
            result = subprocess.run(
                ["git", "log", "-1", "--format=%ct"],
                cwd=project_dir,
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0 and result.stdout.strip():
                timestamp = int(result.stdout.strip())
                return datetime.fromtimestamp(timestamp)
        except Exception:
            pass

    try:
        mtime = datetime.fromtimestamp(project_dir.stat().st_mtime)
        return max(latest_date, mtime)
    except Exception:
        pass

    return latest_date


def is_recently_modified(project_dir: Path) -> bool:
    """Check if project was modified in the last RECENT_DAYS days"""
    mod_date = get_project_modification_date(project_dir)
    return datetime.now() - mod_date < timedelta(days=RECENT_DAYS)


def copy_under_construction(project_name: str) -> str:
    """Copy under-construction.html to a project directory"""
    project_dir = GITHUB_DIR / project_name
    if not project_dir.exists():
        return "under-construction.html"
    dest = project_dir / "under-construction.html"

    if not dest.exists() and UNDER_CONSTRUCTION.exists():
        try:
            shutil.copy2(UNDER_CONSTRUCTION, dest)
            print(f"  Copied under-construction.html to {project_name}")
        except Exception as e:
            print(f"  Warning: could not copy under-construction.html to {project_name}: {e}")

    return "under-construction.html"


def generate_project_html(project_name: str, project_dir: Path) -> str:
    """Generate HTML for a single project entry"""

    h_info = get_hosting_info(project_name, project_dir)
    is_recent = is_recently_modified(project_dir)
    description = get_project_description(project_dir)

    description = re.sub(r'<[^>]+>', '', description)
    description = description.replace('**', '').replace('\\u', '').strip()
    if len(description) > 80:
        description = description[:77] + '...'

    open_url = h_info["deployed_url"]
    github_url = get_github_url(project_name)

    icons = ""
    if is_recent:
        icons += "🔥 "
    if h_info["hosting_type"] == "workflow":
        icons += "⚡ "

    has_landing = h_info["has_landing"]
    muted_class = " muted" if not has_landing else ""

    html = f'''      <div class="bubble{muted_class}" data-name="{project_name}">
        <div class="inner-glow"></div>
        <div class="light-spot"></div>
        <div class="name">{icons}{project_name}</div>
        <div class="desc">{description}</div>
        <div class="actions">
          <a href="{open_url}" target="_blank" rel="noopener noreferrer"><button>Open</button></a>
          <a href="{github_url}" target="_blank" rel="noopener noreferrer"><button>Repo</button></a>
        </div>
      </div>'''

    return html


def generate_pinned_html(pinned_list: list[tuple[str, str, str]], projects_dict: dict) -> str:
    """Generate HTML for pinned projects section"""
    entries = []
    for name, screenshot, default_url in pinned_list:
        p_dir = GITHUB_DIR / name
        if not p_dir.exists():
            for p_name, (path, mdate) in projects_dict.items():
                if p_name.lower() == name.lower():
                    p_dir = path
                    break

        description = get_project_description(p_dir) if p_dir.exists() else ""
        description = re.sub(r'<[^>]+>', '', description).replace('**', '').replace('\\u', '').strip()
        if len(description) > 80:
            description = description[:77] + '...'
            
        open_url = default_url
        if p_dir.exists():
            h_info = get_hosting_info(name, p_dir)
            open_url = h_info["deployed_url"]

        github_url = get_github_url(name)

        bg_style = f' style="--bg-image: url({screenshot});"' if screenshot else ''

        entries.append(f'''      <div class="bubble pinned" data-name="{name}"{bg_style}>
        <div class="name">🥇 {name}</div>
        <div class="desc">{description}</div>
        <div class="actions">
          <a href="{open_url}" target="_blank" rel="noopener noreferrer"><button>Open</button></a>
          <a href="{github_url}" target="_blank" rel="noopener noreferrer"><button>Repo</button></a>
        </div>
      </div>''')

    return '\n'.join(entries)


def get_all_projects() -> list[tuple[Path, datetime]]:
    """Get all project directories sorted by modification date"""
    projects = []

    for item in GITHUB_DIR.iterdir():
        if not item.is_dir():
            continue
        if item.name.startswith('.') or item.name.startswith('clawd'):
            continue
        if item.name == "big0time":
            continue

        mod_date = get_project_modification_date(item)
        projects.append((item, mod_date))

    projects.sort(key=lambda x: x[1], reverse=True)
    return projects


def update_index_html():
    """Update the index.html with current project list"""

    print(f"Scanning projects in {GITHUB_DIR}...")
    projects = get_all_projects()
    print(f"Found {len(projects)} projects")

    projects_dict = {p[0].name: p for p in projects}

    # Generate Pinned Projects Section
    pinned_html = generate_pinned_html(PINNED_PROJECTS, projects_dict)

    # Generate All Projects Grid Entries
    project_entries = []
    for project_dir, mod_date in projects:
        project_name = project_dir.name
        print(f"  {project_name}: {mod_date.strftime('%Y-%m-%d')}", end="")

        h_info = get_hosting_info(project_name, project_dir)
        is_recent = is_recently_modified(project_dir)

        if not h_info["has_landing"]:
            print(" [no landing]", end="")
        else:
            print(f" [{h_info['hosting_type']}]", end="")
        if is_recent:
            print(" [recent]", end="")

        print()

        html = generate_project_html(project_name, project_dir)
        project_entries.append(html)

    template = INDEX_HTML.read_text(encoding='utf-8')

    menu_start = '<!-- MENU START -->'
    menu_end = '<!-- MENU END -->'

    start_idx = template.find(menu_start)
    end_idx = template.find(menu_end)

    if start_idx == -1 or end_idx == -1:
        print("ERROR: Could not find menu markers in index.html")
        return

    new_menu_content = (
        '\n    <div class="grid">' +
        '\n<div class="grid-title">Pinned</div>\n' +
        pinned_html +
        '\n<div class="grid-title">All Projects</div>\n' +
        '\n'.join(project_entries) +
        '\n    </div>'
    )

    new_template = (
        template[:start_idx + len(menu_start)] +
        new_menu_content +
        template[end_idx:]
    )

    INDEX_HTML.write_text(new_template, encoding='utf-8')
    print(f"\nSuccessfully updated {INDEX_HTML}")


def main():
    """Main entry point"""
    print("=" * 50)
    print("Big0Time Project Sync")
    print("=" * 50)

    if not GITHUB_DIR.exists():
        print(f"ERROR: GitHub directory not found: {GITHUB_DIR}")
        return

    if not big0time_DIR.exists():
        print(f"ERROR: big0time directory not found: {big0time_DIR}")
        return

    update_index_html()
    print("\nSync complete!")


if __name__ == "__main__":
    main()
