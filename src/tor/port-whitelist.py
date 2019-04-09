#!/usr/bin/env python3
from argparse import ArgumentParser, RawDescriptionHelpFormatter
from stem.control import Controller, EventType
import logging
import queue

logging.basicConfig(level=logging.DEBUG)
log = logging


def main(args, cont):
    allow = args.allow or []
    block = args.block or []
    assert args.default in {'block', 'allow'}
    q = queue.Queue(maxsize=1)
    cont.add_event_listener(add_stream_to_queue(q), EventType.STREAM)
    while True:
        ev = q.get()
        port = int(ev.target_port)
        if args.default == 'block' and port not in allow:
            log.info('Closing: %s', ev)
            cont.close_stream(ev.id)
        elif args.default == 'allow' and port in block:
            log.info('Closing: %s', ev)
            cont.close_stream(ev.id)
        else:
            log.debug('Allowing: %s', ev)


def _get_controller_port(args):
    return Controller.from_port(port=args.ctrl_port)


def _get_controller_socket(args):
    return Controller.from_socket_file(path=args.ctrl_socket)


def get_controller(args):
    if args.ctrl_port:
        c = _get_controller_port(args)
    else:
        c = _get_controller_socket(args)
    c.authenticate()
    return c


def add_stream_to_queue(queue):
    def add_stream_to_queue_impl(ev):
        if ev.status in {'NEW'} and ev.purpose in {'USER'}:
            queue.put(ev)
        else:
            log.debug('Ignoring stream event: %s', ev)
    return add_stream_to_queue_impl


if __name__ == '__main__':
    # :set tw=70 for this variable
    d = '''
Connect to a running Tor process and only allow it to connect to one
or more ports, or disallow it from connecting to one or more ports.

Control port/socket hints:
    - Many Linux distros' system Tor daemon defaults to opening a
    ControlPort on 9051
    - Tor Browser opens a ControlPort on 9151
'''
    parser = ArgumentParser(
        formatter_class=RawDescriptionHelpFormatter,
        description=d,
    )
    parser.add_argument(
        '-p', '--ctrl-port', metavar='PORT', type=int,
        default=None,
        help='Port on which to control the tor client')
    parser.add_argument(
        '-s', '--ctrl-socket', metavar='SOCK', type=str,
        default=None,
        help='Path to socket with which to control the tor client')
    parser.add_argument(
        '--default', choices=('allow', 'block'), default='block')
    parser.add_argument(
        '-a', '--allow', nargs='+', type=int,
        help='One or more ports to allow')
    parser.add_argument(
        '-b', '--block', nargs='+', type=int,
        help='One or more ports to disallow')
    args = parser.parse_args()

    if not args.ctrl_port and not args.ctrl_socket:
        log.error('Give either --ctrl-port or --ctrl-socket')
        exit(1)
    if args.ctrl_port and args.ctrl_socket:
        log.error('Only give --ctrl-port or --ctrl-socket, not both')
        exit(1)
    if args.allow and args.block:
        log.error('May only specify --allow or --block, not both')
        exit(1)
    if args.default == 'allow' and not args.block:
        log.error(
            'Ineffective arguments: would allow all traffic by default, and '
            'block nothing')
        exit(1)
    if args.default == 'block' and not args.allow:
        log.error(
            'Ineffective arguments: would block all traffic by default, and '
            'allow nothing')
        exit(1)

    with get_controller(args) as cont:
        try:
            exit(main(args, cont))
        except KeyboardInterrupt:
            pass
