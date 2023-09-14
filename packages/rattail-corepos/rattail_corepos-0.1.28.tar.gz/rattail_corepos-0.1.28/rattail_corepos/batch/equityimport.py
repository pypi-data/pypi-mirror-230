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
Handler for CORE equity import batches
"""

from rattail.batch import BatchHandler
from rattail_corepos.db.model import CoreEquityImportBatch


class CoreEquityImportBatchHandler(BatchHandler):
    """
    Handler for CORE member batches.
    """
    batch_model_class = CoreEquityImportBatch

    def refresh_row(self, row):
        session = self.app.get_session(row)
        model = self.model

        if not row.card_number:
            row.status_code = row.STATUS_MISSING_VALUES
            row.status_text = "card_number"
            return

        if not row.payment_amount:
            row.status_code = row.STATUS_MISSING_VALUES
            row.status_text = "payment_amount"
            return

        if not row.department_number:
            row.status_code = row.STATUS_MISSING_VALUES
            row.status_text = "department_number"
            return

        if not row.timestamp:
            row.status_code = row.STATUS_MISSING_VALUES
            row.status_text = "timestamp"
            return

        payment = row.payment
        member = payment.member if payment else None
        row.member = member
        if not member:
            row.status_code = row.STATUS_MEMBER_NOT_FOUND
            return

        memtype = member.membership_type
        row.member_type_id = memtype.number if memtype else None

        if member.person:
            person = member.person
            row.first_name = person.first_name
            row.last_name = person.last_name

        membership = self.app.get_membership_handler()
        row.rattail_equity_total = membership.get_equity_total(member)

        row.status_code = row.STATUS_OK

    def describe_execution(self, batch, **kwargs):
        return "New payment transactions will be added directly to CORE-POS."

    def get_effective_rows(self, batch):
        return [row for row in batch.active_rows()
                if row.status_code not in (row.STATUS_MISSING_VALUES,
                                           row.STATUS_MEMBER_NOT_FOUND)]

    def execute(self, batch, progress=None, **kwargs):
        if self.config.production():
            raise NotImplementedError("TODO: not yet implemented for production")

        session = self.app.get_session(batch)
        rows = self.get_effective_rows(batch)

        def process(row, i):
            payment = row.payment
            if payment:
                payment.corepos_card_number = row.card_number
                payment.corepos_department_number = row.department_number
                payment.corepos_transaction_number = 'pending'
            if i % 200 == 0:
                session.flush()

        self.progress_loop(process, rows, progress,
                           message="Processing payments")
        return True
