"""Utility functions for config2py."""

import re
import os
from pathlib import Path
from functools import partial
from typing import Optional, Union, Any, Callable
from dol import TextFiles
import getpass

pkg_name = 'config2py'
DFLT_MASKING_INPUT = False


def always_true(x: Any) -> bool:
    """Function that just returns True."""
    return True


def identity(x: Any) -> Any:
    """Function that just returns its argument."""
    return x


# TODO: Make this into an open-closed mini-framework
def ask_user_for_input(
    prompt: str,
    default: str = None,
    *,
    mask_input=DFLT_MASKING_INPUT,
    masking_toggle_str: str = None,
    egress: Callable = identity,
) -> str:
    """
    Ask the user for input, optionally masking, validating and transforming the input.

    :param prompt: Prompt to display to the user
    :param default: Default value to return if the user enters nothing
    :param mask_input: Whether to mask the user's input
    :param masking_toggle_str: String to toggle input masking. If ``None``, no toggle
        is available. If not ``None`` (a common choice is the empty string)
        the user can enter this string to toggle input masking.
    :param egress: Function to apply to the user's response before returning it.
        This can be used to validate the response, for example.
    :return: The user's response (or the default value if the user entered nothing)
    """
    _original_prompt = prompt
    if prompt[-1] != ' ':  # pragma: no cover
        prompt = prompt + ' '
    if masking_toggle_str is not None:
        prompt = (
            f'{prompt}\n'
            f"    (Input masking is {'ENABLED' if mask_input else 'DISABLED'}. "
            f"Enter '{masking_toggle_str}' (without quotes) to toggle input masking)\n"
        )
    if default:
        prompt = prompt + f' [{default}]: '
    if mask_input:
        response = getpass.getpass(prompt)
    else:
        response = input(prompt)
    if masking_toggle_str is not None and response == masking_toggle_str:
        return ask_user_for_input(
            _original_prompt,
            default,
            mask_input=not mask_input,
            masking_toggle_str=masking_toggle_str,
        )

    return egress(response or default)


# Note: Could be made more efficient, but this is good enough (for now)
def extract_variable_declarations(
    string: str, expand: Optional[Union[dict, bool]] = None
) -> dict:
    """
    Reads the contents of a config file, extracting Unix-style environment variable
    declarations of the form
    `export {NAME}={value}`, returning a dictionary of `{NAME: value, ...}` pairs.

    See issue for more info and applications:
    https://github.com/i2mint/config2py/issues/2

    :param string: String to extract variable declarations from
    :param expand: An optional dictionary of variable names and values to use to
        expand variables that are referenced (i.e. ``$NAME`` is a reference to ``NAME``
        variable) in the values of config variables.
        If ``True``, ``expand`` is replaced with an empty dictionary, which means we
        want to expand variables recursively, but we have no references to seed the
        expansion with. If ``False``, ``expand`` is replaced with ``None``, indicating
        that we don't want to expand any variables.

    :return: A dictionary of variable names and values.

    >>> config = 'export ENVIRONMENT="dev"\\nexport PORT=8080\\nexport DEBUG=true'
    >>> extract_variable_declarations(config)
    {'ENVIRONMENT': 'dev', 'PORT': '8080', 'DEBUG': 'true'}

    >>> config = 'export PATH="$PATH:/usr/local/bin"\\nexport EDITOR="nano"'
    >>> extract_variable_declarations(config)
    {'PATH': '$PATH:/usr/local/bin', 'EDITOR': 'nano'}

    The ``expand`` argument can be used to expand variables in the values of other.

    Let's add a reference to the ``PATH`` variable in the ``EDITOR`` variable:

    >>> config = 'export PATH="$PATH:/usr/local/bin"\\nexport EDITOR="nano $PATH"'

    If you specify a value for ``PATH`` in the ``expand`` argument, you'll see it
    reflected in the ``PATH`` variable (self reference) and the ``EDITOR`` variable.
    (Note if you changed the order of ``PATH`` and ``EDITOR`` in the ``config``,
    you wouldn't get the same thing though.)

    >>> extract_variable_declarations(config, expand={'PATH': '/root'})
    {'PATH': '/root:/usr/local/bin', 'EDITOR': 'nano /root:/usr/local/bin'}

    If you specify ``expand={}``, the first ``PATH`` variable will not be expanded,
    since PATH is not in the expand dictionary. But the second ``PATH`` variable,
    referenced in the definition of ``EDITOR`` will be expanded, since it is in the
    expand dictionary.

    >>> extract_variable_declarations(config, expand={})
    {'PATH': '$PATH:/usr/local/bin', 'EDITOR': 'nano $PATH:/usr/local/bin'}

    """
    if expand is True:
        # If expand is True, we'll use an empty dictionary as the expand dictionary
        # This means we want variables to be expanded recursively, but we have no
        # references to seed the expansion with.
        expand = {}
    elif expand is False:
        # If expand is False, we don't want to expand any variables.
        expand = None

    env_vars = {}
    pattern = re.compile(r'^export\s+([A-Za-z0-9_]+)=(.*)$')
    lines = string.split('\n')
    for line in lines:
        line = line.strip()
        match = pattern.match(line)
        if match:
            name = match.group(1)
            value = match.group(2).strip('"')
            if expand is not None:
                for key, val in expand.items():
                    value = value.replace(f'${key}', val)
                env_vars[name] = value
                expand = dict(expand, **env_vars)
            else:
                env_vars[name] = value
    return env_vars


