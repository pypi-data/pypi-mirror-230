import os
import json
import csv
import logging

import click
import yaml

from .base import IpaService


logger = logging.getLogger(__name__)

@click.group()
@click.option("-h", "--host", default="127.0.0.1", help=u"Server address, default to 127.0.0.1.")
@click.option("-p", "--port", default=389, type=int, help=u"Server port, default 389.")
@click.option("-u", "--username", help=u"Usesname to binding. Different user may have different field permissions. If no username provides, bind with anonymous user.")
@click.option("-P", "--password", help=u"Password for the user.")
@click.option("-b", "--base-dn", help=u"BaseDN of the ldap server. If no BaseDN provides, try to search it automatically.")
@click.pass_context
def ipa(ctx, host, port, username, password, base_dn):
    u"""Freeipa command line utils. Use sub-command to do real work.
    """
    ctx.ensure_object(dict)
    ctx.obj["host"] = host
    ctx.obj["port"] = port
    ctx.obj["username"] = username
    ctx.obj["password"] = password
    ctx.obj["base_dn"] = base_dn


@ipa.command(name="get-user-detail")
@click.option("-o", "--output-format", default="yaml", type=click.Choice(['yaml', 'json']), help=u"Output format, default to yaml.")
@click.argument("username", nargs=1, required=True)
@click.pass_context
def get_user_detail(ctx, output_format, username):
    u"""Get user entry information.
    """
    service = IpaService(ctx.obj["host"], ctx.obj["port"], ctx.obj["base_dn"], ctx.obj["username"], ctx.obj["password"])
    user = service.get_user_detail(username)
    if not user:
        click.echo(u"Error: username [{username}] not found.".format(username=username))
        os.sys.exit(1)
    else:
        if output_format.lower() == u"json":
            click.echo(json.dumps(user, ensure_ascii=False))
        else:
            click.echo(yaml.safe_dump(user, allow_unicode=True))


@ipa.command(name="get-users")
@click.option("-o", "--output", default="users.csv")
@click.option("-e", "--encoding", default="gb18030")
@click.pass_context
def get_users(ctx, output, encoding):
    u"""Export all users to a csv file.
    """
    service = IpaService(ctx.obj["host"], ctx.obj["port"], ctx.obj["base_dn"], ctx.obj["username"], ctx.obj["password"])
    user_entries = service.get_user_entries()
    if not user_entries:
        print("no user entry found...")
        os.sys.exit(1)
    users = [service.get_user_detail_from_entry(user) for user in user_entries]
    user = users[0]
    headers = list(user.keys())
    headers.sort()
    rows = []
    for user in users:
        row = []
        for field in headers:
            row.append(user.get(field, None))
        rows.append(row)
    with open(output, "w", encoding=encoding, newline="") as fobj:
        f_csv = csv.writer(fobj)
        f_csv.writerow(headers)
        f_csv.writerows(rows)


@ipa.command(name="add-user")
@click.option("-a", "--attribute", multiple=True)
@click.argument("username", nargs=1, required=True)
@click.pass_context
def add_user(ctx, username, attribute):
    u"""Create a new user entry.
    """
    attributes = attribute
    print("USERNAME:", username)
    print("ATTRIBUTES:", attributes)
    service = IpaService(ctx.obj["host"], ctx.obj["port"], ctx.obj["base_dn"], ctx.obj["username"], ctx.obj["password"])
    user_detail = {}
    for attribute in attributes:
        key, value = [x.strip() for x in attribute.split("=")]
        user_detail[key] = value
    try:
        result = service.add_user_entry(username, user_detail)
        print("Add user success!")
        print("New user info:")
        user = service.get_user_detail(username)
        print(json.dumps(user, ensure_ascii=False))
    except Exception as error:
        print("Add user failed!!!")
        print("Error info:")
        print(str(error))


@ipa.command(name="update-user")
@click.option("-a", "--attribute", multiple=True)
@click.argument("username", nargs=1, required=True)
@click.pass_context
def update_user(ctx, username, attribute):
    u"""Update user attributes.
    """
    attributes = attribute
    print("USERNAME:", username)
    print("ATTRIBUTES:", attributes)
    service = IpaService(ctx.obj["host"], ctx.obj["port"], ctx.obj["base_dn"], ctx.obj["username"], ctx.obj["password"])
    user_changes = {}
    for attribute in attributes:
        key, value = [x.strip() for x in attribute.split("=")]
        user_changes[key] = value
    try:
        result = service.update_user_entry(username, user_changes)
        print("Update user success!")
        print("New user info:")
        user = service.get_user_detail(username)
        print(json.dumps(user, ensure_ascii=False))
    except Exception as error:
        print("Update user failed!!!")
        print("Error info:")
        print(str(error))


@ipa.command(name="delete-user")
@click.argument("username", nargs=1, required=True)
@click.pass_context
def delete_user(ctx, username):
    u"""Delete a user entry.
    """
    print("USERNAME:", username)
    service = IpaService(ctx.obj["host"], ctx.obj["port"], ctx.obj["base_dn"], ctx.obj["username"], ctx.obj["password"])
    try:
        result = service.delete_user_entry(username)
        print("User {} deleted!".format(username))
    except Exception as error:
        print("Delete user failed!!!")
        print("Error info:")
        print(str(error))

@ipa.command(name="change-password")
@click.argument("username", nargs=1, required=True)
@click.argument("password", nargs=1, required=True)
@click.pass_context
def change_password(ctx, username, password):
    u"""Delete a user entry.
    """
    print("USERNAME:", username)
    print("PASSWORD:", password)
    service = IpaService(ctx.obj["host"], ctx.obj["port"], ctx.obj["base_dn"], ctx.obj["username"], ctx.obj["password"])
    try:
        result = service.modify_user_password(username, password)
        print("User password changed!")
    except Exception as error:
        print("Change user password failed!!!")
        print("Error info:")
        print(str(error))


if __name__ == "__main__":
    ipa()
