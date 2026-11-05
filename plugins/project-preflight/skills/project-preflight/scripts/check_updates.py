"""Read-only GitHub update checks. Requires Python 3 and authenticated gh CLI."""
import argparse
import json
from pathlib import Path
import subprocess
import sys
from urllib.parse import quote

COLLECTION = "TreasureGooldove/personal-skills"

def github_api(path):
    try:
        result = subprocess.run(
            ["gh", "api", path], capture_output=True, text=True,
            encoding="utf-8", timeout=30,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise RuntimeError(f"GitHub CLI unavailable or timed out: {exc}") from exc
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or "GitHub request failed")
    return json.loads(result.stdout)

def check_repo(repo, baseline, api=github_api):
    latest = api(f"repos/{repo}/commits/HEAD")["sha"]
    result = {"repository": repo, "baseline": baseline, "latest": latest}
    if not baseline:
        return dict(result, status="unknown_baseline")
    if latest == baseline:
        return dict(result, status="current")
    compare = api(f"repos/{repo}/compare/{quote(baseline, safe='')}...{latest}?per_page=100")
    if compare["status"] != "ahead":
        return dict(result, status=compare["status"], url=compare.get("html_url"))
    return dict(
        result, status="updated", count=compare["ahead_by"],
        commits=[c["commit"]["message"].splitlines()[0] for c in compare.get("commits", [])][-3:],
        files=[f["filename"] for f in compare.get("files", [])][:5],
        url=compare["html_url"],
    )

def check_all(items, api=github_api):
    results = []
    for name, repo, baseline in items:
        try:
            result = check_repo(repo, baseline, api)
        except (RuntimeError, KeyError, ValueError) as exc:
            result = {"repository": repo, "status": "error", "error": str(exc)}
        results.append(dict(result, name=name))
    return results

def local_collection_base():
    # An installed plugin may live inside another project's Git checkout.
    # Only infer a baseline from this collection's own directory structure.
    for parent in Path(__file__).resolve().parents:
        if (parent / ".git").exists() and (parent / "upstream-lock.json").exists() and (parent / ".agents/plugins/marketplace.json").exists():
            proc = subprocess.run(["git", "-C", str(parent), "rev-parse", "HEAD"],
                                  capture_output=True, text=True, timeout=10)
            if proc.returncode == 0:
                return proc.stdout.strip()
    return None

def render(results):
    labels = {"current": "已是最新", "updated": "有更新", "unknown_baseline": "本地版本未知",
              "diverged": "历史已分叉，需人工核对", "behind": "本地基线领先远端，需核对",
              "identical": "内容一致", "error": "未能检查"}
    lines = ["技能更新检查（只读，不自动更新）"]
    for row in results:
        lines.append(f"- {row['name']}：{labels.get(row['status'], row['status'])}")
        if row["status"] == "updated":
            lines.append(f"  新增 {row['count']} 个提交；提交标题摘录（最多 3 条）：")
            lines.extend(f"  • {title}" for title in row["commits"])
            if row["files"]:
                lines.append("  涉及文件（最多 5 项）：" + "、".join(row["files"]))
        elif row["status"] == "unknown_baseline":
            lines.append(f"  远端最新 {row['latest'][:7]}；无法判断当前安装副本是否落后。")
        elif row["status"] == "error":
            lines.append("  " + row["error"])
        if row.get("url"):
            lines.append("  " + row["url"])
    return "\n".join(lines)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lock", type=Path, default=Path(__file__).resolve().parents[1] / "references/upstream-lock.json")
    parser.add_argument("--collection-base", help="Installed collection revision, when known")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable results")
    args = parser.parse_args()
    try:
        lock = json.loads(args.lock.read_text(encoding="utf-8-sig"))
        base = args.collection_base or local_collection_base()
        items = [("personal-skills", COLLECTION, base)]
        for row in lock:
            repo = row["repository"].removeprefix("https://github.com/").removesuffix(".git").rstrip("/")
            if len(repo.split("/")) != 2:
                raise ValueError(f"Invalid GitHub repository: {repo}")
            items.append((row["name"], repo, row["commit"]))
    except (OSError, ValueError, KeyError, subprocess.SubprocessError) as exc:
        print(f"无法读取更新基线：{exc}", file=sys.stderr)
        return 1
    results = check_all(items)
    print(json.dumps(results, ensure_ascii=False, indent=2) if args.json else render(results))
    return 1 if any(r["status"] == "error" for r in results) else 0

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    raise SystemExit(main())
