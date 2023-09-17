'''
############################################
portalocker - Cross-platform locking library
############################################

.. image:: https://github.com/WoLpH/portalocker/actions/workflows/python-package.yml/badge.svg?branch=master
    :alt: Linux Test Status
    :target: https://github.com/WoLpH/portalocker/actions/

.. image:: https://ci.appveyor.com/api/projects/status/mgqry98hgpy4prhh?svg=true
    :alt: Windows Tests Status
    :target: https://ci.appveyor.com/project/WoLpH/portalocker

.. image:: https://coveralls.io/repos/WoLpH/portalocker/badge.svg?branch=master
    :alt: Coverage Status
    :target: https://coveralls.io/r/WoLpH/portalocker?branch=master

Overview
--------

Portalocker is a library to provide an easy API to file locking.

An important detail to note is that on Linux and Unix systems the locks are
advisory by default. By specifying the `-o mand` option to the mount command it
is possible to enable mandatory file locking on Linux. This is generally not
recommended however. For more information about the subject:

 - https://en.wikipedia.org/wiki/File_locking
 - http://stackoverflow.com/questions/39292051/portalocker-does-not-seem-to-lock
 - https://stackoverflow.com/questions/12062466/mandatory-file-lock-on-linux

The module is currently maintained by Rick van Hattem <Wolph@wol.ph>.
The project resides at https://github.com/WoLpH/portalocker . Bugs and feature
requests can be submitted there. Patches are also very welcome.

Security contact information
------------------------------------------------------------------------------

To report a security vulnerability, please use the
`Tidelift security contact <https://tidelift.com/security>`_.
Tidelift will coordinate the fix and disclosure.

Redis Locks
-----------

This library now features a lock based on Redis which allows for locks across
multiple threads, processes and even distributed locks across multiple
computers.

It is an extremely reliable Redis lock that is based on pubsub.

As opposed to most Redis locking systems based on key/value pairs,
this locking method is based on the pubsub system. The big advantage is
that if the connection gets killed due to network issues, crashing
processes or otherwise, it will still immediately unlock instead of
waiting for a lock timeout.

First make sure you have everything installed correctly:

::

    pip install "portalocker[redis]"

Usage is really easy:

::

    import portalocker

    lock = portalocker.RedisLock('some_lock_channel_name')

    with lock:
        print('do something here')

The API is essentially identical to the other ``Lock`` classes so in addition
to the ``with`` statement you can also use ``lock.acquire(...)``.

Python 2
--------

Python 2 was supported in versions before Portalocker 2.0. If you are still
using
Python 2,
you can run this to install:

::

    pip install "portalocker<2"

Tips
----

On some networked filesystems it might be needed to force a `os.fsync()` before
closing the file so it's actually written before another client reads the file.
Effectively this comes down to:

::

   with portalocker.Lock('some_file', 'rb+', timeout=60) as fh:
       # do what you need to do
       ...

       # flush and sync to filesystem
       fh.flush()
       os.fsync(fh.fileno())

Links
-----

* Documentation
    - http://portalocker.readthedocs.org/en/latest/
* Source
    - https://github.com/WoLpH/portalocker
* Bug reports
    - https://github.com/WoLpH/portalocker/issues
* Package homepage
    - https://pypi.python.org/pypi/portalocker
* My blog
    - http://w.wol.ph/

Examples
--------

To make sure your cache generation scripts don't race, use the `Lock` class:

>>> import portalocker
>>> with portalocker.Lock('somefile', timeout=1) as fh:
...     print('writing some stuff to my cache...', file=fh)

To customize the opening and locking a manual approach is also possible:

>>> import portalocker
>>> file = open('somefile', 'r+')
>>> portalocker.lock(file, portalocker.LockFlags.EXCLUSIVE)
>>> file.seek(12)
>>> file.write('foo')
>>> file.close()

Explicitly unlocking is not needed in most cases but omitting it has been known
to cause issues:
https://github.com/AzureAD/microsoft-authentication-extensions-for-python/issues/42#issuecomment-601108266

If needed, it can be done through:

>>> portalocker.unlock(file)

Do note that your data might still be in a buffer so it is possible that your
data is not available until you `flush()` or `close()`.

To create a cross platform bounded semaphore across multiple processes you can
use the `BoundedSemaphore` class which functions somewhat similar to
`threading.BoundedSemaphore`:

>>> import portalocker
>>> n = 2
>>> timeout = 0.1

>>> semaphore_a = portalocker.BoundedSemaphore(n, timeout=timeout)
>>> semaphore_b = portalocker.BoundedSemaphore(n, timeout=timeout)
>>> semaphore_c = portalocker.BoundedSemaphore(n, timeout=timeout)

>>> semaphore_a.acquire()
<portalocker.utils.Lock object at ...>
>>> semaphore_b.acquire()
<portalocker.utils.Lock object at ...>
>>> semaphore_c.acquire()
Traceback (most recent call last):
  ...
portalocker.exceptions.AlreadyLocked


More examples can be found in the
`tests <http://portalocker.readthedocs.io/en/latest/_modules/tests/tests.html>`_.


Versioning
----------

This library follows `Semantic Versioning <http://semver.org/>`_.


Changelog
---------

Every release has a ``git tag`` with a commit message for the tag
explaining what was added and/or changed. The list of tags/releases
including the commit messages can be found here:
https://github.com/WoLpH/portalocker/releases

License
-------

See the `LICENSE <https://github.com/WoLpH/portalocker/blob/develop/LICENSE>`_ file.


'''

