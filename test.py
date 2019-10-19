from argparse import ArgumentParser
import sys



parser = ArgumentParser()

subparsers = parser.add_subparsers(help='sub-command help', dest='action')


parser_a = subparsers.add_parser('hydra', help='a help')

sub_parser_a = parser_a.add_subparsers()

sub_a = sub_parser_a.add_parser('deploy')

sub_a.add_argument('repo')




parser_b = subparsers.add_parser('provisioner', help='b help')

sub_b = parser_b.add_subparsers(help='testing a sub of b')

sub_b_parser = sub_b.add_parser('plan')

sub_b_parser.add_argument('nickname')

args = parser.parse_args()






