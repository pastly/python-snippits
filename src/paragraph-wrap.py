#!/usr/bin/env python3
from argparse import ArgumentDefaultsHelpFormatter, ArgumentParser
import sys
import textwrap


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


def wrap_paragraph(textwrapper, paragraph, width, do_pad):
    # do the wrapping, but doesn't do padding
    wrapped_lines = textwrapper.wrap(paragraph)
    # need the line number in order to determine when we're on the last line of
    # the reformatted paragraph: if we are and we are padding, then we don't
    # want to pad that line.
    for line_num, wrapped_line in enumerate(wrapped_lines):
        words = wrapped_line.split()
        # if not last line and padding, then pad with extra spaces
        if line_num + 1 != len(wrapped_lines) and do_pad:
            # how many ' ' can fit
            total_spaces = width - sum([len(w) for w in words])
            # split the ' '-budget up as evenly as possible between each word
            space_iter = [
                ' ' * i for i in
                split_x_by_y(total_spaces, len(words) - 1)]
        # either the last line or not padding (or both), so just one space
        # between each word.
        else:
            space_iter = [' '] * (len(words) - 1)
        # needs one more "space" to be the same length as the word list. add a
        # dummy space so zip() works correctly
        space_iter += ['']
        # OUTPUT :D
        s = ''
        for word, white in zip(words, space_iter):
            s += word + white
        yield s


def main(fd_in, fd_out, width, do_pad):
    tw = textwrap.TextWrapper(width=width)
    paragraph = ''
    for in_line in fd_in:
        # append the in_line to the accumulating paragraph. in_line has a
        # trailing \n
        paragraph += in_line
        # blank line, so process and output accumulated paragraph
        if not len(in_line.strip()):
            # all the hard work is done in wrap_paragraph
            for out_line in wrap_paragraph(
                    tw, paragraph.rstrip(), width, do_pad):
                print(out_line, file=fd_out)
            # clear the accumulator
            paragraph = ''
            # output a blank line before the next paragraph
            print('')
    # if there's leftover text, print it
    if len(paragraph):
        for out_line in wrap_paragraph(tw, paragraph.rstrip(), width, do_pad):
            print(out_line, file=fd_out)


if __name__ == '__main__':
    p = ArgumentParser(
        formatter_class=ArgumentDefaultsHelpFormatter,
        description='Read paragraphs of text on stdin, where paragraphs are '
        'broken up by empty lines. Wrap each line in each paragraph to a '
        'maximum width, and optinally pad each line internally with spaces '
        'such that it is exactly the desired with.'
    )
    p.add_argument(
        '-w', '--width', type=int, default=80, help='Number of columns')
    p.add_argument('--pad', action='store_true')
    args = p.parse_args()
    main(sys.stdin, sys.stdout, args.width, args.pad)
