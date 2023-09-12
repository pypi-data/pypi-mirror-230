import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--foo', nargs='+', default=[])
parser.add_argument('--bar', action='append', nargs=2, default=[])
args = parser.parse_args()

print(args)
