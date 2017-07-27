from datetime import datetime
def log(*msg):
    ts = '[{}]'.format(datetime.now())
    if msg: print(ts,*msg)
def warn(*msg):
    if msg: log('[WARN]',*msg)
def fail_hard(*msg):
    if msg: log('[ERROR]',*msg)
    exit(1)
