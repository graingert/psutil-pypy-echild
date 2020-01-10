```sh
$ python
Python 2.7.13 (7.1.1+dfsg-1, Aug 09 2019, 05:11:07)
[PyPy 7.1.1 with GCC 9.1.0] on linux2
Type "help", "copyright", "credits" or "license" for more information.
$ python psutil_pypy_echild.py 
Traceback (most recent call last):
  File "psutil_pypy_echild.py", line 102, in <module>
    test_set_pdeathsig()
  File "psutil_pypy_echild.py", line 98, in test_set_pdeathsig
    assert child_proc.wait(3) is None
  File "/home/graingert/.virtualenvs/pypy2_psutil/site-packages/psutil/__init__.py", line 1383, in wait
    return self._proc.wait(timeout)
  File "/home/graingert/.virtualenvs/pypy2_psutil/site-packages/psutil/_pslinux.py", line 1517, in wrapper
    return fun(self, *args, **kwargs)
  File "/home/graingert/.virtualenvs/pypy2_psutil/site-packages/psutil/_pslinux.py", line 1725, in wait
    return _psposix.wait_pid(self.pid, timeout, self._name)
  File "<patchy>", line 48, in wait_pid
Exception: Something very strange happened
```
