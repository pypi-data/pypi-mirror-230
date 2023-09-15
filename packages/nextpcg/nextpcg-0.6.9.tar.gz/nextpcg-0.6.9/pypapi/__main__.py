# -*- coding: utf-8 -*-
"""command line tool
Author  : NextPCG
"""
import argparse
import os
import yaml
import shutil
from importlib_resources import files, as_file


def entry():
    parser = argparse.ArgumentParser(prog = 'nextpcg')
    subparsers = parser.add_subparsers(
        title='These are common NextPCG Dson commands used in various situations',
        metavar='command'
    )

    init_parser = subparsers.add_parser(
        'init',
        help='Init a nextpcg python plugin environment'
    )
    init_parser.add_argument(
        'path',
        help='the path to plugin directory(optional, default is current directory)',
        nargs='?',
        default='.'
    )
    init_parser.add_argument('--name', help='the plugin name')
    init_parser.add_argument('--conda_env', help='conda env name')
    init_parser.set_defaults(handle=handle_init)

    # run parser
    args = parser.parse_args()
    if hasattr(args, 'handle'):
        args.handle(args)
    else:
        parser.print_help()


def handle_init(args):
    try:
        plugin_path = os.path.abspath(args.path)
    except Exception as e:
        print('path is no valid')
        print(e)

    dson_text = files('pypapi').joinpath('pantry').joinpath('dson_config.yaml').read_text()
    dson_config = yaml.full_load(dson_text)
    # deal with optional arg(name and conda_env)
    if hasattr(args, 'name'):
        dson_config['name'] = args.name
    if hasattr(args, 'conda_env'):
        dson_config['conda_env'] = args.conda_env
    
    with open(os.path.join(plugin_path, 'dson_config.yaml'), 'w', encoding='utf-8') as f:
        yaml.safe_dump(dson_config, f, sort_keys=False)
        f.close()
    
    source = files('pypapi').joinpath('pantry').joinpath('dson_generator.py')
    with as_file(source) as source_path:
        shutil.copyfile(source_path,os.path.join(plugin_path, 'dson_generator.py'))
    

if __name__ == '__main__':
    entry()