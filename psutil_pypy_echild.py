import multiprocessing
import os
import signal
import sys
import time

import patchy
import psutil

try:
    import cffi
except ImportError:
    import ctypes

# Constants from prctl.h
PR_GET_PDEATHSIG = 2
PR_SET_PDEATHSIG = 1

patchy.patch(
    "psutil._psposix.wait_pid",
    """
    @@ -34,24 +34,28 @@
             except ChildProcessError:
                 # This has two meanings:
                 # - pid is not a child of os.getpid() in which case
                 #   we keep polling until it's gone
                 # - pid never existed in the first place
                 # In both cases we'll eventually return None as we
                 # can't determine its exit status code.
                 while True:
                     if pid_exists(pid):
                         delay = check_timeout(delay)
                     else:
                         return
    +        except Exception as e:
    +            if isinstance(e, ChildProcessError):
    +                raise Exception("Something very strange happened")
    +            raise
             else:
                 if retpid == 0:
                     # WNOHANG was used, pid is still running
                     delay = check_timeout(delay)
                     continue
                 # process exited due to a signal; return the integer of
                 # that signal
                 if os.WIFSIGNALED(status):
                     return -os.WTERMSIG(status)
                 # process exited using exit(2) system call; return the
                 # integer exit(2) system call has been called with
                 elif os.WIFEXITED(status):
    """,
)


def set_pdeathsig(sig):
    """
    Set the parent process death signal of the calling process to sig
    (either a signal value in the range 1..maxsig, or 0 to clear).
    This is the signal that the calling process will get when its parent dies.
    This value is cleared for the child of a fork(2) and
    (since Linux 2.4.36 / 2.6.23) when executing a set-user-ID or set-group-ID binary.
    """
    if not sys.platform.startswith("linux"):
        # currently we support only linux platform.
        raise OSError()
    try:
        if "cffi" in sys.modules:
            ffi = cffi.FFI()
            ffi.cdef("int prctl (int __option, ...);")
            C = ffi.dlopen(None)
            C.prctl(PR_SET_PDEATHSIG, ffi.cast("int", sig))
        else:
            libc = ctypes.cdll.LoadLibrary("libc.so.6")
            libc.prctl(PR_SET_PDEATHSIG, sig)
    except Exception:
        raise OSError()


def child_process(q):
    set_pdeathsig(signal.SIGTERM)
    q.put(os.getpid())
    while True:
        time.sleep(1)


def parent_task(q):
    p = multiprocessing.Process(target=child_process, args=(q,))
    p.start()
    p.join()


def test_set_pdeathsig():
    q = multiprocessing.Queue()
    p = multiprocessing.Process(target=parent_task, args=(q,))
    p.start()
    child_proc = psutil.Process(q.get(timeout=3))
    p.terminate()
    assert child_proc.wait(3) is None


if __name__ == "__main__":
    test_set_pdeathsig()
