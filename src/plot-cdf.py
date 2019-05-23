#!/usr/bin/env python3

import sys, random
from argparse import ArgumentDefaultsHelpFormatter, ArgumentParser
import matplotlib; matplotlib.use('Agg') # for systems without X11
from matplotlib.backends.backend_pdf import PdfPages
import pylab as plt
import numpy as np
import random

plt.rcParams.update({
    'axes.grid' : True,
})

## helper - cumulative fraction for y axis
def cf(d): return plt.arange(1.0,float(len(d))+1.0)/float(len(d))

## helper - return step-based CDF x and y values
def getcdf(data):
    data.sort()
    frac = cf(data)
    x, y, lasty = [], [], 0.0
    for i in range(len(data)):
        assert not np.isnan(data[i])
        x.append(data[i])
        y.append(lasty)
        x.append(data[i])
        y.append(frac[i])
        lasty = frac[i]
    return x, y

def get_all_values_from_fd(fd):
    values = []
    for line in fd:
        line = line.strip()
        try: values.append(float(line))
        except: print('ignoring', line)
    return values

def print_percentiles(label, values):
    try:
        from scipy.stats import scoreatpercentile as percentile
    except ImportError:
        print('WARN: no scipy means no percentile stats printed')
        return
    d = {
        0: min(values),
        5: percentile(values, 5),
        25: percentile(values, 25),
        50: percentile(values, 50),
        75: percentile(values, 75),
        95: percentile(values, 95),
        100: max(values),
    }
    for k, v in d.items():
        print('%s: %d percentile: %f' % (label, k, v))

def main(args, pdf):
    plt.figure()
    if not args.input:
        values = get_all_values_from_fd(sys.stdin)
        if args.max_points >= 0 and len(values) > args.max_points:
            values = random.sample(values, args.max_points)
        plt.plot(*getcdf(values))
        print_percentiles('stdin', values)
        plt.xlim(xmin=min(values), xmax=max(values))
    else:
        all_min, all_max = None, None
        for fname, label in args.input:
            with open(fname, 'rt') as fd:
                values = get_all_values_from_fd(fd)
            if args.max_points >= 0 and len(values) > args.max_points:
                values = random.sample(values, args.max_points)
            this_min, this_max = min(values), max(values)
            if all_min == None or this_min < all_min: all_min = this_min
            if all_max == None or this_max > all_max: all_max = this_max
            plt.plot(*getcdf(values), label=label)
            print_percentiles(label, values)
        plt.xlim(xmin=all_min, xmax=all_max)
        plt.legend(loc='lower right')
    plt.ylim(ymin=0, ymax=1)
    if args.label: plt.xlabel(args.label)
    if args.title: plt.title(args.title)
    plt.ylabel('CDF')
    pdf.savefig()

if __name__=='__main__':
    parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter,
        description='Takes one or more lists of values, one per line, and '
        'plots a CDF of them. Values may either be given on stdin or read '
        'from one or more files.')
    parser.add_argument('-i', '--input', nargs=2, metavar=('FNAME', 'LABEL'),
        action='append', help='Specify a file to read values from and what '
        'to label its line in the PDF. If given 0 times, data will be '
        'read from stdin. Can be given more than once. The only time data '
        'will be read from stdin is if it is given 0 times.')
    parser.add_argument('-o', '--output', default='temp.pdf')
    parser.add_argument('-l', '--label', type=str,
        help='What to label the X axis in the PDF')
    parser.add_argument('-t', '--title', type=str,
        help='What to title the plot in the PDF')
    parser.add_argument('--max-points', default=10000, type=int,
        help='Maximum number of points on a line. Negative means infinite')
    args = parser.parse_args()
    with PdfPages(args.output) as pdf:
        exit(main(args, pdf))
