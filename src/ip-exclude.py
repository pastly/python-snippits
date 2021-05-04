#!/usr/bin/env python3
import ipaddress
import textwrap
from argparse import ArgumentDefaultsHelpFormatter, ArgumentParser

# Getting IPv4 address ranges of OVH: visit these pages.
#    https://bgp.he.net/AS16276#_prefixes
#    https://bgp.he.net/AS35540#_prefixes
# Manually copy paste the tables into a text file. Hope you're efficent at vim
# or some other text editor so you can remove everything except the networks.
# Save the text file.

# # Getting IPv4 addresses of OVH relays
# curl https://onionoo.torproject.org/details?search=as:AS16276 > a
# curl https://onionoo.torproject.org/details?search=as:AS35540 > b
# jq -r .relays[].or_addresses[] a b | sort > c
# <c grep -vF '[' | cut -d ':' -f 1 > ovh-relays.txt
# rm a b c


def _wrap_line(tw, s):
    ''' Given a :class:`textwrap.TextWrapper` and a single long line of text
    ``s``, wrap ``s`` after reducing whitespace between its words to a single
    space. '''
    return tw.wrap(' '.join(s.split()))


def wrap_text(s, max_width):
    ''' Wrap the given multi-line string ``s`` such that each line is no more
    than ``max_width`` characters.

    The input text can be more than one paragraph, in which case each paragraph
    is wrapped separately. Paragraphs are deliminated with blank lines::

        This is one
        very short paragraph.

        And this is the start of another paragraph.

    This function yields wrapped lines, each *with* a trailing newline. It may,
    in the case of the input containing multiple paragraphs, return lines that
    are simply a single newline character.
    '''
    # object that actually does the wrapping
    tw = textwrap.TextWrapper(width=max_width)
    # accumulate the current working paragraph here
    acc = ''
    # strip unnecessary whitespace from left of top-most line and right of
    # bottom-most line
    s = s.strip()
    for in_line in s.split('\n'):
        # Append the input line to the accumulating paragraph. Add a space so
        # that there's always *at least* one space between words. Later we will
        # make it *exactly* one space.
        acc += ' ' + in_line
        # if the in_line is actually all just whitespace, then we've reached
        # the end of the current paragraph and should output it as wrapped
        # lines.
        if not len(in_line.strip()):
            for out_line in _wrap_line(tw, acc):
                yield out_line + '\n'
            # clear paragraph
            acc = ''
            # output a blank line before the next paragraph
            yield '\n'
    # if there's leftover text, print it
    if len(acc):
        for out_line in _wrap_line(tw, acc):
            yield out_line + '\n'


def print_list_as_comment(l):
    s = '\n'.join([str(_) for _ in l])
    for line in wrap_text(s, 75):
        print(f'#    {line}', end='')


def read_fd(fd):
    ''' Create a set with all the IPv4 networks listed in the given file-like
    object. Ignore empty lines and comment lines (starting with '#'). '''
    s = set()
    for line in fd:
        line = line.strip()
        if not len(line) or line.startswith('#'):
            continue
        s.add(ipaddress.ip_network(line))
    return s


def main(include_fd, exclude_fd):
    include_nets, exclude_nets = set(), set()
    output_nets = set()
    include_nets = read_fd(include_fd)
    exclude_nets = read_fd(exclude_fd)
    print(f'# {len(include_nets)} input include nets:')
    print_list_as_comment(sorted(include_nets))
    print(f'# {len(exclude_nets)} input exclude nets:')
    print_list_as_comment(sorted(exclude_nets))
    output_nets = set()
    while len(include_nets):
        in_net = include_nets.pop()
        for ex_net in exclude_nets:
            if in_net.overlaps(ex_net):
                new = in_net.address_exclude(ex_net)
                include_nets.update(new)
                break
        else:
            output_nets.add(in_net)
    print(f'# {len(output_nets)} output nets')
    for out_net in sorted(output_nets):
        print(out_net)
    # sanity check. Due to the way the overlaps() function works, I worry that
    # certain types of input could result in these checks failing
    for out_net in output_nets:
        for ex_net in exclude_nets:
            assert not out_net.overlaps(ex_net)


if __name__ == '__main__':
    parser = ArgumentParser(
        formatter_class=ArgumentDefaultsHelpFormatter,
        description='Takes a list of IPv4 subnets to include. Takes a '
        'list of IPv4 subnets to exclude. Output the inlcude-list of '
        'subnets, modified such that they do not include any IP space '
        'in the exclude list.')
    parser.add_argument(
        'include_file', type=str,
        help='File from which to read IPv4 subnets to include, one per '
        'line. Format: 1.2.3.4/5')
    parser.add_argument(
        'exclude_file', type=str,
        help='File from which to read IPv4 subnets to exclude, one per '
        'line. Format: 1.2.3.4/5')
    args = parser.parse_args()
    try:
        main(
            open(args.include_file, 'rt'),
            open(args.exclude_file, 'rt'))
    except KeyboardInterrupt:
        print()