'''
Copyright 2022 Rick van Hattem

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

'''

__package_name__ = 'portalocker'
__author__ = 'Rick van Hattem'
__email__ = 'wolph@wol.ph'
__version__ = '2.7.0'
__description__ = '''Wraps the portalocker recipe for easy usage'''
__url__ = 'https://github.com/WoLpH/portalocker'
'''
Locking constants

Lock types:

- `EXCLUSIVE` exclusive lock
- `SHARED` shared lock

Lock flags:

- `NON_BLOCKING` non-blocking

Manually unlock, only needed internally

- `UNBLOCK` unlock
'''
import enum
import os

# The actual tests will execute the code anyhow so the following code can
# safely be ignored from the coverage tests
if os.name == 'nt':  # pragma: no cover
    import msvcrt

    #: exclusive lock
    LOCK_EX = 0x1
    #: shared lock
    LOCK_SH = 0x2
    #: non-blocking
    LOCK_NB = 0x4
    #: unlock
    LOCK_UN = msvcrt.LK_UNLCK  # type: ignore

elif os.name == 'posix':  # pragma: no cover
    import fcntl

    #: exclusive lock
    LOCK_EX = fcntl.LOCK_EX
    #: shared lock
    LOCK_SH = fcntl.LOCK_SH
    #: non-blocking
    LOCK_NB = fcntl.LOCK_NB
    #: unlock
    LOCK_UN = fcntl.LOCK_UN

else:  # pragma: no cover
    raise RuntimeError('PortaLocker only defined for nt and posix platforms')


class LockFlags(enum.IntFlag):
    #: exclusive lock
    EXCLUSIVE = LOCK_EX
    #: shared lock
    SHARED = LOCK_SH
    #: non-blocking
    NON_BLOCKING = LOCK_NB
    #: unlock
    UNBLOCK = LOCK_UN


import typing


class BaseLockException(Exception):  # noqa: N818
    # Error codes:
    LOCK_FAILED = 1

    def __init__(
        self,
        *args: typing.Any,
        fh: typing.Union[typing.IO, None, int] = None,
        **kwargs: typing.Any,
    ) -> None:
        self.fh = fh
        Exception.__init__(self, *args)


class LockException(BaseLockException):
    pass


class AlreadyLocked(LockException):
    pass


class FileToLarge(LockException):
    pass


import contextlib
import os
import typing

# Alias for readability. Due to import recursion issues we cannot do:
# from .constants import LockFlags


