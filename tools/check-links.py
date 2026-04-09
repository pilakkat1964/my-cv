#!/usr/bin/env python3
"""
check-links.py — Pre-publish link checker for the Jekyll blog.

What it does:
  1. Collects slugs of all PUBLISHED posts (_posts/) and all DRAFTS (_drafts/).
  2. Scans every published post for internal Markdown links that point to
     /posts/<slug>/ where <slug> is a DRAFT (not published yet).
  3. Replaces each broken link  [label](/posts/slug/)
     with plain text             label (coming soon)
  4. Reports what was changed and what is still a potential issue.
  5. Optionally runs htmlproofer against a fresh local build.

Usage:
  ./tools/check-links.py                # check + auto-fix only
  ./tools/check-links.py --htmlproofer  # check + fix + build + htmlproofer
  ./tools/check-links.py --dry-run      # show what would change, do nothing
"""

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path

# ── Configuration ────────────────────────────────────────────────────────────

REPO_ROOT   = Path(__file__).resolve().parent.parent
POSTS_DIR   = REPO_ROOT / "_posts"
DRAFTS_DIR  = REPO_ROOT / "_drafts"
SITE_DIR    = REPO_ROOT / "_site"
CACHE_DIR   = REPO_ROOT / ".jekyll-cache"

# Matches Markdown links whose href starts with /posts/
# Group 1 = label text, Group 2 = slug  e.g. /posts/rust-on-esp32/
INTERNAL_LINK_RE = re.compile(r'\[([^\]]+)\]\(/posts/([^/)]+)/?[^)]*\)')

# ── Helpers ──────────────────────────────────────────────────────────────────

def slug_from_filename(filename: str) -> str:
    """
    Derive the Jekyll URL slug from a post filename.
    '2026-02-15-rust-on-esp32.md'  →  'rust-on-esp32'
    Strips the leading YYYY-MM-DD- date prefix and the .md extension.
    """
    name = Path(filename).stem          # remove .md
    # Remove optional leading date prefix
    name = re.sub(r'^\d{4}-\d{2}-\d{2}-', '', name)
    return name


def collect_slugs(directory: Path) -> dict[str, Path]:
    """Return {slug: filepath} for all .md files in a directory."""
    slugs = {}
    if directory.is_dir():
        for f in directory.glob("*.md"):
            slugs[slug_from_filename(f.name)] = f
    return slugs


def run(cmd: list[str], check: bool = True) -> subprocess.CompletedProcess:
    """Run a shell command, streaming output to the terminal."""
    print(f"\n$ {' '.join(cmd)}")
    return subprocess.run(cmd, cwd=REPO_ROOT, check=check)

# ── Core logic ────────────────────────────────────────────────────────────────

def find_and_fix_broken_links(
    published: dict[str, Path],
    drafts: dict[str, Path],
    dry_run: bool,
) -> list[tuple[Path, str, str, str]]:
    """
    Scan all published posts for links to unpublished slugs.
    Returns a list of (file, label, slug, status) tuples for reporting.
    'status' is one of: 'fixed' | 'draft' | 'unknown'
    """
    report = []

    for post_path in POSTS_DIR.glob("*.md"):
        original = post_path.read_text(encoding="utf-8")
        updated  = original

        for match in INTERNAL_LINK_RE.finditer(original):
            label  = match.group(1)
            slug   = match.group(2)
            full   = match.group(0)   # the whole [label](/posts/slug/) token

            if slug in published:
                continue              # link is fine

            status = "draft" if slug in drafts else "unknown"

            replacement = f"{label} *(coming soon)*"
            updated = updated.replace(full, replacement, 1)
            report.append((post_path, label, slug, status))

            action = "[dry-run]" if dry_run else "[fixed]"
            print(
                f"  {action} {post_path.name}\n"
                f"           link : {full}\n"
                f"           →    : {replacement}\n"
                f"           slug is a {'draft' if status == 'draft' else 'UNKNOWN post'}\n"
            )

        if updated != original and not dry_run:
            post_path.write_text(updated, encoding="utf-8")

    return report


def clean_build() -> None:
    """Remove .jekyll-cache and _site, then do a fresh build."""
    print("\n==> Cleaning previous build...")
    for d in (CACHE_DIR, SITE_DIR):
        if d.exists():
            import shutil
            shutil.rmtree(d)
            print(f"    removed {d.relative_to(REPO_ROOT)}/")

    print("\n==> Building site...")
    run(["bundle", "exec", "jekyll", "build"])


def run_htmlproofer() -> bool:
    """Run htmlproofer; return True if it passes."""
    print("\n==> Running htmlproofer...")
    result = run(
        [
            "bundle", "exec", "htmlproofer", str(SITE_DIR),
            "--disable-external",
            "--ignore-urls",
            "/^http:\\/\\/127\\.0\\.0\\.1/,"
            "/^http:\\/\\/0\\.0\\.0\\.0/,"
            "/^http:\\/\\/localhost/",
        ],
        check=False,
    )
    return result.returncode == 0

# ── Entry point ───────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--dry-run",      action="store_true", help="Show what would change without modifying files")
    parser.add_argument("--htmlproofer",  action="store_true", help="Also run a clean build + htmlproofer")
    args = parser.parse_args()

    print("=" * 60)
    print("  Jekyll internal-link checker")
    print("=" * 60)

    published = collect_slugs(POSTS_DIR)
    drafts    = collect_slugs(DRAFTS_DIR)

    print(f"\nPublished posts : {len(published)}")
    print(f"Drafts          : {len(drafts)}")

    print("\n── Checking internal /posts/ links in published posts ──\n")
    issues = find_and_fix_broken_links(published, drafts, dry_run=args.dry_run)

    if not issues:
        print("  ✓ No broken internal links found.")
    else:
        verb = "would be" if args.dry_run else "were"
        print(f"\n  {len(issues)} broken link(s) {verb} {'flagged' if args.dry_run else 'fixed'}.")
        if args.dry_run:
            print("  Re-run without --dry-run to apply fixes.")

    if args.htmlproofer:
        clean_build()
        ok = run_htmlproofer()
        if ok:
            print("\n  ✓ htmlproofer passed — site is ready to deploy.")
        else:
            print("\n  ✗ htmlproofer reported failures (see output above).")
            sys.exit(1)
    else:
        print(
            "\nTip: run with --htmlproofer to also do a clean build and\n"
            "     validate all internal links with htmlproofer."
        )

    print()


if __name__ == "__main__":
    main()
