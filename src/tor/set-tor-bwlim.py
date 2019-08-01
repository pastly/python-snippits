#!/usr/bin/env python3
from argparse import ArgumentDefaultsHelpFormatter, ArgumentParser
import sys
import os
from stem.control import Controller


def log(*a, **kw):
    me = os.path.basename(sys.argv[0])
    return print('%s:' % (me,), *a, file=sys.stderr, **kw)


def get_controller(args):
    assert args.ctrl_port or args.ctrl_socket
    assert not (args.ctrl_port and args.ctrl_socket)
    c = None
    if args.ctrl_port:
        c = Controller.from_port(port=args.ctrl_port)
    elif args.ctrl_socket:
        c = Controller.from_socket_file(path=args.ctrl_socket)
    c.authenticate()
    log('We are%s connected to Tor' % (
        '' if c.is_authenticated() else ' not',))
    return c


def bytes_to_mbits(b):
    return round(b * 8 / 1000 / 1000)


def mbits_to_bytes(b):
    return round(b / 8 * 1000 * 1000)


def main(args):
    c = get_controller(args)
    old_rate = int(c.get_conf('RelayBandwidthRate'))
    old_burst = int(c.get_conf('RelayBandwidthBurst'))
    log(old_rate, old_burst)
    new_rate = mbits_to_bytes(args.rate)
    new_burst = mbits_to_bytes(args.burst)
    log(
        'Changing RelayBandwidthRate from %s Mbit/s to %s Mbit/s' % (
            bytes_to_mbits(old_rate), bytes_to_mbits(new_rate)))
    log(
        'Changing RelayBandwidthBurst from %s Mbit/s to %s Mbit/s' % (
            bytes_to_mbits(old_burst), bytes_to_mbits(new_burst)))
    try:
        c.set_options({
            'RelayBandwidthRate': str(new_rate),
            'RelayBandwidthBurst': str(new_burst),
        })
    except Exception as e:
        log('Error setting options:', e)
        return 1
    return 0


if __name__ == '__main__':
    parser = ArgumentParser(
        formatter_class=ArgumentDefaultsHelpFormatter,
        description='Connect to a Tor process and set its '
        'RelayBandwidth{Rate,Burst} options. You must specify either -s or -p '
        'as the ControlSocket or ControlPort on which the Tor process is '
        'listening. --rate must be provided, and if --burst is unspecified, '
        'it defaults to the value of --rate.'
    )
    parser.add_argument(
        '-s', '--ctrl-socket', type=str, help='Path to a Tor ControlSocket')
    parser.add_argument(
        '-p', '--ctrl-port', type=int, help='A Tor ControlPort')
    parser.add_argument('--rate', type=int, required=True)
    parser.add_argument('--burst', type=int)
    args = parser.parse_args()
    if args.ctrl_socket and args.ctrl_port:
        log('Do not specify both -s and -p')
        exit(1)
    if not args.ctrl_socket and not args.ctrl_port:
        log('Specify one of either -s or -p')
        exit(1)
    if args.rate < 10:
        log('--rate must be at least 10 Mbit/s')
        exit(1)
    if not args.burst:
        log('--burst not set, setting to --rate\'s value of %d' % (args.rate,))
        args.burst = args.rate
    if args.burst < 10:
        log('--burst must be at least 10 Mbit/s')
        exit(1)
    exit(main(args))
