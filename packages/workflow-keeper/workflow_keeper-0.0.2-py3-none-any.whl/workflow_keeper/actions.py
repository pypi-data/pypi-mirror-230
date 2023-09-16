import getpass
import io
import os
import subprocess
import time
from abc import ABC
from socket import socket
import paramiko
import re
from typing import Tuple, Optional

from loguru import logger

from workflow_keeper.datamodels import JobStep


class Action(ABC):
    @classmethod
    def run(cls, job_step: JobStep, log_output: Optional[io.TextIOWrapper] = None) -> Tuple[str, Optional[Exception]]:
        # does nothing
        logger.info(f"running none action: {job_step.name}")
        return "", None


class ShellAction(Action):

    @classmethod
    def run(cls, job_step: JobStep, log_output: Optional[io.TextIOWrapper] = None) -> Tuple[str, Optional[Exception]]:
        logger.info(f"running shell action: {job_step.name}")
        # open a subprocess
        subp = subprocess.Popen(job_step.run, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        out, err = "", ""
        time.sleep(0.1)
        start_t = time.time()
        process_exit_flag = False
        while True:
            poll_res = subp.poll()

            # read output
            _out = subp.stdout.read().decode()
            _err = subp.stderr.read().decode()

            # live display
            print(_out, end="") if _out != "" else None
            print(_err, end="") if _err != "" else None

            # add to collection
            out += _out
            err += _err

            # write to log files if specified
            if log_output is not None:
                log_output.write(_out)
                log_output.write(_err)

            if poll_res is None:
                time.sleep(0.1)
            else:
                if process_exit_flag:
                    logger.info(f"subprocess {subp.pid} exited in {time.time() - start_t}s with {poll_res}")
                    break
                else:
                    process_exit_flag = True
                    continue

        content = "-------- STDERR --------\n\n" + err + "\n\n-------- STDOUT --------\n\n" + out + "\n\n------------------------\n\n"
        # kill the subprocess
        subp.kill()
        return content, None


class Ssh2Client:
    def __init__(self, host: str, port: int):
        self.__host = host
        self.__port = port
        self.__ssh = None
        self.__channel = None

        self.__ansi_escape = re.compile(r'''
                        \x1B  # ESC
                        (?:   # 7-bit C1 Fe (except CSI)
                        [@-Z\\-_]
                        |     # or [ for CSI, followed by a control sequence
                        \[
                        [0-?]*  # Parameter bytes
                        [ -/]*  # Intermediate bytes
                        [@-~]   # Final byte
                    )
                ''', re.VERBOSE)

    def __del__(self):
        self.__close()

    def connect(self, username: str, password: str, private: paramiko.PKey) -> bool:
        self.__close()

        self.__ssh = paramiko.SSHClient()
        self.__ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # Connect to the host
        self.__ssh.connect(self.__host, self.__port, username=username, password=password, pkey=private)
        return True

    def exec(self, cmd: str, end_str=('# ', '$ ', '? ', '% '), timeout=30) -> str:
        if not self.__channel:
            self.__channel = self.__ssh.invoke_shell(term='xterm', width=4096, height=48)
            time.sleep(0.020)
            self.__channel.recv(4096).decode()

        if cmd.endswith('\n'):
            self.__channel.send(cmd)
        else:
            self.__channel.send(cmd + '\n')

        result = self.__recv(self.__channel, end_str, timeout)
        begin_pos = result.find('\r\n')
        end_pos = result.rfind('\r\n')
        if begin_pos == end_pos:
            return ''
        return result[begin_pos + 2:end_pos]

    def __recv(self, channel, end_str, timeout) -> str:
        result = ''
        out_str = ''
        max_wait_time = timeout * 1000
        channel.settimeout(0.05)
        while max_wait_time > 0:
            try:
                out = channel.recv(1024 * 1024).decode()

                if not out or out == '':
                    continue
                out_str = out_str + out

                match, result = self.__match(out_str, end_str)
                if match is True or not channel.recv_ready():
                    return result.strip()
                else:
                    max_wait_time -= 50
            except socket.timeout:
                max_wait_time -= 50

        raise Exception('recv data timeout')

    def __match(self, out_str: str, end_str: list) -> (bool, str):
        result = self.__ansi_escape.sub('', out_str)

        for it in end_str:
            if result.endswith(it):
                return True, result
        return False, result

    def __close(self):
        if not self.__ssh:
            return
        self.__ssh.close()
        self.__ssh = None

    def close(self):
        self.__close()


class SSHAction(Action):
    @classmethod
    def run(cls, job_step: JobStep, log_output: Optional[io.TextIOWrapper] = None) -> Tuple[str, Optional[Exception]]:
        logger.info(f"running ssh action: {job_step.name}")

        try:
            import paramiko
            host = job_step.params.get("host", None)
            port = job_step.params.get("port", 22)
            username = job_step.params.get("username", getpass.getuser())
            password = job_step.params.get("password", None)
            private = paramiko.RSAKey.from_private_key_file(os.path.expanduser("~/.ssh/id_rsa"))
            assert host is not None
        except ImportError:
            logger.error("paramiko not installed")
            return "", Exception("paramiko not installed")
        except Exception as e:
            return "", e

        # Create a new SSH client
        ssh = Ssh2Client(host, port)
        ssh.connect(username, password, private)

        # Execute each command
        if isinstance(job_step.run, str):
            _run = job_step.run
        else:
            _run = "\n".join(job_step.run)
        if not _run.endswith("\n"):
            _run += "\n"

        result = ssh.exec(_run)

        print(result)
        if log_output is not None:
            log_output.write(result)

        # Close the SSH connection
        ssh.close()


def get_action(job_step: JobStep) -> Action:
    """
    Get action from job step
    """
    # TODO: add more actions
    if job_step.uses is None:
        return Action()
    elif job_step.uses == "shell":
        return ShellAction()
    elif job_step.uses == "ssh":
        return SSHAction()
    else:
        raise NotImplementedError
