# Split a list into batches of size n
# https://stackoverflow.com/q/8290397
def batch(iterable, n = 1):
   current_batch = []
   for item in iterable:
       current_batch.append(item)
       if len(current_batch) == n:
           yield current_batch
           current_batch = []
   if current_batch:
       yield current_batch


def split_x_by_y(x, y):
    ''' Divide X as evenly as possible Y ways using only ints, and return those
    ints. Consider x=5 and y=3. 5 cannot be divided into 3 pieces evenly using
    ints. This function would yield a generator producing 1, 2, 2.

    x=8, y=5 yields 1, 2, 1, 2, 2.
    x=6, y=3 yields 2, 2, 2
    '''
    frac_accum = 0
    for iters_left in range(y-1, 0-1, -1):
        frac_accum += x % y
        if frac_accum >= y or not iters_left and frac_accum:
            yield x // y + 1
        else:
            yield x // y
        if frac_accum >= y:
            frac_accum -= y