if os.name == 'nt':  # pragma: no cover
    import msvcrt

    import pywintypes
    import win32con
    import win32file
    import winerror

    __overlapped = pywintypes.OVERLAPPED()

    def lock(file_: typing.Union[typing.IO, int], flags: LockFlags):
        # Windows locking does not support locking through `fh.fileno()` so
        # we cast it to make mypy and pyright happy
        file_ = typing.cast(typing.IO, file_)

        mode = 0
        if flags & LockFlags.NON_BLOCKING:
            mode |= win32con.LOCKFILE_FAIL_IMMEDIATELY

        if flags & LockFlags.EXCLUSIVE:
            mode |= win32con.LOCKFILE_EXCLUSIVE_LOCK

        # Save the old position so we can go back to that position but
        # still lock from the beginning of the file
        savepos = file_.tell()
        if savepos:
            file_.seek(0)

        os_fh = msvcrt.get_osfhandle(file_.fileno())  # type: ignore
        try:
            win32file.LockFileEx(os_fh, mode, 0, -0x10000, __overlapped)
        except pywintypes.error as exc_value:
            # error: (33, 'LockFileEx', 'The process cannot access the file
            # because another process has locked a portion of the file.')
            if exc_value.winerror == winerror.ERROR_LOCK_VIOLATION:
                raise AlreadyLocked(
                    LockException.LOCK_FAILED,
                    exc_value.strerror,
                    fh=file_,
                ) from exc_value
            else:
                # Q:  Are there exceptions/codes we should be dealing with
                # here?
                raise
        finally:
            if savepos:
                file_.seek(savepos)

    def unlock(file_: typing.IO):
        try:
            savepos = file_.tell()
            if savepos:
                file_.seek(0)

            os_fh = msvcrt.get_osfhandle(file_.fileno())  # type: ignore
            try:
                win32file.UnlockFileEx(
                    os_fh,
                    0,
                    -0x10000,
                    __overlapped,
                )
            except pywintypes.error as exc:
                if exc.winerror != winerror.ERROR_NOT_LOCKED:
                    # Q:  Are there exceptions/codes we should be
                    # dealing with here?
                    raise
            finally:
                if savepos:
                    file_.seek(savepos)
        except OSError as exc:
            raise LockException(
                LockException.LOCK_FAILED,
                exc.strerror,
                fh=file_,
            ) from exc

elif os.name == 'posix':  # pragma: no cover
    import fcntl

    def lock(file_: typing.Union[typing.IO, int], flags: LockFlags):
        locking_exceptions = (IOError,)
        with contextlib.suppress(NameError):
            locking_exceptions += (BlockingIOError,)  # type: ignore
        # Locking with NON_BLOCKING without EXCLUSIVE or SHARED enabled results
        # in an error
        if (flags & LockFlags.NON_BLOCKING) and not flags & (
            LockFlags.SHARED | LockFlags.EXCLUSIVE
        ):
            raise RuntimeError(
                'When locking in non-blocking mode the SHARED '
                'or EXCLUSIVE flag must be specified as well',
            )

        try:
            fcntl.flock(file_, flags)
        except locking_exceptions as exc_value:
            # The exception code varies on different systems so we'll catch
            # every IO error
            raise LockException(exc_value, fh=file_) from exc_value

    def unlock(file_: typing.IO):
        fcntl.flock(file_.fileno(), LockFlags.UNBLOCK)

else:  # pragma: no cover
    raise RuntimeError('PortaLocker only defined for nt and posix platforms')
import abc
import atexit
import contextlib
import logging
import os
import pathlib
import random
import tempfile
import time
import typing
import warnings

logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT = 5
DEFAULT_CHECK_INTERVAL = 0.25
DEFAULT_FAIL_WHEN_LOCKED = False
LOCK_METHOD = LockFlags.EXCLUSIVE | LockFlags.NON_BLOCKING

__all__ = [
    'Lock',
    'open_atomic',
]

Filename = typing.Union[str, pathlib.Path]


def coalesce(*args: typing.Any, test_value: typing.Any = None) -> typing.Any:
    '''Simple coalescing function that returns the first value that is not
    equal to the `test_value`. Or `None` if no value is valid. Usually this
    means that the last given value is the default value.

    Note that the `test_value` is compared using an identity check
    (i.e. `value is not test_value`) so changing the `test_value` won't work
    for all values.

    >>> coalesce(None, 1)
    1
    >>> coalesce()

    >>> coalesce(0, False, True)
    0
    >>> coalesce(0, False, True, test_value=0)
    False

    # This won't work because of the `is not test_value` type testing:
    >>> coalesce([], dict(spam='eggs'), test_value=[])
    []
    '''
    return next((arg for arg in args if arg is not test_value), None)


