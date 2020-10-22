import os
import platform
import struct
from pathlib import Path

M_TYPE = platform.system()
GIT_URL = {
    "Darwin-64": "https://sourceforge.net/projects/git-osx-installer/files/git-2.23.0-intel-universal-mavericks.dmg",
    "Darwin-32": "https://sourceforge.net/projects/git-osx-installer/files/git-2.23.0-intel-universal-mavericks.dmg",
    "Windows-32": "https://github.com/git-for-windows/git/releases/download/v2.25.0.windows.1/Git-2.25.0-32-bit.exe",
    "Windows-64": "https://github.com/git-for-windows/git/releases/download/v2.25.0.windows.1/Git-2.25.0-64-bit.exe",
}


def run_cmd(cmd):
    os.system(cmd)


def install_dependencies():
    dependencies = ["requests", "tqdm"]
    for dependency in dependencies:
        run_cmd(f"pip3 install {dependency}")


def git_pkg_fn():
    mount_path = Path("/Volumes")
    git_pkg_dir = list(mount_path.glob("Git*"))[0]
    git_pkg_path = str(list(git_pkg_dir.glob("git*"))[0])
    return git_pkg_path.replace(" ", r"\ ")


def is_git_installed():
    from shutil import which

    return which("git") is not None


def download_git(url):
    import requests
    from tqdm import tqdm

    git_installer_fn = Path.home() / "Downloads" / url.split("/")[-1]
    if git_installer_fn.is_file():
        print("[INFO] Git installer already downloaded")
        return git_installer_fn

    r = requests.get(url, stream=True)
    total_size = int(r.headers.get("content-length", 0))
    block_size = 1024  # 1 kibibyte
    t = tqdm(total=total_size, unit="iB", unit_scale=True)

    with git_installer_fn.open("wb") as f:
        for data in r.iter_content(block_size):
            t.update(len(data))
            f.write(data)
    t.close()

    return git_installer_fn


def install_git():
    bit = sys_32_or_64()
    if bit == 32:
        git_installer_fn = download_git(GIT_URL[f"{M_TYPE}-32"])
    else:
        git_installer_fn = download_git(GIT_URL[f"{M_TYPE}-64"])

    if M_TYPE == "Darwin":
        # mount and install git
        run_cmd(f"hdiutil attach {git_installer_fn}")
        run_cmd(f"sudo installer -pkg {git_pkg_fn()} -target /")
    elif M_TYPE == "Windows":
        run_cmd(f"start {git_installer_fn}")
    else:
        pass


def sys_32_or_64():
    return struct.calcsize("P") * 8


def install_op_toolkit():
    run_cmd("pip3 install openpecha")


def install():
    print("[INFO] Installing dependencies ...")
    install_dependencies()

    print("[INFO] Installing Git ...")
    if is_git_installed():
        print("[INFO] Git already installed")
    else:
        install_git()

    print("[INFO] Installing OpenPecha ToolKit ....")
    install_op_toolkit()


if __name__ == "__main__":
    install()
