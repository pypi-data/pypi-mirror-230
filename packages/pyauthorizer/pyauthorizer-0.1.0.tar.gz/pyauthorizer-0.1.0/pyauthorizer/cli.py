import json
import sys
from dataclasses import asdict
from json.decoder import JSONDecodeError

import click

from pyauthorizer.encryptor import interface
from pyauthorizer.encryptor.base import License, LicenseStatus


def convert_user_args_to_dict(user_list):
    """
    Converts a list of user arguments to a dictionary.

    Args:
        user_list (list): A list of user arguments.

    Returns:
        dict: A dictionary containing the converted user arguments. The keys are the names extracted from the user arguments, and the values are the corresponding values.

    Raises:
        click.BadOptionUsage: If the user arguments are not in the correct format.
        click.ClickException: If a parameter is repeated in the user arguments.
    """
    user_dict = {}
    for s in user_list:
        try:
            # Some configs may contain '=' in the value
            name, value = s.split("=", 1)
        except ValueError as exc:
            # not enough values to unpack
            msg = "config"
            raise click.BadOptionUsage(
                msg,
                "Config options must be a pair and should be "
                "provided as ``-C key=value`` or "
                "``--config key=value``",
            ) from exc
        if name in user_dict:
            msg = f"Repeated parameter: '{name}'"
            raise click.ClickException(msg)
        user_dict[name] = value
    return user_dict


# load all registered encryptors
installed_flavors = list(interface.plugin_store.registry)
if len(installed_flavors) > 0:
    supported_flavors_msg = "Support is currently installed for encryptor to: {flavors}".format(
        flavors=", ".join(installed_flavors)
    )
else:
    supported_flavors_msg = "NOTE: you currently do not have support installed for any encryptor flavors."


# cmd options
parse_output = click.option(
    "--output-path",
    "-O",
    help="File to output results to as a JSON file. If not provided, prints output to stdout.",
)
parse_input = click.option("--input-path", "-I", required=True, help="Path to input json file for prediction")
parse_custom_arguments = click.option(
    "--config",
    "-C",
    metavar="NAME=VALUE",
    multiple=True,
    help="Extra target-specific config for the model "
    "encryptor, of the form -C name=value. See "
    "documentation/help for your encryptor target for a "
    "list of supported config options.",
)
encryptor_flavor = click.option(
    "--flavor",
    "-f",
    required=True,
    help="Which flavor to be used to encrypt. This will be auto inferred if it's not given",
)


@click.group(
    "encrpytor",
    help=f"""
    Using encrpytor to manage license.Run `pyauthorizer --help` for
    more details on the supported URI format and config options for a given target.
    {supported_flavors_msg}

    See all supported encryption targets and installation instructions in
    https://github.com/msclock/pyauthorizer/tree/master/pyauthorizer/encrpytor/builtin

    You can also write your own plugin for encryptor to a custom target. For instructions on
    writing and distributing a plugin, related docs are coming soon.""",
)
def commands():
    """
    Provide commands to manage license for py project.
    """


@commands.command("create")
@parse_output
@parse_custom_arguments
@encryptor_flavor
def generate_license(flavor, config, output_path):
    """
    Generate a license using the given flavor and configuration, and either write it to a file or print it to the console.
    """
    config_dict = convert_user_args_to_dict(config)
    encryptor = interface.get_encryptor(flavor)
    license = encryptor.generate_license(config_dict)

    json_license = json.dumps(
        asdict(license),
        indent=4,
        ensure_ascii=False,
        sort_keys=False,
        separators=(",", ":"),
    )
    if output_path is not None:
        with open(output_path, "w") as f:
            f.write(json_license)
    else:
        click.echo(json_license)


@commands.command("validate")
@parse_input
@parse_custom_arguments
@encryptor_flavor
def validate_license(flavor, config, input_path):
    """
    Validates a license using the specified flavor.
    """
    config_dict = convert_user_args_to_dict(config)
    encryptor = interface.get_encryptor(flavor)

    data = {}
    try:
        with open(input_path) as f:
            data = json.load(f)
        license = License(**data)
    except (TypeError, FileNotFoundError, JSONDecodeError) as err:
        if isinstance(err, FileNotFoundError):
            err_msg = f"open license.json: {err.args}"
        elif isinstance(err, JSONDecodeError):
            err_msg = f"invalid license.json: {err.args}"
        else:
            err_msg = err.args
        click.echo(f"Init License failed with {err_msg}")
        sys.exit(2)

    status = encryptor.validate_license(license, config_dict)
    if status == LicenseStatus.ACTIVE:
        click.echo("License is active")
    elif status == LicenseStatus.EXPIRED:
        click.echo("License has expired")
    else:
        click.echo("License is invalid")


if __name__ == "__main__":
    commands()
