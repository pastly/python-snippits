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

def main(args):
    values = []
    for line in sys.stdin:
        line = line.strip() 
        try: values.append(float(line))
        except: print('ignoring', line)
    if args.max_points >= 0 and len(values) > args.max_points:
        values = random.sample(values, args.max_points)
    with PdfPages(args.output) as pdf:
        plt.figure()
        plt.plot(*getcdf(values))
        plt.ylim(ymin=0, ymax=1)
        plt.xlim(xmin=min(values), xmax=max(values))
        if args.label: plt.xlabel(args.label)
        if args.title: plt.title(args.title)
        plt.ylabel('CDF')
        pdf.savefig()

if __name__=='__main__':
    parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter,
        description='Take a list of values on stdin, one value per line, and '
        'plot a CDF of them')
    parser.add_argument('-o', '--output', default='temp.pdf')
    parser.add_argument('-l', '--label', type=str,
        help='What to label the data in the PDF')
    parser.add_argument('-t', '--title', type=str,
        help='What to title the plot in the PDF')
    parser.add_argument('--max-points', default=10000, type=int,
        help='Negative means infinite')
    args = parser.parse_args()
    exit(main(args))
