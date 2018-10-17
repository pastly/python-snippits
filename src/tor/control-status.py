#!/usr/bin/env python3
from argparse import ArgumentDefaultsHelpFormatter, ArgumentParser
import stem
from stem.control import Controller
from curses import wrapper
import time


def myprint(s, *words):
    s.addstr(' '.join([str(w) for w in words])+'\n')


def print_stats(scr, cont, only_used_circs):
    all_circs = []
    all_streams = cont.get_streams()
    for circ in cont.get_circuits():
        path = [nick for fp, nick in circ.path]
        streams = [s for s in all_streams if s.circ_id == circ.id]
        all_circs.append({
            'id': int(circ.id),
            'path': path,
            'used': True if len(streams) else False,
            'targets': [s.target for s in streams],
        })
    all_circs = sorted(all_circs, key=lambda c: c['id'])
    for circ in all_circs:
        s = '*' if circ['used'] else ' '
        s += ' {} {}'.format(circ['id'], ' '.join(circ['path']))
        if circ['used']:
            s += ' (' + ','.join(circ['targets']) + ')'
            if only_used_circs:
                myprint(scr, s)
        if not only_used_circs:
            myprint(scr, s)
    myprint(
        scr, len(all_streams), 'streams; {}/{} circuits in use'.format(
            len([c for c in all_circs if c['used']]), len(all_circs)))


def _get_controller_port(args):
    return Controller.from_port(port=args.ctrl_port)


def _get_controller_socket(args):
    return Controller.from_socket_file(path=args.socket)


def get_controller(args):
    try:
        cont = _get_controller_port(args)
    except stem.SocketError:
        cont = _get_controller_socket(args)
    return cont


def main(stdscr, args):
    stdscr.clear()
    with get_controller(args) as cont:
        cont.authenticate()
        assert cont.is_authenticated()
        while True:
            stdscr.erase()
            print_stats(stdscr, cont, args.only_used)
            stdscr.refresh()
            time.sleep(args.interval)


def pre_main():
    parser = ArgumentParser(
            formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument(
        '-p', '--ctrl-port', metavar='PORT', type=int,
        help='Port on which to control the tor client', default=9051)
    parser.add_argument(
        '-s', '--socket', metavar='SOCK', type=str,
        help='Path to socket with which to control the tor client',
        default='/var/run/tor/control')
    parser.add_argument(
        '-i', '--interval', metavar='SECS', type=float,
        help='How often to update screen', default=1.0)
    parser.add_argument(
        '--only-used', action='store_true',
        help='Only print circuits with 1 or more streams')
    args = parser.parse_args()
    return wrapper(main, args)


if __name__ == '__main__':
    try:
        exit(pre_main())
    except KeyboardInterrupt:
        pass
