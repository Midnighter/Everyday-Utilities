#!/usr/bin/env python
# -*- coding: utf-8 -*-


"""
=================
Threading Classes
=================

:Author:
    Moritz Emanuel Beber
:Date:
    2011-02-26
:Copyright:
    Copyright(c) 2011 Jacobs University of Bremen. All rights reserved.
:File:
    threaded.py

Notes
-----
Most classes (unless they inherit from old-style classes) are new-style classes.
Attributes and methods not intended to be accessed directly by the user are
preceeded by a single underscore '_' but they can be used if the user knows
what he is doing. Those preceeded with two underscores '__' should under no
circumstances be touched.
"""


import os
import threading
import logging
import paramiko
import socket
import math

from Queue import Queue
from .errors import NetworkError


class ThreadPoolWorker(threading.Thread):
    """
    Worker thread that operates on items from its queue.
    """

    def __init__(self, queue, exception_queue=None):
        """
        """
        threading.Thread.__init__(self)
        self._queue = queue
        self._exception_queue = exception_queue
        self.daemon = True

    def run(self):
        """
        """
        while True:
            (perform, args, kw_args) = self._queue.get()
            try:
                perform(*args, **kw_args)
            except StandardError as err:
                if self._exception_queue:
                    self._exception_queue.put((err, perform, args, kw_args))
            finally:
                self._queue.task_done()


def ThreadPool(object):
    """
    """

    def __init__(self, num_threads, retry=False):
        """
        """
        object.__init__(self)
        self.queue = Queue()
        if retry:
            self.exception_queue = Queue()
        else:
            self.exception_queue = None
        for i in xrange(num_threads):
            w = ThreadPoolWorker(self.queue, self.exception_queue)
            w.start()

    def put(self, perform, *args, **kw_args):
        """
        """
        self.queue.put((perform, args, kw_args))

    def join(self):
        """
        """
        self.queue.join()


