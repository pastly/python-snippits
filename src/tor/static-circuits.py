#!/usr/bin/env python3
from argparse import ArgumentDefaultsHelpFormatter, ArgumentParser
import logging
import os
import queue
import time

from stem.control import Controller, EventType


logging.basicConfig(format='%(asctime)s %(levelname)s %(threadName)s '
                    '%(filename)s:%(lineno)s - %(funcName)s - %(message)s',
                    level=logging.DEBUG)
log = logging.getLogger(__name__)
stream_queue = queue.Queue(maxsize=1)

def loop_iter_forever(l):
    while True:
        for i in l:
            yield i


def add_new_stream_to_queue(stream_event):
    if stream_event.status in ['NEW', 'NEWRESOLVE']:
        stream_queue.put(stream_event)

def close_circ_for_closing_stream(controller, stream_event):
    if stream_event.status in ['FAILED', 'CLOSED']:
        log.debug(stream_event)
        if stream_event.circ_id:
            log.info(
                'Closing circ %s', circuit_str(
                    controller, stream_event.circ_id))
            controller.close_circuit(stream_event.circ_id)

def parse_circuit_list_fd(fd):
    out = []
    for line in fd:
        line = line.strip()
        if not len(line):
            continue
        if line[0] == '#':
            continue
        parts = line.split()
        if len(parts) < 2:
            continue
        for part in parts:
            if len(part) != 40:
                continue
        out.append(parts)
    return out


def circuit_str(controller, circ_id):
    assert isinstance(circ_id, str)
    int(circ_id)
    try:
        circ = controller.get_circuit(circ_id)
    except ValueError as e:
        log.warning('Circuit %s no longer seems to exist so can\'t return '
                    'a valid circuit string for it: %s', circ_id, e)
        return '[unknown]'
    except ControllerError as e:
        log.exception("Exception trying to get circuit string %s", e)
        return '[unknown]'
    return '[' +\
        ' -> '.join(['{} ({})'.format(n, fp[0:8]) for fp, n in circ.path]) +\
        ']'


def get_controller(args):
    if not args.ctrl_port and not args.ctrl_socket:
        log.error('Need control port or control socket')
        exit(1)
    c = None
    if args.ctrl_port:
        c = Controller.from_port(port=args.ctrl_port)
    elif args.ctrl_socket:
        c = Controller.from_socket_file(path=args.ctrl_socket)
    c.authenticate()
    c.set_conf('__LeaveStreamsUnattached', '1')
    log.debug('We are%s connected to Tor',
              '' if c.is_authenticated() else ' not')
    return c


def main(args):
    circuits = parse_circuit_list_fd(open(args.circuit_list, 'rt'))
    if not len(circuits):
        log.error('Didn\'t read any circuits from %s', args.circuit_list)
        exit(1)
    cont = get_controller(args)
    cont.add_event_listener(
        lambda ev: close_circ_for_closing_stream(cont, ev), EventType.STREAM)
    cont.add_event_listener(add_new_stream_to_queue, EventType.STREAM)
    circuit_iter = loop_iter_forever(circuits)
    while True:
        stream_event = stream_queue.get()
        circ_path = next(circuit_iter)
        circ_id = cont.new_circuit(circ_path, await_build=True)
        cont.attach_stream(stream_event.id, circ_id)
        log.info(
            'Connecting stream %s %s to circuit: %s',
            stream_event.id,
            stream_event.target,
            circuit_str(cont, circ_id))


if __name__ == '__main__':
    parser = ArgumentParser(
        formatter_class=ArgumentDefaultsHelpFormatter,
        description='Connect to a Tor client, wait for programs to ask it '
        'to connect somewhere, and tell Tor how to build a circuit for that '
        'connection. Reads a file for a list of circuits we should build, '
        'one per line, and we loop over it in order forever. Each circuit '
        'must have at least 2 relays in it (and up to 8?). The relays must '
        'be identified by fingerprint and seperated by spaces.')
    parser.add_argument(
        '--circuit-list', type=str, default='circuits.txt',
        help='List of circuits, one per line')
    parser.add_argument(
        '-s', '--ctrl-socket', type=str, help='Path to a Tor ControlSocket. If '
        'both this and --ctrl-port are given, this wins')
    parser.add_argument(
        '-p', '--ctrl-port', type=str, help='A Tor ControlPort')
    args = parser.parse_args()
    args.circuit_list = os.path.abspath(args.circuit_list)
    try:
        main(args)
    except KeyboardInterrupt:
        print()
