# -*- coding: utf-8 -*-
"""
"""
import logging

import cmdln

from apiaccesstoken.tokenmanager import Manager


class HelperCmds(cmdln.Cmdln):
    """Usage:
        tokenhelper SUBCOMMAND [ARGS...]
        tokenhelper help SUBCOMMAND

    ${command_list}
    ${help_list}

    """

    def do_make_access_secret(self, subcmd, opts):
        """${cmd_name}: Generate the api access secret for use with access
        token generation.

        ${cmd_usage}
        ${cmd_option_list}

        """
        print("New secret token is:\n\t{}".format(Manager.generate_secret()))

    def do_make_access_token(
        self, subcmd, opts, username, access_secret
    ):
        """${cmd_name}: Generate an access token.

        The username fields could be a database unique ID or something else
        which the server side can work with. This username is stored securely
        in the token payload.

        The secret is generated using make_access_secret.

        ${cmd_usage}
        ${cmd_option_list}

        """
        man = Manager(access_secret)
        at = man.generate_access_token(identity=username)
        print("New access token is:\n\t{}".format(at))


def main():
    """tokenhelper main with setup tools uses."""
    log = logging.getLogger()
    hdlr = logging.StreamHandler()
    fmt = '%(asctime)s %(name)s %(levelname)s %(message)s'
    formatter = logging.Formatter(fmt)
    hdlr.setFormatter(formatter)
    log.addHandler(hdlr)
    log.setLevel(logging.DEBUG)
    log.propagate = False
    HelperCmds().main()
