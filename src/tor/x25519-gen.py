#!/usr/bin/env python3
import base64
import os
import sys
try:
    import nacl.public
except ImportError:
    print('PyNaCl is required: "pip install pynacl" or similar')
    exit(1)


def key_str(key):
    # bytes to base 32
    key_bytes = bytes(key)
    key_b32 = base64.b32encode(key_bytes)
    # strip trailing ====
    assert key_b32[-4:] == b'===='
    key_b32 = key_b32[:-4]
    # change from b'ASDF' to ASDF
    s = key_b32.decode('utf-8')
    return s


def main(*args):
    priv_key = nacl.public.PrivateKey.generate()
    pub_key = priv_key.public_key
    if len(args) > 0:
        name = args[0]
        if os.path.exists("../hostname"):
            hostname = open("../hostname").read().strip().removesuffix(".onion")
        else:
            hostname = "your-onion-address-here-without-dot-onion-suffix"
        print('%s:descriptor:x25519:%s' % (hostname, key_str(priv_key)), file=open("%s.auth_private" % name, "w+"))
        os.chmod("%s.auth_private" % name, 0o600)
        print('descriptor:x25519:%s' % key_str(pub_key), file=open("%s.auth" % name, "w+"))
    else:
        print('public:  %s' % key_str(pub_key))
        print('private: %s' % key_str(priv_key))


if __name__ == '__main__':
    exit(main(*sys.argv[1:]))