@contextlib.contextmanager
def open_atomic(
    filename: Filename,
    binary: bool = True,
) -> typing.Iterator[typing.IO]:
    '''Open a file for atomic writing. Instead of locking this method allows
    you to write the entire file and move it to the actual location. Note that
    this makes the assumption that a rename is atomic on your platform which
    is generally the case but not a guarantee.

    http://docs.python.org/library/os.html#os.rename

    >>> filename = 'test_file.txt'
    >>> if os.path.exists(filename):
    ...     os.remove(filename)

    >>> with open_atomic(filename) as fh:
    ...     written = fh.write(b'test')
    >>> assert os.path.exists(filename)
    >>> os.remove(filename)

    >>> import pathlib
    >>> path_filename = pathlib.Path('test_file.txt')

    >>> with open_atomic(path_filename) as fh:
    ...     written = fh.write(b'test')
    >>> assert path_filename.exists()
    >>> path_filename.unlink()
    '''
    # `pathlib.Path` cast in case `path` is a `str`
    path: pathlib.Path = pathlib.Path(filename)

    assert not path.exists(), '%r exists' % path

    # Create the parent directory if it doesn't exist
    path.parent.mkdir(parents=True, exist_ok=True)

    temp_fh = tempfile.NamedTemporaryFile(
        mode=binary and 'wb' or 'w',
        dir=str(path.parent),
        delete=False,
    )
    yield temp_fh
    temp_fh.flush()
    os.fsync(temp_fh.fileno())
    temp_fh.close()
    try:
        os.rename(temp_fh.name, path)
    finally:
        with contextlib.suppress(Exception):
            os.remove(temp_fh.name)


class LockBase(abc.ABC):  # pragma: no cover
    #: timeout when trying to acquire a lock
    timeout: float
    #: check interval while waiting for `timeout`
    check_interval: float
    #: skip the timeout and immediately fail if the initial lock fails
    fail_when_locked: bool

    def __init__(
        self,
        timeout: typing.Optional[float] = None,
        check_interval: typing.Optional[float] = None,
        fail_when_locked: typing.Optional[bool] = None,
    ):
        self.timeout = coalesce(timeout, DEFAULT_TIMEOUT)
        self.check_interval = coalesce(check_interval, DEFAULT_CHECK_INTERVAL)
        self.fail_when_locked = coalesce(
            fail_when_locked,
            DEFAULT_FAIL_WHEN_LOCKED,
        )

    @abc.abstractmethod
    def acquire(
        self,
        timeout: typing.Optional[float] = None,
        check_interval: typing.Optional[float] = None,
        fail_when_locked: typing.Optional[bool] = None,
    ):
        return NotImplemented

    def _timeout_generator(
        self,
        timeout: typing.Optional[float],
        check_interval: typing.Optional[float],
    ) -> typing.Iterator[int]:
        f_timeout = coalesce(timeout, self.timeout, 0.0)
        f_check_interval = coalesce(check_interval, self.check_interval, 0.0)

        yield 0
        i = 0

        start_time = time.perf_counter()
        while start_time + f_timeout > time.perf_counter():
            i += 1
            yield i

            # Take low lock checks into account to stay within the interval
            since_start_time = time.perf_counter() - start_time
            time.sleep(max(0.001, (i * f_check_interval) - since_start_time))

    @abc.abstractmethod
    def release(self):
        return NotImplemented

    def __enter__(self):
        return self.acquire()

    def __exit__(
        self,
        exc_type: typing.Optional[typing.Type[BaseException]],
        exc_value: typing.Optional[BaseException],
        traceback: typing.Any,  # Should be typing.TracebackType
    ) -> typing.Optional[bool]:
        self.release()
        return None

    def __delete__(self, instance):
        instance.release()


