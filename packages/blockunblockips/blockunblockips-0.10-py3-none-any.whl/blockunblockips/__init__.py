import subprocess
from detachedproc import DetachedPopen
import shutil
netshexe = shutil.which("netsh.exe")

def unblock_out(ipaddress):
    r"""
    Unblock outgoing traffic to a specific IP address by deleting a Windows Firewall rule.

    Args:
        ipaddress (str): The IP address to unblock.

    Returns:
        DetachedPopen: A DetachedPopen object representing the subprocess.

    Note:
        This function deletes a Windows Firewall rule that blocks outgoing traffic
        to the specified IP address.

    """
    return DetachedPopen(
        args=[
            netshexe,
            "advfirewall",
            "firewall",
            "delete",
            "rule",
            f'name="BLOCK_IP_ADDRESS_OUT_{ipaddress}"',
            "dir=in",
        ],
        bufsize=-1,
        executable=None,
        stdin=None,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        preexec_fn=None,
        close_fds=True,
        shell=False,
        cwd=None,
        env=None,
        universal_newlines=None,
        startupinfo=None,
        creationflags=0,
        restore_signals=True,
        start_new_session=False,
        pass_fds=(),
        user=None,
        group=None,
        extra_groups=None,
        encoding=None,
        errors=None,
        text=None,
        umask=-1,
        pipesize=-1,
        window_style="Hidden",
        wait=False,
        verb=None,
        what_if=False,
        print_stdout=True,
        print_stderr=True,
        capture_stdout=True,
        capture_stderr=True,
        stdoutbuffer=None,
        stderrbuffer=None,
        psutil_timeout=3,
        delete_tempfiles=True,
    )


def unblock_in(ipaddress):
    r"""
    Unblock incoming traffic from a specific IP address by deleting a Windows Firewall rule.

    Args:
        ipaddress (str): The IP address to unblock.

    Returns:
        DetachedPopen: A DetachedPopen object representing the subprocess.

    Note:
        This function deletes a Windows Firewall rule that blocks incoming traffic
        from the specified IP address.

    """
    return DetachedPopen(
        args=[
            netshexe,
            "advfirewall",
            "firewall",
            "delete",
            "rule",
            f'name="BLOCK_IP_ADDRESS_IN_{ipaddress}"',
            "dir=in",
        ],
        bufsize=-1,
        executable=None,
        stdin=None,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        preexec_fn=None,
        close_fds=True,
        shell=False,
        cwd=None,
        env=None,
        universal_newlines=None,
        startupinfo=None,
        creationflags=0,
        restore_signals=True,
        start_new_session=False,
        pass_fds=(),
        user=None,
        group=None,
        extra_groups=None,
        encoding=None,
        errors=None,
        text=None,
        umask=-1,
        pipesize=-1,
        window_style="Hidden",
        wait=False,
        verb=None,
        what_if=False,
        print_stdout=True,
        print_stderr=True,
        capture_stdout=True,
        capture_stderr=True,
        stdoutbuffer=None,
        stderrbuffer=None,
        psutil_timeout=3,
        delete_tempfiles=True,
    )


def block_out(ipaddress):
    r"""
    Block outgoing traffic to a specific IP address by creating a Windows Firewall rule.

    Args:
        ipaddress (str): The IP address to block.

    Returns:
        DetachedPopen: A DetachedPopen object representing the subprocess.

    Note:
        This function creates a Windows Firewall rule to block outgoing traffic
        to the specified IP address.

    """
    return DetachedPopen(
        args=[
            netshexe,
            "advfirewall",
            "firewall",
            "add",
            "rule",
            f'name="BLOCK_IP_ADDRESS_OUT_{ipaddress}"',
            "dir=out",
            "action=block",
            f"remoteip={ipaddress}",
        ],
        bufsize=-1,
        executable=None,
        stdin=None,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        preexec_fn=None,
        close_fds=True,
        shell=False,
        cwd=None,
        env=None,
        universal_newlines=None,
        startupinfo=None,
        creationflags=0,
        restore_signals=True,
        start_new_session=False,
        pass_fds=(),
        user=None,
        group=None,
        extra_groups=None,
        encoding=None,
        errors=None,
        text=None,
        umask=-1,
        pipesize=-1,
        window_style="Hidden",
        wait=False,
        verb=None,
        what_if=False,
        print_stdout=True,
        print_stderr=True,
        capture_stdout=True,
        capture_stderr=True,
        stdoutbuffer=None,
        stderrbuffer=None,
        psutil_timeout=3,
        delete_tempfiles=True,
    )


def block_in(ipaddress):
    r"""
    Block incoming traffic from a specific IP address by creating a Windows Firewall rule.

    Args:
        ipaddress (str): The IP address to block.

    Returns:
        DetachedPopen: A DetachedPopen object representing the subprocess.

    Note:
        This function creates a Windows Firewall rule to block incoming traffic
        from the specified IP address.

    """
    return DetachedPopen(
        args=[
            netshexe,
            "advfirewall",
            "firewall",
            "add",
            "rule",
            f'name="BLOCK_IP_ADDRESS_IN_{ipaddress}"',
            "dir=in",
            "action=block",
            f"remoteip={ipaddress}",
        ],
        bufsize=-1,
        executable=None,
        stdin=None,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        preexec_fn=None,
        close_fds=True,
        shell=False,
        cwd=None,
        env=None,
        universal_newlines=None,
        startupinfo=None,
        creationflags=0,
        restore_signals=True,
        start_new_session=False,
        pass_fds=(),
        user=None,
        group=None,
        extra_groups=None,
        encoding=None,
        errors=None,
        text=None,
        umask=-1,
        pipesize=-1,
        window_style="Hidden",
        wait=False,
        verb=None,
        what_if=False,
        print_stdout=True,
        print_stderr=True,
        capture_stdout=True,
        capture_stderr=True,
        stdoutbuffer=None,
        stderrbuffer=None,
        psutil_timeout=3,
        delete_tempfiles=True,
    )
