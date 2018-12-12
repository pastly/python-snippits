#!/usr/bin/env python3
'''
Continuously reads data on stdin until there is no more data. Records how many
bytes there were and how long it took to read them. Prints this information.
'''
import time
import sys

# Don't record the start time until we've read the first byte
data = sys.stdin.read(1)
byte_count = 1
start = time.time()
# Keep reading until no more data
while data:
    data = sys.stdin.read(4096)
    byte_count += len(data)
# Print stats
end = time.time()
duration = end - start
rate = byte_count / duration * 8 / 1000 / 1000
print('%d bytes in %0.2f seconds (%0.2f Mbps)' %\
      (byte_count, duration, rate), file=sys.stderr)
