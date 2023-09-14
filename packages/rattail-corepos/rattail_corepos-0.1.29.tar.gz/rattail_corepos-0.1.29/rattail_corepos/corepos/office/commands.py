# -*- coding: utf-8; -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2023 Lance Edgar
#
#  This file is part of Rattail.
#
#  Rattail is free software: you can redistribute it and/or modify it under the
#  terms of the GNU General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later
#  version.
#
#  Rattail is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#  FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
#  details.
#
#  You should have received a copy of the GNU General Public License along with
#  Rattail.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
"""
CORE Office commands
"""

import logging
import sys

import requests
from requests.auth import HTTPDigestAuth

from rattail import commands
from rattail_corepos import __version__
from rattail.util import load_object
from rattail_corepos.corepos.office.util import get_fannie_config_value
from rattail_corepos.corepos.api import make_corepos_api
from rattail_corepos.corepos.util import get_core_members
from rattail_corepos.config import core_office_url


log = logging.getLogger(__name__)


def main(*args):
    """
    Entry point for 'core-office' commands
    """
    if args:
        args = list(args)
    else:
        args = sys.argv[1:]

    cmd = Command()
    cmd.run(*args)


class Command(commands.Command):
    """
    Primary command for CORE Office
    """
    name = 'core-office'
    version = __version__
    description = "core-office -- command line interface for CORE Office"
    long_description = ""


class Anonymize(commands.Subcommand):
    """
    Update customer etc. data to make it anonymous
    """
    name = 'anonymize'
    description = __doc__.strip()

    def add_parser_args(self, parser):
        parser.add_argument('--force', '-f', action='store_true',
                            help="Do not prompt for confirmation.")

    def run(self, args):
        if not args.force:
            self.rprint("\n[bold yellow]**WARNING** this will modify all customer (and similar) records![/bold yellow]")
            value = input("\nreally want to do this? [yN] ")
            if not value or not self.config.parse_bool(value):
                self.stderr.write("user canceled\n")
                sys.exit(1)

        try:
            import names
        except ImportError:
            self.stderr.write("must install the `names` package first!\n\n"
                              "\tpip install names\n")
            sys.exit(2)

        from rattail_corepos.corepos.api import make_corepos_api
        from rattail_corepos.corepos.util import get_core_members

        api = make_corepos_api(self.config)
        members = get_core_members(self.config, api, progress=self.progress)

        def anonymize(member, i):
            data = dict(member)
            cardno = data.pop('cardNo')

            for customer in data['customers']:
                customer['firstName'] = names.get_first_name()
                customer['lastName'] = names.get_last_name()

            api.set_member(cardno, **data)

        self.progress_loop(anonymize, members,
                           message="Anonymizing all member data")


class CoreDBImportSubcommand(commands.ImportSubcommand):
    """
    Base class for commands which import straight to CORE DB
    """

    def add_parser_args(self, parser):
        super().add_parser_args(parser)

        parser.add_argument('--corepos-dbtype', metavar='TYPE', default='office_op',
                            choices=['office_op', 'office_trans'],
                            help="Config *type* for CORE-POS database engine to which data "
                            "should be written.  Default type is 'office_op' - this determines "
                            "which config section is used with regard to the --corepos-dbkey arg.")

        parser.add_argument('--corepos-dbkey', metavar='KEY', default='default',
                            help="Config key for CORE-POS database engine to which data should "
                            "be written.  This key must be defined in the config section as "
                            "determiend by the --corpos-dbtype arg.")

    def get_handler_kwargs(self, **kwargs):
        if 'args' in kwargs:
            kwargs['corepos_dbtype'] = kwargs['args'].corepos_dbtype
            kwargs['corepos_dbkey'] = kwargs['args'].corepos_dbkey
        return kwargs


class ExportLaneOp(commands.ImportSubcommand):
    """
    Export "op" data from CORE Office to CORE Lane
    """
    name = 'export-lane-op'
    description = __doc__.strip()
    handler_key = 'to_corepos_db_lane_op.from_corepos_db_office_op.export'
    default_dbkey = 'default'

    def add_parser_args(self, parser):
        super(ExportLaneOp, self).add_parser_args(parser)
        parser.add_argument('--dbkey', metavar='KEY', default=self.default_dbkey,
                            help="Config key for database engine to be used as the "
                            "\"target\" CORE Lane DB, i.e. where data will be "
                            " exported.  This key must be defined in the "
                            " [rattail_corepos.db.lane_op] section of your "
                            "config file.")

    def get_handler_kwargs(self, **kwargs):
        if 'args' in kwargs:
            kwargs['dbkey'] = kwargs['args'].dbkey
        return kwargs


