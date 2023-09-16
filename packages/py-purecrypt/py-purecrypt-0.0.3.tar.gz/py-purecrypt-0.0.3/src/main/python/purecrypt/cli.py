import argparse

from . import Crypt, Method


def method(arg):
    try:
        return Method.value_of(arg)
    except ValueError as err:
        raise argparse.ArgumentTypeError(str(err)) from None


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--method", type=method, default=Method.SHA512, help="method of encryption (MD5, SHA256, SHA512)")
    parser.add_argument("-r", "--rounds", type=int, help="number of rounds (SHA256 and SHA512 only)")
    parser.add_argument("-s", "--salt", type=str, help="salt to use")
    parser.add_argument("password", type=str, help="password to encrypt")
    return parser.parse_args()


def main():
    args = parse_args()
    if not args.salt:
        salt = Crypt.generate_salt(args.method, rounds=args.rounds)
        print(Crypt.encrypt(args.password, salt))
    else:
        print(Crypt.encrypt(args.password, args.salt))
