#!/usr/bin/env python3
import base64
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


def main():
    priv_key = nacl.public.PrivateKey.generate()
    pub_key = priv_key.public_key
    print('public:  %s' % key_str(pub_key))
    print('private: %s' % key_str(priv_key))


if __name__ == '__main__':
    exit(main())
