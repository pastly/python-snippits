#!/usr/bin/env python3
from argparse import ArgumentDefaultsHelpFormatter, ArgumentParser
import time

from stem.control import Controller


def get_controller(args):
    if not args.ctrl_port and not args.ctrl_socket:
        exit(1)
    c = None
    if args.ctrl_port:
        c = Controller.from_port(port=args.ctrl_port)
    elif args.ctrl_socket:
        c = Controller.from_socket_file(path=args.ctrl_socket)
    c.authenticate()
    assert c.is_authenticated()
    return c


def main(args):
    cont = get_controller(args)
    cont.add_event_listener(lambda ev: print('%0.4f' % time.time(), ev, flush=True), 'BW')
    while True: time.sleep(100)


if __name__ == '__main__':
    parser = ArgumentParser(
        formatter_class=ArgumentDefaultsHelpFormatter,
        description='Connect to a Tor client and log CONN_BW events')
    parser.add_argument(
        '-s', '--ctrl-socket', type=str, help='Path to a Tor ControlSocket. If '
        'both this and --ctrl-port are given, this wins')
    parser.add_argument(
        '-p', '--ctrl-port', type=str, help='A Tor ControlPort')
    args = parser.parse_args()
    assert args.ctrl_socket or args.ctrl_port
    try:
        main(args)
    except KeyboardInterrupt:
        print()
