from utils.system import run_cmd
from .conf import Conf


def rsync(src: str, des: str, exclude: list[str] = None, port: int = 22) -> bool:
    cmd = [Conf.rsync_bin, "--whole-file", "--info=NAME"]
    if exclude:
        for e in exclude:
            cmd.append("--exclude")
            cmd.append(e)

    cmd.extend(["-e", f"{Conf.ssh_bin} -p {port}"])
    cmd.extend(["-a", src, des])
    out, success = run_cmd(cmd)
    return success
