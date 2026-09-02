#!/usr/bin/env python3
"""
Big0Time LCARS Project Sync Script

Scans the GitHub projects directory and updates big0time index.html with:
- Categorized LCARS sections:
  1. Pinned Core Systems
  2. Business & Enterprise Solutions
  3. Games & Interactive Simulations
  4. Funky Toys & Experimental Labs
- Automatic dual-hosting detection (Static Pages vs GitHub Actions Workflow)
- Live GitHub Pages API status verification
- Dynamic search & category filtering metadata
"""

import os
import re
import json
import shutil
import subprocess
import concurrent.futures
from pathlib import Path
from datetime import datetime, timedelta

# Configuration
SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_GITHUB = Path("/Volumes/Clay/GitHub")
GITHUB_DIR = DEFAULT_GITHUB if DEFAULT_GITHUB.exists() else SCRIPT_DIR.parent
big0time_DIR = SCRIPT_DIR
UNDER_CONSTRUCTION = big0time_DIR / "under-construction.html"
INDEX_HTML = big0time_DIR / "index.html"
RECENT_DAYS = 7

PAGES_CACHE = {}

LANDING_PAGES = [
    "index.html",
    "index.htm",
    "README.html",
    "main.html",
    "app.html",
    "public/index.html",
]

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

# Explicit Categorization Map for accuracy
CATEGORY_MAP = {
    # Business & Enterprise Relevance
    'security-adventure': 'business',
    'defrag-tool': 'business',
    'sandrine-portfolio': 'business',
    'vax-console-sim': 'business',
    'hackers-team': 'business',
    'bus-broadcaster': 'business',
    'bus-broadcaster-swift': 'business',
    'lucid-reader': 'business',
    'motion-tracker': 'business',
    'ytdl-gui': 'business',
    'eyephone': 'business',
    'streamliner': 'business',
    'OBSTriCloner': 'business',
    'RecordMonitor': 'business',
    'ServoSkull': 'business',
    'VK_Terminal': 'business',
    'vk_console': 'business',
    'PixelMonitor': 'business',
    'm314-tracker': 'business',
    'obs-projects': 'business',
    'apfel': 'business',
    'phantom': 'business',
    
    # Games & Interactive Simulations
    'neutral-zero': 'games',
    'mobius-farm-II': 'games',
    'mobius-farm': 'games',
    'pixel-duel-ii': 'games',
    'pixel-duel': 'games',
    'burger-time': 'games',
    'colonbo': 'games',
    'cosmic-brawler': 'games',
    'Cosmo Brawl': 'games',
    'Demon-Attack': 'games',
    'Flipside': 'games',
    'leap-frogs': 'games',
    'moof-patrol': 'games',
    'moofo': 'games',
    'moovers': 'games',
    'otv': 'games',
    'satans-spreadsheet': 'games',
    'tornado-cones': 'games',
    'tubbers': 'games',
    'bubalina': 'games',
    'BPM-Vending Pigs': 'games',
    'bpm-vending-pigs': 'games',
    'xenohive-gauntlet': 'games',
    'poop-boy': 'games',
    'petscii_game': 'games',
    'Drone Swarm Sim': 'games',
    'PORTS Back Panel Brawl': 'games',
    
    # Funky Toys & Experiments
    'ButterPass': 'toys',
    'ButterPass-95': 'toys',
    'aetherstones-council-of-green-point': 'toys',
    'touski': 'toys',
    'kraemeverse-wiki': 'toys',
    'ascii-lab': 'toys',
    'glitcher-app': 'toys',
    'greco-time': 'toys',
    'headroom': 'toys',
    'smrt': 'toys',
    'soul-forge': 'toys',
    'swarm-system-lab': 'toys',
    'c64-os': 'toys',
    'raspberry-pi-fallout': 'toys',
    'raspberry-pi-2b-commodore-1701-screen': 'toys',
    'payload-emulator-loop': 'toys',
    'blinkwell-observer': 'toys',
    'diffvg': 'toys',
    'tmp-nz': 'toys',
    'moo-shroom': 'toys',
    'maudlin-modellers': 'toys',
    'alien-hive': 'toys',
    'valkyr': 'toys',
    'HailMary': 'toys',
    'FunHaus': 'toys',
    'Gargoyle': 'toys',
    'Perambulators': 'toys'
}


