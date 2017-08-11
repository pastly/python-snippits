#!/usr/bin/env python3
from argparse import ArgumentDefaultsHelpFormatter, ArgumentParser
import time
from stem.control import Controller
from curses import wrapper
from datetime import datetime

def myprint(s, *words):
    s.addstr(' '.join([str(w) for w in words])+'\n')

def print_stats(scr, cont):
    all_circs = []
    all_streams = cont.get_streams()
    for circ in cont.get_circuits():
        path = [ nick for fp, nick in circ.path ]
        streams = [ s for s in all_streams if s.circ_id == circ.id ]
        all_circs.append({'id': int(circ.id),
            'path': path,
            'used': True if len(streams) else False,
            'targets': [ s.target for s in streams ],
            })
    all_circs = sorted(all_circs, key=lambda c: c['id'])
    for circ in all_circs:
        s = '*' if circ['used'] else ' '
        s += ' {} {}'.format(circ['id'], ' '.join(circ['path']))
        if circ['used']: s += ' (' + ','.join(circ['targets']) + ')'
        myprint(scr, s)
    myprint(scr, len(all_streams),'streams; {}/{} circuits in use'.format(
            len([c for c in all_circs if c['used'] ]), len(all_circs)))

def main(stdscr, args):
    stdscr.clear()
    with Controller.from_port(port=args.ctrl_port) as cont:
        cont.authenticate()
        assert cont.is_authenticated()
        while True:
            stdscr.erase()
            print_stats(stdscr, cont)
            stdscr.refresh()
            time.sleep(args.interval)

def pre_main():
    parser = ArgumentParser(
            formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument('-p', '--ctrl-port', metavar='PORT', type=int,
            help='Port on which to control the tor client', default=9051)
    parser.add_argument('-i', '--interval', metavar='SECS', type=float,
            help='How often to update screen', default=1.0)
    args = parser.parse_args()
    return wrapper(main,args)

if __name__=='__main__':
    try: exit(pre_main())
    except KeyboardInterrupt: pass
