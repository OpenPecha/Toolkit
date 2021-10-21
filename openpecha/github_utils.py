import os
import shutil
import time
from pathlib import Path
from uuid import uuid4

from git import Repo
from github import Github

org = None


def _get_openpecha_org(org_name, token):
    """OpenPecha github org singleton."""
    global org
    if org is None:
        g = Github(token)
        org = g.get_organization(org_name)
    return org


def get_github_repo(repo_name, org_name, token):
    org = _get_openpecha_org(org_name, token)
    repo = org.get_repo(repo_name)
    return repo


def create_github_repo(path, org_name, token):
    org = _get_openpecha_org(org_name, token)
    repo = org.create_repo(path.name)
    time.sleep(2)
    return repo._html_url.value


def commit(repo_path, message, not_includes, branch="master"):
    if isinstance(repo_path, Repo):
        repo = repo_path
    else:
        repo = Repo(repo_path)
    has_changed = False

    # add untrack fns
    for fn in repo.untracked_files:

        ignored = False
        for not_include_fn in not_includes:
            if not_include_fn in fn:
                ignored = True

        if ignored:
            continue

        if fn:
            repo.git.add(fn)
        if has_changed is False:
            has_changed = True

    # add modified fns
    if repo.is_dirty() is True:
        for fn in repo.git.diff(None, name_only=True).split("\n"):
            if fn:
                repo.git.add(fn)
            if has_changed is False:
                has_changed = True

    if has_changed is True:
        if not message:
            message = "Initial commit"
        repo.git.commit("-m", message)
        repo.git.push("origin", branch)


def create_local_repo(path, remote_url, org, token):
    if (path / ".git").is_dir():
        return Repo(path)
    else:
        repo = Repo.init(path)
        old_url = remote_url.split("//")
        auth_remote_url = f"{old_url[0]}//{org}:{token}@{old_url[1]}"
        repo.create_remote("origin", auth_remote_url)

        repo.config_writer().set_value("user", "name", "10zinten").release()
        repo.config_writer().set_value("user", "email", "ten13zin@gmail.com").release()
        return repo


def create_orphan_branch(repo_path, branch_name, parent_branch="master", type_="opf"):
    if isinstance(repo_path, Repo):
        repo = repo_path
    else:
        repo = Repo(repo_path)
    repo.git.checkout(parent_branch)
    repo.git.checkout("--orphan", branch_name)

    # # move base-text root level
    # repo_path = Path(repo.working_dir)
    # pecha_opf_path = repo_path / f"{repo_path.name}.{type_}"
    # if (pecha_opf_path / "base").is_dir():
    #     for vol_fn in (pecha_opf_path / "base").iterdir():
    #         shutil.move(str(vol_fn), str(repo_path))

    for path in Path(repo_path).iterdir():
        if path.name == ".git":
            continue
        if path.is_dir():
            repo.git.rm("-rf", str(path))
        elif path.is_file():
            repo.git.rm("-f", str(path))


def github_publish(
    path,
    message=None,
    not_includes=None,
    layers=[],
    org="OpenPecha",
    token=os.environ.get("GITHUB_TOKEN"),
):
    path = Path(path)
    remote_repo_url = create_github_repo(path, org, token)
    local_repo = create_local_repo(path, remote_repo_url, org, token)
    commit(local_repo, message, not_includes)
    local_repo.git.checkout("-b", "review")
    local_repo.git.push("origin", "review")

    for layer in layers:
        create_orphan_branch(local_repo, layer)
        commit(local_repo, message, not_includes, branch=layer)


def create_file(
    repo_name,
    path,
    content,
    msg,
    update=False,
    org="OpenPecha",
    token=os.environ.get("GITHUB_TOKEN"),
):
    repo = get_github_repo(repo_name, org, token)
    if update:
        old_content = repo.get_contents(path)
        repo.update_file(old_content.path, msg, content, old_content.sha)
    else:
        repo.create_file(path, msg, content)


def get_bumped_tag(repo):
    try:
        latest_release_tag = repo.get_latest_release().tag_name
    except Exception:
        return "v0.1"

    tag_number = float(latest_release_tag[1:])
    bump_tag_number = round(tag_number + 0.1, 1)
    return f"v{bump_tag_number}"


def _add_tag_in_filename(path, tag_name):
    path = Path(path)
    old_name = path.stem
    old_extension = path.suffix
    directory = path.parent
    new_name = f"{old_name}-{tag_name}{old_extension}"
    target_path = directory / new_name
    path.rename(target_path)
    return target_path


def upload_assets(release, tag_name=None, asset_paths=[]):
    if not tag_name:
        tag_name = release.tag_name
    download_url = ""
    for asset_path in asset_paths:
        # asset_path = _add_tag_in_filename(asset_path, tag_name)
        asset = release.upload_asset(str(asset_path))
        download_url = asset.browser_download_url
        print(f"[INFO] Uploaded asset {asset_path}")
    return download_url


def create_release(
    repo_name,
    prerelease=False,
    asset_paths=[],
    org="OpenPecha",
    token=os.environ.get("GITHUB_TOKEN"),
):
    repo = get_github_repo(repo_name, org, token)
    if prerelease:
        bumped_tag = uuid4().hex
        message = "Pre-release for download"
    else:
        bumped_tag = get_bumped_tag(repo)
        message = "Official Release"
    new_release = repo.create_git_release(
        bumped_tag, bumped_tag, message, prerelease=prerelease
    )
    print(f"[INFO] Created release {bumped_tag} for {repo_name}")
    asset_download_url = upload_assets(
        new_release, tag_name=bumped_tag, asset_paths=asset_paths
    )
    return asset_download_url


def add_assets_to_latest_release(repo_name, asset_paths=[]):
    repo = get_github_repo(repo_name)
    lastest_release = repo.get_latest_release()
    upload_assets(lastest_release, asset_paths=asset_paths)


def create_readme(metadata, path):
    result = ""
    # add title
    result += f"## Title\n\t- {metadata.get('title')}\n\n"

    # add author
    result += f"## Author\n\t- {metadata.get('author')}\n\n"

    readme_fn = path / "README.md"
    readme_fn.write_text(result)


def delete_repo(repo_name):
    org = _get_openpecha_org()
    repo = org.get_repo(repo_name)
    repo.delete()


if __name__ == "__main__":
    asset_download_url = create_release(
        "P000780", prerelease=True, asset_paths=Path("assets").iterdir()
    )
    print(asset_download_url)
    create_release("P000780", asset_paths=Path("assets").iterdir())
