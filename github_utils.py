import shutil
import subprocess


def _run_git(project_dir, args):
    result = subprocess.run(
        ["git"] + args,
        cwd=project_dir,
        capture_output=True,
        text=True,
        shell=False,
    )
    output = ""
    if result.stdout:
        output += result.stdout
    if result.stderr:
        output += result.stderr
    return result.returncode, output.strip()


def has_git():
    return shutil.which("git") is not None


def init_repo_if_needed(project_dir):
    code, out = _run_git(project_dir, ["rev-parse", "--is-inside-work-tree"])
    if code == 0:
        return True, "Git repository already exists."

    code, out = _run_git(project_dir, ["init"])
    if code != 0:
        return False, out or "Khong the khoi tao Git repository."

    code, out2 = _run_git(project_dir, ["branch", "-M", "main"])
    msg = (out + "\n" + out2).strip()
    return code == 0, msg or "Da khoi tao Git repository."


def set_remote(project_dir, remote_url):
    code, out = _run_git(project_dir, ["remote", "get-url", "origin"])
    if code == 0:
        code, out2 = _run_git(project_dir, ["remote", "set-url", "origin", remote_url])
        return code == 0, out2 or "Da cap nhat remote origin."

    code, out2 = _run_git(project_dir, ["remote", "add", "origin", remote_url])
    return code == 0, out2 or "Da them remote origin."


def commit_all(project_dir, message):
    logs = []

    code, out = _run_git(project_dir, ["add", "."])
    logs.append("$ git add .")
    if out:
        logs.append(out)

    code2, out2 = _run_git(project_dir, ["commit", "-m", message])
    logs.append(f'$ git commit -m "{message}"')
    if out2:
        logs.append(out2)

    full_log = "\n\n".join(logs).strip()
    text = full_log.lower()

    if code2 == 0:
        return True, full_log

    if "nothing to commit" in text or "working tree clean" in text:
        return True, full_log

    return False, full_log


def commit_ai_outputs(project_dir, message):
    logs = []

    code, out = _run_git(project_dir, ["add", "outputs/"])
    logs.append("$ git add outputs/")
    if out:
        logs.append(out)

    code2, out2 = _run_git(project_dir, ["commit", "-m", message])
    logs.append(f'$ git commit -m "{message}"')
    if out2:
        logs.append(out2)

    full_log = "\n\n".join(logs).strip()
    text = full_log.lower()

    if code2 == 0:
        return True, full_log

    if "nothing to commit" in text or "working tree clean" in text:
        return True, full_log

    return False, full_log


def push(project_dir, branch="main"):
    logs = []

    code, out = _run_git(project_dir, ["push", "-u", "origin", branch])
    logs.append(f"$ git push -u origin {branch}")
    if out:
        logs.append(out)

    full_log = "\n\n".join(logs).strip()
    text = full_log.lower()

    if code == 0:
        return True, full_log

    if "everything up-to-date" in text:
        return True, full_log

    return False, full_log