#!/usr/bin/env python3
'''
Continuously reads data on stdin until there is no more data. Records how many
bytes there were and how long it took to read them. Prints this information.
'''
import time
import sys
import threading

write_lock = threading.Lock()
thread_done = threading.Event()

def report(stop_ev, start_time, last_byte_count):
    if stop_ev.is_set():
        thread_done.set()
        return
    global byte_count
    b = byte_count - last_byte_count
    t = time.time() - start_time
    r = b / t * 8 / 1000 / 1000
    with write_lock:
        print(
            '%d bytes in %f seconds (%0.2f Mbps)' % (b, t, r),
            file=sys.stderr)
    threading.Timer(1, report, [stop_ev, time.time(), byte_count]).start()

# Don't record the start time until we've read the first byte
fd = open('/dev/stdin', 'rb')
fd.read(1)
byte_count = 1
stop_ev = threading.Event()
threading.Timer(1, report, [stop_ev, time.time(), byte_count]).start()
start = time.time()
# Keep reading until no more data
data = 'foo'
try:
    while data:
        data = fd.read(4096)
        byte_count += len(data)
except KeyboardInterrupt:
    # print('')
    pass
finally:
    stop_ev.set()
thread_done.wait()
# Print stats
end = time.time()
duration = end - start
rate = byte_count / duration * 8 / 1000 / 1000
with write_lock:
    print('OVERALL: %d bytes in %0.2f seconds (%0.2f Mbps)' %\
        (byte_count, duration, rate), file=sys.stderr)
sys.stderr.flush()
fd.close()
