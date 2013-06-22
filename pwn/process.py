import pwn
from basechatter import basechatter

class process(basechatter):
    def __init__(self, cmd, *args, **kwargs):
        env = kwargs.get('env', {})
        timeout = kwargs.get('timeout', 'default')
        silent = kwargs.get('silent', False)
        basechatter.__init__(self, timeout, silent)
        self.proc = None
        self.stdout = None

        self.start(cmd, args, env)

    def start(self, cmd, args, env):
        import subprocess, fcntl, os
        if self.connected():
            pwn.log.warning('Program "%s" already started' % cmd)
            return
        if not self.silent:
            pwn.log.waitfor('Starting program "%s"' % cmd)

        self.proc = subprocess.Popen(
                tuple(cmd.split()) + args,
                stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                env = env,
                bufsize = 0)
        fd = self.proc.stdout.fileno()
        fl = fcntl.fcntl(fd, fcntl.F_GETFL)
        fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)
        self.stdout = fd
        if not self.silent:
            pwn.log.succeeded()

    def connected(self):
        return self.proc != None

    def close(self):
        if self.proc:
            self.proc.kill()
            self.proc = None

    def _send(self, dat):
        self.proc.stdin.write(dat)
        self.proc.stdin.flush()

    def _recv(self, numb):
        import time
        end_time = time.time() + self.timeout

        while True:
            r = ''
            try:
                r = self.proc.stdout.read(numb)
            except IOError as e:
                if e.errno != 11:
                    raise

            if r or time.time() > end_time:
                break
            time.sleep(0.0001)
        return r

    def fileno(self):
        return self.stdout