def get_project_category(project_name: str) -> str:
    """Return category ('business', 'games', 'toys') for a given project"""
    if project_name in CATEGORY_MAP:
        return CATEGORY_MAP[project_name]
    
    # Keyword fallback
    lower = project_name.lower()
    if any(k in lower for k in ['tool', 'sec', 'doc', 'view', 'read', 'track', 'mon', 'sys', 'app', 'cli', 'bot']):
        return 'business'
    if any(k in lower for k in ['game', 'brawl', 'fight', 'play', 'race', 'farm', 'patrol', 'zero']):
        return 'games'
    return 'toys'


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


def get_repo_info(project_dir: Path, project_name: str) -> tuple[str, str, str, str]:
    """
    Extract exact (owner, repo_name, github_url, default_pages_url) from .git remote origin
    """
    git_dir = project_dir / ".git"
    remote_url = None
    if git_dir.exists():
        try:
            res = subprocess.run(
                ["git", "-C", str(project_dir), "remote", "get-url", "origin"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if res.returncode == 0:
                remote_url = res.stdout.strip()
        except Exception:
            pass

    owner = "polerix"
    repo_name = project_name

    if remote_url:
        m = re.search(r"github\.com[:/]([^/]+)/([^/\.]+)", remote_url)
        if m:
            owner = m.group(1)
            repo_name = m.group(2)

    url_safe_repo = repo_name.replace(" ", "-")
    github_url = f"https://github.com/{owner}/{url_safe_repo}"
    pages_url = f"https://polerix.github.io/{url_safe_repo}/" if owner.lower() == "polerix" else f"https://{owner}.github.io/{url_safe_repo}/"
    return owner, repo_name, github_url, pages_url


def get_github_url(project_name: str, project_dir: Path = None) -> str:
    if project_dir and project_dir.exists():
        _, _, github_url, _ = get_repo_info(project_dir, project_name)
        return github_url
    if project_name == "ButterPass":
        return "https://github.com/polerix/ButterPass-95"
    return f"https://github.com/polerix/{project_name}"


def prefetch_pages_info(project_dirs: list[Path]):
    global PAGES_CACHE
    def fetch_one(p_dir):
        if not (p_dir / ".git").exists():
            return p_dir.name, None
        owner, repo_name, _, _ = get_repo_info(p_dir, p_dir.name)
        try:
            res = subprocess.run(
                ["gh", "api", f"repos/{owner}/{repo_name}/pages"],
                capture_output=True,
                text=True,
                timeout=2
            )
            if res.returncode == 0 and res.stdout.strip():
                return p_dir.name, json.loads(res.stdout)
        except Exception:
            pass
        return p_dir.name, None

    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        results = executor.map(fetch_one, project_dirs)
        PAGES_CACHE = dict(results)


def get_hosting_info(project_name: str, project_dir: Path) -> dict:
    has_static = False
    for landing in LANDING_PAGES:
        if (project_dir / landing).exists():
            has_static = True
            break

    wf_dir = project_dir / ".github" / "workflows"
    has_workflow = wf_dir.exists() and any(wf_dir.iterdir())
    has_pkg = (project_dir / "package.json").exists()

    owner, repo_name, github_url, default_pages_url = get_repo_info(project_dir, project_name)

    pages_data = PAGES_CACHE.get(project_name)

    if pages_data:
        btype = pages_data.get("build_type", "legacy")
        url = pages_data.get("html_url") or default_pages_url
        return {
            "has_landing": True,
            "hosting_type": btype,
            "deployed_url": url,
            "is_active": True,
            "github_url": github_url
        }
    elif has_static:
        return {
            "has_landing": True,
            "hosting_type": "legacy",
            "deployed_url": default_pages_url,
            "is_active": True,
            "github_url": github_url
        }
    elif has_workflow or has_pkg:
        return {
            "has_landing": True,
            "hosting_type": "workflow",
            "deployed_url": default_pages_url,
            "is_active": True,
            "github_url": github_url
        }
    else:
        copy_under_construction(project_name)
        url_safe = repo_name.replace(" ", "-")
        under_const_url = f"https://polerix.github.io/{url_safe}/under-construction.html"
        return {
            "has_landing": False,
            "hosting_type": "none",
            "deployed_url": under_const_url,
            "is_active": False,
            "github_url": github_url
        }


def get_project_modification_date(project_dir: Path) -> datetime:
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
    mod_date = get_project_modification_date(project_dir)
    return datetime.now() - mod_date < timedelta(days=RECENT_DAYS)


def copy_under_construction(project_name: str) -> str:
    project_dir = GITHUB_DIR / project_name
    if not project_dir.exists():
        return "under-construction.html"
    dest = project_dir / "under-construction.html"

    if not dest.exists() and UNDER_CONSTRUCTION.exists():
        try:
            shutil.copy2(UNDER_CONSTRUCTION, dest)
        except Exception:
            pass

    return "under-construction.html"


def generate_card_html(project_name: str, project_dir: Path, idx_num: int) -> tuple[str, str]:
    """Generate LCARS styled card HTML and return (category, html)"""
    category = get_project_category(project_name)
    h_info = get_hosting_info(project_name, project_dir)
    is_recent = is_recently_modified(project_dir)
    description = get_project_description(project_dir)

    description = re.sub(r'<[^>]+>', '', description)
    description = description.replace('**', '').replace('\\u', '').strip()
    if len(description) > 80:
        description = description[:77] + '...'

    open_url = h_info["deployed_url"]
    github_url = h_info["github_url"]

    badge = ""
    if is_recent:
        badge += '<span class="lcars-tag tag-recent">🔥 ACTIVE</span> '
    if h_info["hosting_type"] == "workflow":
        badge += '<span class="lcars-tag tag-workflow">⚡ ACTIONS</span> '
    elif h_info["has_landing"]:
        badge += '<span class="lcars-tag tag-static">🌐 PAGES</span> '
    else:
        badge += '<span class="lcars-tag tag-muted">🚧 LAB</span> '

    has_landing = h_info["has_landing"]
    muted_class = " muted" if not has_landing else ""

    sys_id = f"LCARS-{category[:3].upper()}-{idx_num:03d}"

    html = f'''        <div class="bubble{muted_class}" data-category="{category}" data-name="{project_name.lower()}" data-search="{project_name.lower()} {description.lower()}">
          <div class="card-header">
            <span class="sys-id">{sys_id}</span>
            <div class="card-badges">{badge}</div>
          </div>
          <div class="name">{project_name}</div>
          <div class="desc">{description}</div>
          <div class="actions">
            <a href="{open_url}" target="_blank" rel="noopener noreferrer"><button class="lcars-btn open-btn">EXECUTE</button></a>
            <a href="{github_url}" target="_blank" rel="noopener noreferrer"><button class="lcars-btn repo-btn">REPOS</button></a>
          </div>
        </div>'''

    return category, html


def generate_pinned_html(pinned_list: list[tuple[str, str, str]], projects_dict: dict) -> str:
    entries = []
    for idx, (name, screenshot, default_url) in enumerate(pinned_list, 1):
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
        github_url = get_github_url(name, p_dir if p_dir.exists() else None)

        if p_dir.exists():
            h_info = get_hosting_info(name, p_dir)
            if h_info["has_landing"] and h_info["is_active"]:
                open_url = h_info["deployed_url"]
            elif not open_url:
                open_url = h_info["deployed_url"]
            github_url = h_info["github_url"]

        bg_style = f' style="--bg-image: url({screenshot});"' if screenshot else ''
        sys_id = f"LCARS-PRIORITY-{idx:02d}"

        entries.append(f'''        <div class="bubble pinned" data-category="pinned" data-name="{name.lower()}" data-search="{name.lower()} {description.lower()}"{bg_style}>
          <div class="card-header">
            <span class="sys-id">{sys_id}</span>
            <span class="lcars-tag tag-pinned">🥇 FEATURED</span>
          </div>
          <div class="name">{name}</div>
          <div class="desc">{description}</div>
          <div class="actions">
            <a href="{open_url}" target="_blank" rel="noopener noreferrer"><button class="lcars-btn open-btn">EXECUTE</button></a>
            <a href="{github_url}" target="_blank" rel="noopener noreferrer"><button class="lcars-btn repo-btn">REPOS</button></a>
          </div>
        </div>''')

    return '\n'.join(entries)


RENAMED_ALIASES = {
    'cosmo brawl': 'cosmic-brawler',
    'bpm-vending pigs': 'bpm-vending-pigs',
}


def get_all_projects() -> list[tuple[Path, datetime]]:
    all_dirs = [item for item in GITHUB_DIR.iterdir() if item.is_dir() and not item.name.startswith('.') and not item.name.startswith('clawd') and item.name != "big0time"]

    git_repos = {}
    for d in all_dirs:
        if (d / ".git").exists():
            git_repos[d.name.lower()] = d
            clean_d = d.name.lower().replace(" ", "-").replace("_", "-")
            git_repos[clean_d] = d
            _, rname, _, _ = get_repo_info(d, d.name)
            git_repos[rname.lower()] = d
            clean_r = rname.lower().replace(" ", "-").replace("_", "-")
            git_repos[clean_r] = d

    filtered_dirs = []
    for d in all_dirs:
        # If folder has no .git, skip it if a git repo with matching kebab/lowercase name or alias exists
        if not (d / ".git").exists():
            clean_name = d.name.lower().replace(" ", "-").replace("_", "-")
            alias = RENAMED_ALIASES.get(d.name.lower())
            if d.name.lower() in git_repos or clean_name in git_repos or (alias and alias in git_repos):
                continue
        filtered_dirs.append(d)

    projects = []
    for item in filtered_dirs:
        mod_date = get_project_modification_date(item)
        projects.append((item, mod_date))

    projects.sort(key=lambda x: x[1], reverse=True)
    return projects


def update_index_html():
    print(f"Scanning projects in {GITHUB_DIR}...")
    projects = get_all_projects()
    print(f"Found {len(projects)} projects")

    print("Prefetching live GitHub Pages deployment info...")
    prefetch_pages_info([p[0] for p in projects])

    projects_dict = {p[0].name: p for p in projects}

    # Categorized buckets
    cats = {'business': [], 'games': [], 'toys': []}
    
    idx_counter = 1
    for project_dir, mod_date in projects:
        project_name = project_dir.name
        cat, card_html = generate_card_html(project_name, project_dir, idx_counter)
        cats[cat].append(card_html)
        idx_counter += 1

    pinned_html = generate_pinned_html(PINNED_PROJECTS, projects_dict)

    # Build structured LCARS sections: Business Relevance FIRST, then Games, then Funky Toys
    lcars_body = f'''
    <!-- SECTION: PINNED CORE SYSTEMS -->
    <div class="lcars-section-header amber">
      <div class="lcars-elbow-top"></div>
      <div class="lcars-header-text">01 // FEATURED CORE SYSTEMS</div>
      <div class="lcars-header-bar"></div>
    </div>
    <div class="grid" id="grid-pinned">
{pinned_html}
    </div>

    <!-- SECTION: BUSINESS & ENTERPRISE RELEVANCE -->
    <div class="lcars-section-header gold" id="sec-business">
      <div class="lcars-elbow-top"></div>
      <div class="lcars-header-text">02 // BUSINESS & ENTERPRISE SOLUTIONS ({len(cats['business'])} NODES)</div>
      <div class="lcars-header-bar"></div>
    </div>
    <div class="grid" id="grid-business">
{chr(10).join(cats['business'])}
    </div>

    <!-- SECTION: GAMES & INTERACTIVE SIMULATIONS -->
    <div class="lcars-section-header blue" id="sec-games">
      <div class="lcars-elbow-top"></div>
      <div class="lcars-header-text">03 // GAMES & INTERACTIVE SIMULATIONS ({len(cats['games'])} NODES)</div>
      <div class="lcars-header-bar"></div>
    </div>
    <div class="grid" id="grid-games">
{chr(10).join(cats['games'])}
    </div>

    <!-- SECTION: FUNKY TOYS & EXPERIMENTAL LABS -->
    <div class="lcars-section-header purple" id="sec-toys">
      <div class="lcars-elbow-top"></div>
      <div class="lcars-header-text">04 // EXPERIMENTAL TOYS & LABS ({len(cats['toys'])} NODES)</div>
      <div class="lcars-header-bar"></div>
    </div>
    <div class="grid" id="grid-toys">
{chr(10).join(cats['toys'])}
    </div>
'''

    template = INDEX_HTML.read_text(encoding='utf-8')

    menu_start = '<!-- MENU START -->'
    menu_end = '<!-- MENU END -->'

    start_idx = template.find(menu_start)
    end_idx = template.find(menu_end)

    if start_idx == -1 or end_idx == -1:
        print("ERROR: Could not find menu markers in index.html")
        return

    new_template = (
        template[:start_idx + len(menu_start)] +
        lcars_body +
        '\n' +
        template[end_idx:]
    )

    INDEX_HTML.write_text(new_template, encoding='utf-8')
    print(f"\nSuccessfully updated {INDEX_HTML} with LCARS layout & categorization!")


def main():
    print("=" * 50)
    print("Big0Time LCARS Sync & Categorization")
    print("=" * 50)

    if not GITHUB_DIR.exists():
        print(f"ERROR: GitHub directory not found: {GITHUB_DIR}")
        return

    if not big0time_DIR.exists():
        print(f"ERROR: big0time directory not found: {big0time_DIR}")
        return

    update_index_html()
    print("\nLCARS Sync Complete!")


if __name__ == "__main__":
    main()
