#!/usr/bin/env python3
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
import os, http.server

def main(args):
    os.chdir(args.directory)
    addr = ('' ,args.port)
    httpd = http.server.HTTPServer(addr, http.server.SimpleHTTPRequestHandler)
    httpd.serve_forever()

if __name__ == '__main__':
    parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument('-p', '--port', default=8000,
            help='Port on which to listen')
    parser.add_argument('-d', '--directory', metavar='DIR', default=os.getcwd(),
            help='Directory to serve')
    args = parser.parse_args()
    try: exit(main(args))
    except KeyboardInterrupt as e: pass
