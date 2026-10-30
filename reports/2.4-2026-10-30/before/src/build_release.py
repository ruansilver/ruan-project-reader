#!/usr/bin/env python3
"""Development-only release builder. Run tests and semantic acceptance before publication.

python3 src/build_release.py --build   # tests, staged copy, rollback on replacement failure
python3 src/build_release.py --verify  # manifest + source consistency, no writes
"""
import argparse
import ast
import fnmatch
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

SKILL = "ruan-project-reader"
EXCLUDED = (".gitkeep", "__pycache__", "*.pyc", "*.pyo", ".work", "tests", ".DS_Store")


def normalized(data):
    try:
        data.decode("utf-8")
    except UnicodeDecodeError:
        return data
    return data.replace(b"\r\n", b"\n")


def digest(data):
    return hashlib.sha256(data).hexdigest()


def artifact_hash(directory, exclude_development=False):
    rows = []
    for path in sorted(directory.rglob("*"), key=lambda p: p.relative_to(directory).as_posix()):
        if exclude_development and any(fnmatch.fnmatch(part, pattern) for part in path.relative_to(directory).parts for pattern in EXCLUDED):
            continue
        if path.is_symlink():
            raise ValueError(f"成品不得包含符号链接：{path}")
        if path.is_file():
            rows.append(path.relative_to(directory).as_posix() + "\0" + digest(normalized(path.read_bytes())) + "\n")
    return digest("".join(rows).encode("utf-8"))


def frontmatter(path):
    text = path.read_text(encoding="utf-8-sig")
    match = re.match(r"\A---\n(.*?)\n---(?:\n|$)", text, re.S)
    if not match:
        raise ValueError(f"缺少可解析 frontmatter：{path}")
    data = {}
    for line in match.group(1).splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        pair = re.fullmatch(r"([A-Za-z_][\w-]*):\s*(.*?)\s*", line)
        if not pair or pair[1] in data:
            raise ValueError(f"frontmatter 冲突或无法解析：{path}: {line}")
        value = pair[2]
        if value.startswith(('"', "'")):
            if len(value) < 2 or value[-1] != value[0]:
                raise ValueError(f"frontmatter 引号不完整：{path}")
            value = value[1:-1]
        data[pair[1]] = value
    return data


def select_target(root):
    approved, seen = [], set()
    for path in sorted((root / "design/versions").glob("*.md")):
        meta = frontmatter(path)
        version, status = meta.get("version"), meta.get("status")
        if not version or not re.fullmatch(r"(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)", version):
            raise ValueError(f"无法解析三段版本：{path}")
        if path.stem != version or version in seen:
            raise ValueError(f"文件名／版本冲突或重复：{path}")
        if status not in ("approved", "draft"):
            raise ValueError(f"未知设计状态：{path}")
        seen.add(version)
        if status == "approved":
            approved.append((tuple(map(int, version.split("."))), version, path))
    if not approved:
        raise ValueError("尚无可开发的已确认版本，不能自动发布")
    _, version, path = max(approved)
    return version, path


def verify_release(root):
    install = root / "install"
    manifest = install / ".release.json"
    if not manifest.exists():
        if install.exists() and any(install.iterdir()):
            raise ValueError("install 非空但缺少发布清单；停止自动发布")
        return None
    data = json.loads(manifest.read_text(encoding="utf-8"))
    if set(data) != {"version", "design_document", "skill_name", "design_sha256", "artifact_sha256"}:
        raise ValueError("发布清单字段不完整或有冲突")
    if data["skill_name"] != SKILL or data["design_document"] != f"design/versions/{data['version']}.md":
        raise ValueError("发布清单版本／设计路径冲突")
    design = root / data["design_document"]
    meta = frontmatter(design)
    if meta.get("version") != data["version"] or meta.get("status") != "approved":
        raise ValueError("已发布设计元数据不一致")
    if digest(design.read_bytes().replace(b"\r\n", b"\n")) != data["design_sha256"]:
        raise ValueError("已发布设计哈希不一致；停止自动发布")
    if not (install / SKILL / "SKILL.md").is_file() or artifact_hash(install / SKILL) != data["artifact_sha256"]:
        raise ValueError("已发布成品哈希不一致；停止自动发布")
    return data


def validate_source(source, version):
    entry = source / "SKILL.md"
    text = entry.read_text(encoding="utf-8")
    if not text.startswith("---\n") or not re.search(r"(?m)^name: ruan-project-reader$", text):
        raise ValueError("缺少有效业务 Skill 入口")
    if not re.search(r"(?m)^description: .+", text) or f'version: "{version}"' not in text.split("---", 2)[1]:
        raise ValueError("Skill 描述或版本与目标不一致")
    for p in source.rglob("*"):
        if p.is_symlink():
            raise ValueError(f"开发源含符号链接：{p}")
        if p.is_file() and p.suffix == ".py":
            ast.parse(p.read_text(encoding="utf-8"), filename=str(p))
        if p.is_file() and p.suffix == ".md":
            body = re.sub(r"(?ms)^\s*(`{3,}|~{3,})[^\n]*\n.*?^\s*\1\s*$", "", p.read_text(encoding="utf-8"))
            # Output templates intentionally link to files that will be created in the knowledge base.
            if "templates" not in p.relative_to(source).parts:
                for raw in re.findall(r"\[[^\]\n]+\]\(([^)\n]+)\)", body):
                    if "://" not in raw and not raw.startswith("#") and not (p.parent / raw.split("#")[0]).is_file():
                        raise ValueError(f"Skill 资源断链：{p}: {raw}")


def publish(root):
    version, design = select_target(root)
    old = verify_release(root)
    source = root / "src" / SKILL
    validate_source(source, version)
    work = root / "src/.work"
    work.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="release-", dir=work) as tmp:
        staging = Path(tmp) / "install"
        staging.mkdir()
        shutil.copytree(source, staging / SKILL, ignore=shutil.ignore_patterns(*EXCLUDED))
        data = dict(version=version, design_document=design.relative_to(root).as_posix(), skill_name=SKILL,
                    design_sha256=digest(design.read_bytes().replace(b"\r\n", b"\n")),
                    artifact_sha256=artifact_hash(staging / SKILL))
        (staging / ".release.json").write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        if old == data:
            return data, False
        backup = Path(tmp) / "previous-install"
        install = root / "install"
        if install.exists():
            os.replace(install, backup)
        try:
            os.replace(staging, install)
            verify_release(root)
        except BaseException:
            if install.exists():
                shutil.rmtree(install)
            if backup.exists():
                os.replace(backup, install)
            raise
    return data, True


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--build", action="store_true")
    action.add_argument("--verify", action="store_true")
    args = parser.parse_args()
    root = Path(__file__).resolve().parent.parent
    try:
        if args.build:
            env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
            subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", str(root / "src/tests")], check=True, cwd=root, env=env)
            data, changed = publish(root)
            print(json.dumps({"built": changed, **data}, ensure_ascii=False, indent=2))
        else:
            data = verify_release(root)
            if data is None:
                raise ValueError("尚无正式成品")
            version, _ = select_target(root)
            if version != data["version"]:
                raise ValueError(f"目标 {version} 与已发布 {data['version']} 不同")
            if artifact_hash(root / "src" / SKILL, exclude_development=True) != data["artifact_sha256"]:
                raise ValueError("开发源的交付文件与成品不一致")
            print(f"通过：目标与已发布 {version}；设计、成品哈希及源文件一致")
    except (OSError, ValueError, subprocess.CalledProcessError) as exc:
        print(f"失败：{exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
