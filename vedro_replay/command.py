import argparse

from .generator import MainGenerator, generate


def command() -> None:
    parser = argparse.ArgumentParser(description='vedro-replay commands')
    subparsers = parser.add_subparsers(help='List of available commands', required=True)

    generate_parser = subparsers.add_parser('generate', help='Generate vedro-replay tests')
    generate_parser.add_argument(
        'option',  default='all', nargs='?', choices=MainGenerator.generation_options(), help='Generation option',
    )
    generate_parser.add_argument(
        '--requests-dir', help='The path to the directory containing the request files', default='requests'
    )
    generate_parser.add_argument(
        '--force', help='Forced regeneration. The files will be overwritten', action='store_true'
    )
    generate_parser.set_defaults(func=generate)

    args = parser.parse_args()
    args.func(args)