class Lock(LockBase):
    '''Lock manager with built-in timeout

    Args:
        filename: filename
        mode: the open mode, 'a' or 'ab' should be used for writing. When mode
            contains `w` the file will be truncated to 0 bytes.
        timeout: timeout when trying to acquire a lock
        check_interval: check interval while waiting
        fail_when_locked: after the initial lock failed, return an error
            or lock the file. This does not wait for the timeout.
        **file_open_kwargs: The kwargs for the `open(...)` call

    fail_when_locked is useful when multiple threads/processes can race
    when creating a file. If set to true than the system will wait till
    the lock was acquired and then return an AlreadyLocked exception.

    Note that the file is opened first and locked later. So using 'w' as
    mode will result in truncate _BEFORE_ the lock is checked.
    '''

    def __init__(
        self,
        filename: Filename,
        mode: str = 'a',
        timeout: typing.Optional[float] = None,
        check_interval: float = DEFAULT_CHECK_INTERVAL,
        fail_when_locked: bool = DEFAULT_FAIL_WHEN_LOCKED,
        flags: LockFlags = LOCK_METHOD,
        **file_open_kwargs,
    ):
        if 'w' in mode:
            truncate = True
            mode = mode.replace('w', 'a')
        else:
            truncate = False

        if timeout is None:
            timeout = DEFAULT_TIMEOUT
        elif not (flags & LockFlags.NON_BLOCKING):
            warnings.warn(
                'timeout has no effect in blocking mode',
                stacklevel=1,
            )

        self.fh: typing.Optional[typing.IO] = None
        self.filename: str = str(filename)
        self.mode: str = mode
        self.truncate: bool = truncate
        self.timeout: float = timeout
        self.check_interval: float = check_interval
        self.fail_when_locked: bool = fail_when_locked
        self.flags: LockFlags = flags
        self.file_open_kwargs = file_open_kwargs

    def acquire(
        self,
        timeout: typing.Optional[float] = None,
        check_interval: typing.Optional[float] = None,
        fail_when_locked: typing.Optional[bool] = None,
    ) -> typing.IO:
        '''Acquire the locked filehandle'''

        fail_when_locked = coalesce(fail_when_locked, self.fail_when_locked)

        if not (self.flags & LockFlags.NON_BLOCKING) and timeout is not None:
            warnings.warn(
                'timeout has no effect in blocking mode',
                stacklevel=1,
            )

        # If we already have a filehandle, return it
        fh: typing.Optional[typing.IO] = self.fh
        if fh:
            return fh

        # Get a new filehandler
        fh = self._get_fh()

        def try_close():  # pragma: no cover
            # Silently try to close the handle if possible, ignore all issues
            if fh is not None:
                with contextlib.suppress(Exception):
                    fh.close()

        exception = None
        # Try till the timeout has passed
        for _ in self._timeout_generator(timeout, check_interval):
            exception = None
            try:
                # Try to lock
                fh = self._get_lock(fh)
                break
            except LockException as exc:
                # Python will automatically remove the variable from memory
                # unless you save it in a different location
                exception = exc

                # We already tried to the get the lock
                # If fail_when_locked is True, stop trying
                if fail_when_locked:
                    try_close()
                    raise AlreadyLocked(exception) from exc

                # Wait a bit

        if exception:
            try_close()
            # We got a timeout... reraising
            raise LockException(exception)

        # Prepare the filehandle (truncate if needed)
        fh = self._prepare_fh(fh)

        self.fh = fh
        return fh

    def release(self):
        '''Releases the currently locked file handle'''
        if self.fh:
            unlock(self.fh)
            self.fh.close()
            self.fh = None

    def _get_fh(self) -> typing.IO:
        '''Get a new filehandle'''
        return open(  # noqa: SIM115
            self.filename,
            self.mode,
            **self.file_open_kwargs,
        )

    def _get_lock(self, fh: typing.IO) -> typing.IO:
        '''
        Try to lock the given filehandle

        returns LockException if it fails'''
        lock(fh, self.flags)
        return fh

    def _prepare_fh(self, fh: typing.IO) -> typing.IO:
        '''
        Prepare the filehandle for usage

        If truncate is a number, the file will be truncated to that amount of
        bytes
        '''
        if self.truncate:
            fh.seek(0)
            fh.truncate(0)

        return fh


