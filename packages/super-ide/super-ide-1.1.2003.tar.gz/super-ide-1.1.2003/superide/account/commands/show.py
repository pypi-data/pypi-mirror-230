# Copyright (c) Mengning Software. 2023. All rights reserved.
#
# Super IDE licensed under GNU Affero General Public License v3 (AGPL-3.0) .
# You can use this software according to the terms and conditions of the AGPL-3.0.
# You may obtain a copy of AGPL-3.0 at:
#
#    https://www.gnu.org/licenses/agpl-3.0.txt
#
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY OR FIT FOR A PARTICULAR
# PURPOSE.
# See the AGPL-3.0 for more details.

import json

import click
from tabulate import tabulate

from superide import util
from superide.account.client import AccountClient


@click.command("show", short_help="superide Account information")
@click.option("--offline", is_flag=True)
@click.option("--json-output", is_flag=True)
def account_show_cmd(offline, json_output):
    client = AccountClient()
    info = client.get_account_info(offline)
    if json_output:
        click.echo(json.dumps(info))
        return
    click.echo()
    if info.get("profile"):
        print_profile(info["profile"])
    if info.get("packages"):
        print_packages(info["packages"])
    if info.get("subscriptions"):
        print_subscriptions(info["subscriptions"])
    click.echo()


def print_profile(profile):
    click.secho("Profile", fg="cyan", bold=True)
    click.echo("=" * len("Profile"))
    data = []
    if profile.get("username"):
        data.append(("Username:", profile["username"]))
    if profile.get("email"):
        data.append(("Email:", profile["email"]))
    if profile.get("firstname"):
        data.append(("First name:", profile["firstname"]))
    if profile.get("lastname"):
        data.append(("Last name:", profile["lastname"]))
    click.echo(tabulate(data, tablefmt="plain"))


def print_packages(packages):
    click.echo()
    click.secho("Packages", fg="cyan")
    click.echo("=" * len("Packages"))
    for package in packages:
        click.echo()
        click.secho(package.get("name"), bold=True)
        click.echo("-" * len(package.get("name")))
        if package.get("description"):
            click.echo(package.get("description"))
        data = []
        expire = "-"
        if "subscription" in package:
            expire = util.parse_datetime(
                package["subscription"].get("end_at")
                or package["subscription"].get("next_bill_at")
            ).strftime("%Y-%m-%d")
        data.append(("Expire:", expire))
        services = []
        for key in package:
            if not key.startswith("service."):
                continue
            if isinstance(package[key], dict):
                services.append(package[key].get("title"))
            else:
                services.append(package[key])
        if services:
            data.append(("Services:", ", ".join(services)))
        click.echo(tabulate(data, tablefmt="plain"))


def print_subscriptions(subscriptions):
    click.echo()
    click.secho("Subscriptions", fg="cyan")
    click.echo("=" * len("Subscriptions"))
    for subscription in subscriptions:
        click.echo()
        click.secho(subscription.get("product_name"), bold=True)
        click.echo("-" * len(subscription.get("product_name")))
        data = [("State:", subscription.get("status"))]
        begin_at = util.parse_datetime(subscription.get("begin_at")).strftime("%c")
        data.append(("Start date:", begin_at or "-"))
        end_at = subscription.get("end_at")
        if end_at:
            end_at = util.parse_datetime(subscription.get("end_at")).strftime("%c")
        data.append(("End date:", end_at or "-"))
        next_bill_at = subscription.get("next_bill_at")
        if next_bill_at:
            next_bill_at = util.parse_datetime(
                subscription.get("next_bill_at")
            ).strftime("%c")
        data.append(("Next payment:", next_bill_at or "-"))
        data.append(
            ("Edit:", click.style(subscription.get("update_url"), fg="blue") or "-")
        )
        data.append(
            ("Cancel:", click.style(subscription.get("cancel_url"), fg="blue") or "-")
        )
        click.echo(tabulate(data, tablefmt="plain"))