class GetConfigValue(commands.Subcommand):
    """
    Get a value from CORE Office `fannie/config.php`
    """
    name = 'get-config-value'
    description = __doc__.strip()

    def add_parser_args(self, parser):
        parser.add_argument('name', metavar='NAME',
                            help="Name of the config value to get.  "
                            "Prefix of `FANNIE_` is not required.")

    def run(self, args):
        value = get_fannie_config_value(self.config, args.name)
        self.stdout.write(f"{value}\n")


class ExportCSV(commands.ExportFileSubcommand):
    """
    Export data from CORE to CSV file(s)
    """
    name = 'export-csv'
    description = __doc__.strip()
    handler_key = 'to_csv.from_corepos_db_office_op.export'


class ImportCSV(commands.ImportFileSubcommand):
    """
    Import data from CSV to CORE Office "op" DB
    """
    name = 'import-csv'
    description = __doc__.strip()
    handler_key = 'to_corepos_db_office_op.from_csv.import'

    def add_parser_args(self, parser):
        super().add_parser_args(parser)

        parser.add_argument('--dbkey', metavar='KEY', default='default',
                            help="Config key for database engine to be used as the \"target\" "
                            "CORE DB, i.e. where data will be imported *to*.  This key must be "
                            "defined in the [corepos.db.office_op] section of your config file.")

    def get_handler_kwargs(self, **kwargs):
        kwargs = super().get_handler_kwargs(**kwargs)

        if 'args' in kwargs:
            args = kwargs['args']
            kwargs['dbkey'] = args.dbkey

        return kwargs


class ImportSelf(commands.ImportSubcommand):
    """
    Import data from CORE Office ("op" DB) to "self"
    """
    name = 'import-self'
    description = __doc__.strip()
    handler_key = 'to_self.from_corepos_db_office_op.import'


class PatchCustomerGaps(commands.Subcommand):
    """
    POST to the CORE API as needed, to patch gaps for customerID
    """
    name = 'patch-customer-gaps'
    description = __doc__.strip()

    def add_parser_args(self, parser):
        parser.add_argument('--dry-run', action='store_true',
                            help="Do not POST anything, but log members needing it.")

    def run(self, args):
        from corepos.db.office_op import model as corepos

        corepos_api = make_corepos_api(self.config)
        members = get_core_members(self.config, corepos_api, progress=self.progress)
        tally = self.app.make_object(updated=0)

        self.maxlen_phone = self.app.maxlen(corepos.Customer.phone)
        # nb. just in case the smallest one changes in future..
        other = self.app.maxlen(corepos.MemberInfo.phone)
        if other < self.maxlen_phone:
            self.maxlen_phone = other

        def inspect(member, i):
            for customer in member['customers']:
                customer_id = int(customer['customerID'])
                if not customer_id:
                    data = dict(member)
                    self.trim_phones(data)
                    cardno = data.pop('cardNo')
                    log.debug("%s call set_member() for card no %s: %s",
                              'should' if args.dry_run else 'will',
                              cardno, data)
                    if not args.dry_run:
                        corepos_api.set_member(cardno, **data)
                    tally.updated += 1
                    return

        action = "Finding"
        if not args.dry_run:
            action += " and fixing"
        self.progress_loop(inspect, members,
                           message=f"{action} customerID gaps")

        self.stdout.write("\n")
        if args.dry_run:
            self.stdout.write("would have ")
        self.stdout.write(f"updated {tally.updated} members\n")

    def trim_phones(self, data):
        # the `meminfo` table allows 30 chars for phone, but
        # `Customers` table only allows 20 chars.  so we must trim to
        # 20 chars or else the CORE API will silently fail to update
        # tables correctly when we POST to it
        for customer in data['customers']:
            for field in ['phone', 'altPhone']:
                value = customer[field]
                if len(value) > self.maxlen_phone:
                    log.warning("phone value for cardno %s is too long (%s chars) "
                                "and will be trimmed to %s chars: %s",
                                data['cardNo'],
                                len(value),
                                self.maxlen_phone,
                                value)
                    customer[field] = value[:self.maxlen_phone]


class PingInstall(commands.Subcommand):
    """
    Ping the /install URL in CORE Office (for DB setup)
    """
    name = 'ping-install'
    description = __doc__.strip()

    def run(self, args):
        url = core_office_url(self.config, require=True)
        url = f'{url}/install/'

        # TODO: hacky re-using credentials from API config..
        username = self.config.get('corepos.api', 'htdigest.username')
        password = self.config.get('corepos.api', 'htdigest.password')

        session = requests.Session()
        if username and password:
            session.auth = HTTPDigestAuth(username, password)

        response = session.get(url)
        response.raise_for_status()