class RLock(Lock):
    '''
    A reentrant lock, functions in a similar way to threading.RLock in that it
    can be acquired multiple times.  When the corresponding number of release()
    calls are made the lock will finally release the underlying file lock.
    '''

    def __init__(
        self,
        filename,
        mode='a',
        timeout=DEFAULT_TIMEOUT,
        check_interval=DEFAULT_CHECK_INTERVAL,
        fail_when_locked=False,
        flags=LOCK_METHOD,
    ):
        super().__init__(
            filename,
            mode,
            timeout,
            check_interval,
            fail_when_locked,
            flags,
        )
        self._acquire_count = 0

    def acquire(
        self,
        timeout: typing.Optional[float] = None,
        check_interval: typing.Optional[float] = None,
        fail_when_locked: typing.Optional[bool] = None,
    ) -> typing.IO:
        if self._acquire_count >= 1:
            fh = self.fh
        else:
            fh = super().acquire(timeout, check_interval, fail_when_locked)
        self._acquire_count += 1
        assert fh
        return fh

    def release(self):
        if self._acquire_count == 0:
            raise LockException(
                'Cannot release more times than acquired',
            )

        if self._acquire_count == 1:
            super().release()
        self._acquire_count -= 1


class TemporaryFileLock(Lock):
    def __init__(
        self,
        filename='.lock',
        timeout=DEFAULT_TIMEOUT,
        check_interval=DEFAULT_CHECK_INTERVAL,
        fail_when_locked=True,
        flags=LOCK_METHOD,
    ):
        Lock.__init__(
            self,
            filename=filename,
            mode='w',
            timeout=timeout,
            check_interval=check_interval,
            fail_when_locked=fail_when_locked,
            flags=flags,
        )
        atexit.register(self.release)

    def release(self):
        Lock.release(self)
        if os.path.isfile(self.filename):  # pragma: no branch
            os.unlink(self.filename)


class BoundedSemaphore(LockBase):
    '''
    Bounded semaphore to prevent too many parallel processes from running

    This method is deprecated because multiple processes that are completely
    unrelated could end up using the same semaphore.  To prevent this,
    use `NamedBoundedSemaphore` instead. The
    `NamedBoundedSemaphore` is a drop-in replacement for this class.

    >>> semaphore = BoundedSemaphore(2, directory='')
    >>> str(semaphore.get_filenames()[0])
    'bounded_semaphore.00.lock'
    >>> str(sorted(semaphore.get_random_filenames())[1])
    'bounded_semaphore.01.lock'
    '''

    lock: typing.Optional[Lock]

    def __init__(
        self,
        maximum: int,
        name: str = 'bounded_semaphore',
        filename_pattern: str = '{name}.{number:02d}.lock',
        directory: str = tempfile.gettempdir(),
        timeout: typing.Optional[float] = DEFAULT_TIMEOUT,
        check_interval: typing.Optional[float] = DEFAULT_CHECK_INTERVAL,
        fail_when_locked: typing.Optional[bool] = True,
    ):
        self.maximum = maximum
        self.name = name
        self.filename_pattern = filename_pattern
        self.directory = directory
        self.lock: typing.Optional[Lock] = None
        super().__init__(
            timeout=timeout,
            check_interval=check_interval,
            fail_when_locked=fail_when_locked,
        )

        if not name or name == 'bounded_semaphore':
            warnings.warn(
                '`BoundedSemaphore` without an explicit `name` '
                'argument is deprecated, use NamedBoundedSemaphore',
                DeprecationWarning,
                stacklevel=1,
            )

    def get_filenames(self) -> typing.Sequence[pathlib.Path]:
        return [self.get_filename(n) for n in range(self.maximum)]

    def get_random_filenames(self) -> typing.Sequence[pathlib.Path]:
        filenames = list(self.get_filenames())
        random.shuffle(filenames)
        return filenames

    def get_filename(self, number) -> pathlib.Path:
        return pathlib.Path(self.directory) / self.filename_pattern.format(
            name=self.name,
            number=number,
        )

    def acquire(
        self,
        timeout: typing.Optional[float] = None,
        check_interval: typing.Optional[float] = None,
        fail_when_locked: typing.Optional[bool] = None,
    ) -> typing.Optional[Lock]:
        assert not self.lock, 'Already locked'

        filenames = self.get_filenames()

        for n in self._timeout_generator(timeout, check_interval):  # pragma:
            logger.debug('trying lock (attempt %d) %r', n, filenames)
            # no branch
            if self.try_lock(filenames):  # pragma: no branch
                return self.lock  # pragma: no cover

        if fail_when_locked := coalesce(
            fail_when_locked,
            self.fail_when_locked,
        ):
            raise AlreadyLocked()

        return None

    def try_lock(self, filenames: typing.Sequence[Filename]) -> bool:
        filename: Filename
        for filename in filenames:
            logger.debug('trying lock for %r', filename)
            self.lock = Lock(filename, fail_when_locked=True)
            try:
                self.lock.acquire()
            except AlreadyLocked:
                self.lock = None
            else:
                logger.debug('locked %r', filename)
                return True

        return False

    def release(self):  # pragma: no cover
        if self.lock is not None:
            self.lock.release()
            self.lock = None


