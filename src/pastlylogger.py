from datetime import datetime
from threading import Lock, current_thread
# Logging class inspired by Tor's logging API
class PastlyLogger:
    # error, warn, etc. are file names to open for logging.
    # If a log level doesn't have a file name given for it, messages destined
    # for that level cascade down to the next noisiest level.
    # Example 1: warn=foo.txt, debug=bar.txt
    #   error and warn messages go to foo.txt, all other messages to bar.txt
    # Example 2: notice=baz.txt
    #   error, warn, and notice messages go to baz.txt, all others are lost
    #
    # overwrite is a list of log levels that should overwrite their log file
    # when opening instead of appending.
    # Example: notice=a.txt, info=b.txt, overwrite=['info']
    #   error, warn, and notice messages are appended to a.txt;
    #   b.txt is overwritten and info messages are appended to it;
    #   all debug messages are lost
    def __init__(self, error=None, warn=None, notice=None,
        info=None, debug=None, overwrite=[]):

        # buffering=1 means line-based buffering
        if error:
            self.error_fd = open(error, 'w' if 'error' in overwrite else 'a',
                buffering=1)
            self.error_fd_mutex = Lock()
        else:
            self.error_fd = None
            self.error_fd_mutex = None
        if warn:
            self.warn_fd = open(warn, 'w' if 'warn' in overwrite else 'a',
                buffering=1)
            self.warn_fd_mutex = Lock()
        else:
            self.warn_fd = None
            self.warn_fd_mutex = None
        if notice:
            self.notice_fd = open(notice, 'w' if 'notice' in overwrite else 'a',
                buffering=1)
            self.notice_fd_mutex = Lock()
        else:
            self.notice_fd = None
            self.notice_fd_mutex = None
        if info:
            self.info_fd = open(info, 'w' if 'info' in overwrite else 'a',
                buffering=1)
            self.info_fd_mutex = Lock()
        else:
            self.info_fd = None
            self.info_fd_mutex = None
        if debug:
            self.debug_fd = open(debug, 'w' if 'debug' in overwrite else 'a',
                buffering=1)
            self.debug_fd_mutex = Lock()
        else:
            self.debug_fd = None
            self.debug_fd_mutex = None

        self.debug('Creating PastlyLogger instance')

    def __del__(self):
        self.debug('Deleting PastlyLogger instance')
        self.flush()
        if self.error_fd: self.error_fd.close()
        if self.warn_fd: self.warn_fd.close()
        if self.notice_fd: self.notice_fd.close()
        if self.info_fd: self.info_fd.close()
        if self.debug_fd: self.debug_fd.close()
        self.error_fd, self.warn_fd = None, None
        self.notice_fd, self.info_fd, self.debug_fd = None, None, None
        if self.error_fd_mutex:
            if not self.error_fd_mutex.acquire(blocking=False):
                self.error_fd_mutex.release()
        if self.warn_fd_mutex:
            if not self.warn_fd_mutex.acquire(blocking=False):
                self.warn_fd_mutex.release()
        if self.notice_fd_mutex:
            if not self.notice_fd_mutex.acquire(blocking=False):
                self.notice_fd_mutex.release()
        if self.info_fd_mutex:
            if not self.info_fd_mutex.acquire(blocking=False):
                self.info_fd_mutex.release()
        if self.debug_fd_mutex:
            if not self.debug_fd_mutex.acquire(blocking=False):
                self.debug_fd_mutex.release()

    def _log_file(fd, lock, s, level):
        assert fd
        lock.acquire()
        ts = datetime.now()
        if current_thread():
            fd.write('[{}] [{}] [{}] {}\n'.format(ts, level, current_thread().name,s))
        else:
            fd.write('[{}] [{}] {}\n'.format(ts, level, s))
        lock.release()

    def flush(self):
        if self.error_fd: self.error_fd.flush()
        if self.warn_fd: self.warn_fd.flush()
        if self.notice_fd: self.notice_fd.flush()
        if self.info_fd: self.info_fd.flush()
        if self.debug_fd: self.debug_fd.flush()

    def debug(self, s, level='debug'):
        if self.debug_fd: return PastlyLogger._log_file(
            self.debug_fd, self.debug_fd_mutex, s, level)
        return None

    def info(self, s, level='info'):
        if self.info_fd: return PastlyLogger._log_file(
            self.info_fd, self.info_fd_mutex, s, level)
        else: return self.debug(s, level)

    def notice(self, s, level='notice'):
        if self.notice_fd: return PastlyLogger._log_file(
            self.notice_fd, self.notice_fd_mutex, s, level)
        else: return self.info(s, level)

    def warn(self, s, level='warn'):
        if self.warn_fd: return PastlyLogger._log_file(
            self.warn_fd, self.warn_fd_mutex, s, level)
        else: return self.notice(s, level)

    def error(self, s, level='error'):
        if self.error_fd: return PastlyLogger._log_file(
            self.error_fd, self.error_fd_mutex, s, level)
        else: return self.warn(s, level)
