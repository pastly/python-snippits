#!/usr/bin/env python3
from argparse import ArgumentDefaultsHelpFormatter, ArgumentParser
import logging
from stem.control import Controller


logging.basicConfig(format='%(asctime)s %(levelname)s %(threadName)s '
                    '%(filename)s:%(lineno)s - %(funcName)s - %(message)s',
                    level=logging.DEBUG)
log = logging.getLogger(__name__)


def main(args):
    cont = get_controller(args)
    if not have_geoip(cont):
        log.error('Do not appear to have geoip information. Cannot continue')
        return 1
    # To store fingerprint -> [country codes] mappings for each relay
    cc_map = {}
    # To store fingerprint -> consensus weight mappings for each relay
    bw_map = {}
    # To store fingerprint -> [Flags] mappings for each relay
    flags_map = {}
    # Fetch info from Tor
    for ns in cont.get_network_statuses():
        bw_map[ns.fingerprint] = ns.bandwidth
        flags_map[ns.fingerprint] = ns.flags
        geo = geoip_lookup(cont, ns.address)
        # relays have more than 1 IP address. There's the main one, and then 0
        # or more additional ones. Get the country code for all of them.
        cc_map[ns.fingerprint] = {geo}
        for addr, port, is_ipv6 in ns.or_addresses:
            geo = geoip_lookup(cont, addr)
            cc_map[ns.fingerprint].add(geo)
    # cc_map but for just guards and just exits
    guards = {fp: cc_map[fp] for fp in cc_map if 'Guard' in flags_map[fp]}
    exits = {fp: cc_map[fp] for fp in cc_map if 'Exit' in flags_map[fp]}
    log.info(f'Found {len(cc_map)} relays. {len(guards)} guards and '
             f'{len(exits)} exits.')
    # cc_map for relays in 1+ countries, zero countries, and for relays that
    # are in 1+ bad countries
    many_countries = {fp: cc_map[fp] for fp in cc_map if len(cc_map[fp]) > 1}
    zero_countries = {fp: cc_map[fp] for fp in cc_map if len(cc_map[fp]) < 1}
    bad_countries = {fp: cc_map[fp] for fp in cc_map if
                     len([_ for _ in filter(
                         lambda cc: cc in args.exclude_nodes,
                         cc_map[fp])]) > 0}
    log.info(f'{len(many_countries)} relays in >1 country')
    log.info(f'{len(zero_countries)} relays in 0 countries')
    log.info(
        f'{len(bad_countries)}/{len(cc_map)} '
        f'({len(bad_countries)/len(cc_map)*100:.2f}%) '
        'relays in bad countries')
    # cc_map for bad guards and bad exits
    bad_guards = {fp: cc_map[fp] for fp in guards if fp in bad_countries}
    bad_exits = {fp: cc_map[fp] for fp in exits if fp in bad_countries}
    log.info(
        f'{len(bad_guards)}/{len(guards)} '
        f'({len(bad_guards)/len(guards)*100:.2f}%) '
        f'guards in bad countries')
    log.info(
        f'{len(bad_exits)}/{len(exits)} '
        f'({len(bad_exits)/len(exits)*100:.2f}%) '
        f'exits in bad countries')
    # consensus weight for specific subsets of the network
    total_bw = sum([bw_map[fp] for fp in bw_map])
    bad_bw = sum([bw_map[fp] for fp in bad_countries])
    guard_bw = sum([bw_map[fp] for fp in guards])
    exit_bw = sum([bw_map[fp] for fp in exits])
    bad_guard_bw = sum([bw_map[fp] for fp in bad_guards])
    bad_exit_bw = sum([bw_map[fp] for fp in bad_exits])
    log.info(
        f'{bad_bw/total_bw*100:.2f}% '
        f'of relays by bandwidth in bad countries')
    log.info(
        f'{bad_guard_bw/guard_bw*100:.2f}% '
        f'of guards by bandwidth in bad countries')
    log.info(
        f'{bad_exit_bw/exit_bw*100:.2f}% '
        f'of exits by bandwidth in bad countries')


def have_geoip(controller):
    return controller.get_info('ip-to-country/ipv4-available', 0) == '1'


def geoip_lookup(controller, ip):
    return controller.get_info(f'ip-to-country/{ip}')


def get_controller(args):
    if not args.ctrl_port and not args.ctrl_socket:
        log.error('Need control port or control socket')
        exit(1)
    c = None
    if args.ctrl_socket:
        c = Controller.from_socket_file(path=args.ctrl_socket)
    elif args.ctrl_port:
        c = Controller.from_port(port=args.ctrl_port)
    c.authenticate()
    log.debug('We are%s connected to Tor',
              '' if c.is_authenticated() else ' not')
    return c


def parse_cc(s):
    if s is None:
        return []
    ccs = s.lower().replace('{', '').replace('}', '').split(',')
    return ccs


if __name__ == '__main__':
    parser = ArgumentParser(
        formatter_class=ArgumentDefaultsHelpFormatter,
        description='Connect to a Tor client and get consensus data '
        'from it. Calculate various statistics about relay locations '
        'and their relation to the given list of countries to '
        'hypothetically exclude.')
    parser.add_argument(
        '--circuit-list', type=str, default='circuits.txt',
        help='List of circuits, one per line')
    parser.add_argument(
        '-s', '--ctrl-socket', type=str, help='Path to a Tor ControlSocket. '
        'If both this and --ctrl-port are given, this wins')
    parser.add_argument(
        '-p', '--ctrl-port', type=int, help='A Tor ControlPort')
    parser.add_argument(
        '--exclude-nodes', type=str, help='Comma-separated list of two-letter '
        'country codes. '
        'For example, to exclude the US and Canada: us,ca')
    args = parser.parse_args()
    args.exclude_nodes = parse_cc(args.exclude_nodes)
    try:
        exit(main(args))
    except KeyboardInterrupt:
        print()