class NamedBoundedSemaphore(BoundedSemaphore):
    '''
    Bounded semaphore to prevent too many parallel processes from running

    It's also possible to specify a timeout when acquiring the lock to wait
    for a resource to become available.  This is very similar to
    `threading.BoundedSemaphore` but works across multiple processes and across
    multiple operating systems.

    Because this works across multiple processes it's important to give the
    semaphore a name.  This name is used to create the lock files.  If you
    don't specify a name, a random name will be generated.  This means that
    you can't use the same semaphore in multiple processes unless you pass the
    semaphore object to the other processes.

    >>> semaphore = NamedBoundedSemaphore(2, name='test')
    >>> str(semaphore.get_filenames()[0])
    '...test.00.lock'

    >>> semaphore = NamedBoundedSemaphore(2)
    >>> 'bounded_semaphore' in str(semaphore.get_filenames()[0])
    True

    '''

    def __init__(
        self,
        maximum: int,
        name: typing.Optional[str] = None,
        filename_pattern: str = '{name}.{number:02d}.lock',
        directory: str = tempfile.gettempdir(),
        timeout: typing.Optional[float] = DEFAULT_TIMEOUT,
        check_interval: typing.Optional[float] = DEFAULT_CHECK_INTERVAL,
        fail_when_locked: typing.Optional[bool] = True,
    ):
        if name is None:
            name = 'bounded_semaphore.%d' % random.randint(0, 1000000)
        super().__init__(
            maximum,
            name,
            filename_pattern,
            directory,
            timeout,
            check_interval,
            fail_when_locked,
        )


try:  # pragma: no cover
    from .redis import RedisLock
except ImportError:  # pragma: no cover
    RedisLock = None  # type: ignore


#: The package name on Pypi
#: Current author and maintainer, view the git history for the previous ones
#: Current author's email address
#: Version number
#: Package description for Pypi
#: Package homepage


#: Exception thrown when the file is already locked by someone else
#: Exception thrown if an error occurred during locking


#: Lock a file. Note that this is an advisory lock on Linux/Unix systems
#: Unlock a file

#: Place an exclusive lock.
#: Only one process may hold an exclusive lock for a given file at a given
#: time.
LOCK_EX: LockFlags = LockFlags.EXCLUSIVE

#: Place a shared lock.
#: More than one process may hold a shared lock for a given file at a given
#: time.
LOCK_SH: LockFlags = LockFlags.SHARED

#: Acquire the lock in a non-blocking fashion.
LOCK_NB: LockFlags = LockFlags.NON_BLOCKING

#: Remove an existing lock held by this process.
LOCK_UN: LockFlags = LockFlags.UNBLOCK

#: Locking flags enum

#: Locking utility class to automatically handle opening with timeouts and
#: context wrappers

__all__ = [
    'lock',
    'unlock',
    'LOCK_EX',
    'LOCK_SH',
    'LOCK_NB',
    'LOCK_UN',
    'LockFlags',
    'LockException',
    'Lock',
    'RLock',
    'AlreadyLocked',
    'BoundedSemaphore',
    'open_atomic',
    'RedisLock',
]