# Note: First possible i2 dependency -- vendoring for now
def get_app_data_folder(ensure_exists=False):
    """
    Returns the full path of a directory suitable for storing application-specific data.

    On Windows, this is typically %APPDATA%.
    On macOS, this is typically ~/.config.
    On Linux, this is typically ~/.config.

    Returns:
        str: The full path of the app data folder.

    See https://github.com/i2mint/i2mint/issues/1.

    For a more complete implementation, see:
    """
    if os.name == 'nt':
        # Windows
        app_data_folder = os.getenv('APPDATA')
    else:
        # macOS and Linux/Unix
        app_data_folder = os.path.expanduser('~/.config')

    if ensure_exists and not os.path.isdir(app_data_folder):
        os.mkdir(app_data_folder)
    return app_data_folder


def _get_app_data_dir(dirname=pkg_name):
    """Get the app data directory."""
    app_data_dir = os.path.join(get_app_data_folder(ensure_exists=True), dirname)
    if not os.path.isdir(app_data_dir):
        os.mkdir(app_data_dir)
        # Add a hidden file that annotates the directory as one managed by config2py,
        # so that we at least have a chance of distinguishing it from a directory of
        # the same name that another program might create (we don't want to write in
        # someone else's directory!).
        (Path(app_data_dir) / '.config2py').write_text('I was created by config2py.')
    return app_data_dir


# TODO: Build Configs from dol.Files, returning dol.TextFiles except if .bin extension,
#  and returning Configs(dirpath) if key is a directory
# TODO: Make the Configs class with use outside config2py in mind.
Configs = TextFiles


def get_configs_local_store(dirname=pkg_name):
    """Get the local store of configs."""
    return Configs(_get_app_data_dir(dirname))


configs = get_configs_local_store()


# def extract_variable_declarations(string):
#     """
#     Reads the contents of a config file, extracting Unix-style environment variable
#     declarations of the form
#     `export {NAME}={value}`, returning a dictionary of `{NAME: value, ...}` pairs.
#
#     # >>> config = (
#     # ...   'export ENVIRONMENT="development"\\n'
#     # ...   'export PORT=8080\\n'
#     # ...   'alias = "just to make it harder"\\n'
#     # ...   '\\n'
#     # ...   'export DEBUG=true'
#     # ...)
#     # >>> extract_variable_declarations(config)
#     # {'ENVIRONMENT': '"development"', 'PORT': '8080', 'DEBUG': 'true'}
#
#     >>> config = 'export PATH="$PATH:/usr/local/bin"\\nexport EDITOR="nano"'
#     >>> extract_variable_declarations(config)
#     {'PATH': '$PATH:/usr/local/bin', 'EDITOR': 'nano'}
#
#     """
#     env_vars = {}
#     lines = string.split("\n")
#     for line in lines:
#         line = line.strip()
#         if line.startswith("export"):
#             parts = line.split("=")
#             name = parts[0].split(" ")[1]
#             value = parts[1]
#             env_vars[name] = value
#     return env_vars
