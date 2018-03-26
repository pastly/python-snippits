#!/usr/bin/env python3

import sys
import random
from argparse import ArgumentDefaultsHelpFormatter, ArgumentParser
import matplotlib; matplotlib.use('Agg')  # noqa; for systems without X11
from matplotlib.backends.backend_pdf import PdfPages
import pylab as plt

plt.rcParams.update({
    'axes.grid': True,
})


def get_all_values_from_fd(fd):
    values = []
    for line in fd:
        try:
            x, y = line.strip().split()
            values.append((float(x), float(y)))
        except ValueError:
            print('ignoring', line)
            continue
    return values


def main(args, pdf):
    plt.figure()
    if not args.input:
        values = get_all_values_from_fd(sys.stdin)
        if args.max_points >= 0 and len(values) > args.max_points:
            values = random.sample(values, args.max_points)
        x = [v[0] for v in values]
        y = [v[1] for v in values]
        plt.scatter(x, y, s=args.size)
        plt.xlim(xmin=min(x), xmax=max(x))
        plt.ylim(ymin=min(y), ymax=max(y))
    else:
        all_min_x, all_max_x = None, None
        all_min_y, all_max_y = None, None
        for fname, label in args.input:
            with open(fname, 'rt') as fd:
                values = get_all_values_from_fd(fd)
            if args.max_points >= 0 and len(values) > args.max_points:
                values = random.sample(values, args.max_points)
            x = [v[0] for v in values]
            y = [v[1] for v in values]
            this_min_x, this_max_x = min(x), max(x)
            this_min_y, this_max_y = min(y), max(y)
            if all_min_x is None or this_min_x < all_min_x:
                all_min_x = this_min_x
            if all_max_x is None or this_max_x > all_max_x:
                all_max_x = this_max_x
            if all_min_y is None or this_min_y < all_min_y:
                all_min_y = this_min_y
            if all_max_y is None or this_max_y > all_max_y:
                all_max_y = this_max_y
            plt.scatter(x, y, s=args.size, label=label)
        plt.xlim(xmin=all_min_x, xmax=all_max_x)
        plt.ylim(ymin=all_min_y, ymax=all_max_y)
        plt.legend(loc='lower right')
    if args.xlabel:
        plt.xlabel(args.xlabel)
    if args.ylabel:
        plt.ylabel(args.ylabel)
    if args.title:
        plt.title(args.title)
    pdf.savefig()


if __name__ == '__main__':
    parser = ArgumentParser(
        formatter_class=ArgumentDefaultsHelpFormatter,
        description='Takes one or more lists of (x, y) points, one per line, '
        'and plots a scatter of them. Values may either be given on stdin or '
        'read from one or more files.')
    parser.add_argument(
        '-i', '--input', nargs=2, metavar=('FNAME', 'LABEL'),
        action='append', help='Specify a file to read values from and what '
        'to label its line in the PDF. If given 0 times, data will be '
        'read from stdin. Can be given more than once. The only time data '
        'will be read from stdin is if it is given 0 times.')
    parser.add_argument('-o', '--output', default='temp.pdf')
    parser.add_argument('-x', '--xlabel', type=str,
                        help='What to label the X axis in the PDF')
    parser.add_argument('-y', '--ylabel', type=str,
                        help='What to label the Y axis in the PDF')
    parser.add_argument('-t', '--title', type=str,
                        help='What to title the plot in the PDF')
    parser.add_argument('--max-points', default=10000, type=int,
                        help='Maximum number of points on a line. Negative '
                        'means infinite')
    parser.add_argument('-s', '--size', type=float, default=5,
                        help='Size of scatter plot points')
    args = parser.parse_args()
    with PdfPages(args.output) as pdf:
        exit(main(args, pdf))
