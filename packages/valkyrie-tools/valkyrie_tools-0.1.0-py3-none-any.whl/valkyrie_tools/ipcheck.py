# src/valkyrie/ipcheck.py

from typing import Dict, List

import click
import requests

__title__ = "Get Info on an IP Address"
__version__ = "0.1.0"

API_URL = "https://ipinfo.io/{ipaddr}/json"


def get_ip_info(ip: str) -> Dict:
    """Pull IP information from ipinfo.io API.

    Args:
        ip (str): The IP address to look up.

    Returns:
        dict: A dictionary containing IP information.
    """
    with requests.get(API_URL.format(ipaddr=ip), timeout=10) as r:
        r.raise_for_status()
        data = r.json()
        return data


@click.command()
@click.version_option(version=__version__)
@click.argument("ipaddr", type=str, nargs=-1)
def main(ipaddr: List[str]) -> None:
    """Get information on an IP address.

    Args:
        ipaddr (List[str]): A list of IP addresses to look up.

    Raises:
        click.ClickException: Raised if no arguments are provided.
        click.ClickException: Raised if an error occurs while making the request.
    """
    if len(ipaddr) == 0:
        raise click.ClickException("no arguments provided")

    for ip in ipaddr:
        try:
            data = get_ip_info(ip)
            click.secho("> %s" % ip)

            for key, value in data.items():
                click.secho("   %s: " % key, nl=False)
                click.secho("%s" % value, fg="green")

        except requests.RequestException as e:
            raise click.ClickException from e