class RemoteSetup(object):
    """
    docstring for RemoteSetup
    """
    def __init__(self, host, options, *args, **kwargs):
        """
        docstring
        """
        object.__init__(self)
        self._host = str(host)
        self.name = "%s@%s" % (self.__class__.__name__, self._host)
        self.logger = logging.getLogger(self.name)
        self._child_name = "%s.SSHClient" % self.name
        self._child_logger = logging.getLogger(self._child_name)
        self._child_logger.propagate = 0
        self._options = options
        self._client = None
        self._n_cpus = None
        self._cpu_usage = None
        self._io_lock = threading.Lock()

    def __del__(self):
        """
        docstring
        """
        if self._client:
            self._client.close()

    def close(self):
        if self._client:
            self._client.close()

    def make_ssh_connection(self):
        """
        docstring
        """
        # create the communication instance
        self.logger.debug("Creating SSHClient instance")
        self._client = paramiko.SSHClient()
        # set logging for it
        self.logger.debug("Setting log channel")
        self._client.set_log_channel(self._child_name)
        self.logger.debug("Setting missing host key policies")
        if self._options.auto_add:
            self._client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        else:
            self._client.set_missing_host_key_policy(paramiko.WarningPolicy())
        self.logger.debug("Loading known host keys")
        self._io_lock.acquire()
        try:
            self._client.load_host_keys(
                os.path.expanduser("~/.ssh/known_hosts"))
        except IOError as err:
            self.logger.exception(str(err))
        # how to proceed when loading of host keys fails?
        # right now making the connection probably still fails so all is well
        finally:
            self._io_lock.release()
        self.logger.debug("Making connection")
        try:
            self._client.connect(hostname=self._host, port=self._options.ssh_port,
                username=self._options.username, password=self._options.password)
        except paramiko.BadHostKeyException:
            raise NetworkError("Bad Host Key")
        except paramiko.AuthenticationException:
            raise NetworkError("Authentication Error")
        except paramiko.SSHException:
            raise NetworkError("Connection Error")
        except socket.error:
            raise NetworkError("Socket Error")
        else:
            self.logger.info("Connection established and authenticated")
        self._io_lock.acquire()
        self._client.save_host_keys(os.path.expanduser("~/.ssh/known_hosts"))
        self._io_lock.release()

    def one_time_cmd(self, cmd):
        """
        """
        try:
            (stdin_fh, stdout_fh, stderr_fh) = self._client.exec_command(cmd,\
                self._options.buf_size)
        except paramiko.SSHException:
            raise NetworkError("Failed to execute remote command")
        stderr = stderr_fh.read()
        stdout = stdout_fh.read()
        if stderr and not stdout:
            raise NetworkError("Remote command failed with: %s", stderr)
        else:
            return stdout


    def _detect_ncpus(self):
        """
        docstring
        """
        # get number of cpus on linux
        cmd = "grep -c 'model name' '/proc/cpuinfo'"
        stdout = self.one_time_cmd(cmd)
        if stdout:
            self.logger.debug(stdout)
            stdout = stdout.split("\n")
            for line in stdout:
                try:
                    self._n_cpus = int(line)
                except ValueError:
                    continue
                else:
                    return
        # no CPUs detected, i.e., cmd caused an error
        # will use pty on MacOS as well for consistency
        cmd = "sysctl -n hw.ncpu"
        stdout = self.one_time_cmd(cmd)
        if stdout:
            self.logger.debug(stdout)
            stdout = stdout.split("\n")
            for line in stdout:
                try:
                    self._n_cpus = int(line)
                except ValueError:
                    continue
                else:
                    return
        # return the default value
        self.logger.warning("Could not detect number of CPUs,"\
            " assuming default '1'")
        self._n_cpus = 1

    def _detect_cpu_usage(self, num_probes=10.0):
        """
        docstring
        """
        # for linux, unix, and macosx that's why both -e and -a
        cmd = "vmstat 1 %d" % num_probes
        stdout = self.one_time_cmd(cmd)
        if stdout:
            self.logger.debug(stdout)
            stdout = stdout.split("\n")
            total = 0.
            for line in stdout:
                if not line:
                    continue
                tmp = line.split()
                # only want to parse lines that start with numbers
                try:
                    float(tmp[0])
                except ValueError:
                    continue
                # cheap trick not to parse ordinary text, like %CPU header
                # ps --no-headers not available on mac, for example
                try:
                    total += float(tmp[12])
                except ValueError:
                    continue
            self._cpu_usage = math.ceil(total / num_probes)
            return
        # default usage
        self.logger.warning("Could not detect CPU usage, assuming 0 %%")
        self._cpu_usage = 0.

    def remote_shell_cmd(self, cmd, timeout=20.):
        """
        """
        try:
            channel = self._client.invoke_shell()
        except paramiko.SSHException:
            raise NetworkError("Failed to invoke remote shell")
        if channel.gettimeout():
            self.logger.debug("Channel timeout: %f", channel.gettimeout())
        else:
            channel.settimeout(timeout)
        try:
            channel.sendall(cmd)
        except socket.timeout:
            channel.close()
            raise NetworkError("Connection timed out")
        stdout = ""
        expect = "%s@%s:~>\r\n" % (self._options.username, self._host)
        while True:
            try:
                stdout += channel.recv(self._options.buf_size)
                if stdout.endswith(expect):
                    break
            except socket.timeout:
                break
        channel.close()
        return stdout

    def _setup_job(self, lower, upper, shell_file="batch_jobs.sh"):
        """
        docstring
        """
        cmd = "screen -dmS batch_simulation %s %d %d\n"\
            % (shell_file, lower, upper)
        # we only have to check for immediate errors of running this command
        # not sure how to do that atm
        stdout = self.remote_shell_cmd(cmd)
        if stdout:
            self.logger.debug(stdout)

    def usage(self):
        """
        docstring
        """
        self.logger.debug("Establishing SSH connection...")
        try:
            self.make_ssh_connection()
        except NetworkError as err:
            self.logger.debug(str(err))
            return 0
        self.logger.debug("Detecting number of CPUs...")
        self._detect_ncpus()
        self.logger.debug("There are %d CPUs online", self._n_cpus)
        self.logger.debug("Detecting CPU usage...")
        self._detect_cpu_usage()
        self.logger.debug("Usage is: %f", self._cpu_usage)
        # compare work load with number of cpus present
        self._cpu_usage = round(self._n_cpus * self._cpu_usage / 100.0, 0)
        self._n_cpus = self._n_cpus - int(self._cpu_usage)
        self.logger.debug("Number of CPUs to use: %d", self._n_cpus)
        self.logger.debug("Closing client")
        self._client.close()
        return self._n_cpus

    def run(self, lower, upper, shell_file="batch_jobs.sh"):
        """
        docstring
        """
        self.logger.debug("Establishing SSH connection...")
        try:
            self.make_ssh_connection()
        except NetworkError as err:
            self.logger.debug(str(err))
            return None
        # start simulations
        self._setup_job(lower, upper, shell_file)
        self.logger.info("Remote job started")
        self._client.close()

    def _detect_processes(self, *args):
        """
        docstring
        """
        pids = list()
        for comm in args:
            cmd = "ps -u %s -o pid,comm | grep %s | grep -v grep" %\
                    (self._options.username, comm)
            stdout = self.one_time_cmd(cmd)
            if stdout:
                self.logger.debug(stdout)
                stdout = stdout.split("\n")
                for line in stdout:
                    # cheap trick not to parse ordinary text, like %CPU header
                    try:
                        pids.append(int(line.split()[0]))
                    except ValueError:
                        continue
                    except IndexError:
                        break
        return pids

    def kill(self, *args):
        """
        docstring
        """
        self.logger.debug("Establishing SSH connection...")
        try:
            self.make_ssh_connection()
        except NetworkError as err:
            self.logger.debug(str(err))
            return 0
        self.logger.debug("Killing process(es)...")
        pids = self._detect_processes(*args)
        self.logger.debug(pids)
        killed = 0
        for pid in pids:
            cmd = "kill %d" % pid
            try:
                stdout = self.one_time_cmd(cmd)
            except NetworkError as err:
                self.logger.debug(str(err))
                self.logger.debug(stdout)
            else:
                killed += 1
        self.logger.debug("Closing client")
        self._client.close()
        return killed

