#!/usr/bin/env python
# encoding: utf-8
import click
import os
import sys
from .model_download import download_model_from_mirror

__version__ = "0.1"
pgk_dir = os.path.join(os.path.dirname(os.path.abspath('__file__')))


# 主组命令 CSP
# 在setup的entry_points字段中指定
@click.group(context_settings={'help_option_names': ['-h', '--help']}, invoke_without_command=True)
@click.version_option('{0} from {1} (Python {2})'.format(__version__, pgk_dir, sys.version[:3]))
def llmcli():
    """
    LLM Command line tools
    """ 
 
@llmcli.command()
@click.option("-i","--repo_id", type=click.STRING, required=True, default=None)
@click.option("-t","--repo_type", type=click.STRING, default="model", required=True) 
def download(repo_id,repo_type):
    """
    Command on model download
    """
    print("download the model: {}".format(repo_id))
    download_model_from_mirror(repo_id, repo_type)

if __name__ == '__main__':
    llmcli()



