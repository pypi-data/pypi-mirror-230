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
Clientele Handler
"""

from collections import OrderedDict
import logging
import warnings

from rattail.util import load_object
from rattail.app import GenericHandler


log = logging.getLogger(__name__)


class ClienteleHandler(GenericHandler):
    """
    Base class and default implementation for clientele handlers.
    """

    def choice_uses_dropdown(self):
        """
        Returns boolean indicating whether a customer choice should be
        presented to the user via a dropdown (select) element, vs.  an
        autocomplete field.  The latter is the default because
        potentially the customer list can be quite large, so we avoid
        loading them all in the dropdown unless so configured.

        :returns: Boolean; if true then a dropdown should be used;
           otherwise (false) autocomplete is used.
        """
        return self.config.getbool('rattail', 'customers.choice_uses_dropdown',
                                   default=False)

    def ensure_customer(self, person):
        """
        Returns the customer record associated with the given person, creating
        it first if necessary.
        """
        customer = self.get_customer(person)
        if customer:
            return customer

        session = self.get_session(person)
        customer = self.make_customer(person)
        session.add(customer)
        session.flush()
        session.refresh(person)
        return customer

    def get_customer(self, obj):
        """
        Return the Customer associated with the given object, if any.
        """
        model = self.model

        if isinstance(obj, model.Customer):
            return obj

        else:
            person = self.app.get_person(obj)
            if person:
                # TODO: all 3 options below are indeterminate, since it's
                # *possible* for a person to hold multiple accounts
                # etc. but not sure how to fix in a generic way?  maybe
                # just everyone must override as needed
                if person.customer_accounts:
                    return person.customer_accounts[0]
                for shopper in person.customer_shoppers:
                    if shopper.shopper_number == 1:
                        return shopper.customer
                # legacy fallback
                if person.customers:
                    return person.customers[0]

    def get_email_address(self, customer, **kwargs):
        """
        Return the first email address found for the given customer.

        :returns: The email address as string, or ``None``.
        """
        warnings.warn("clientele.get_email_address(customer) is deprecated; please "
                      "use app.get_contact_email_address(customer) instead",
                      DeprecationWarning, stacklevel=2)
        return self.app.get_contact_email_address(customer)

    def get_customers_for_account_holder(
            self,
            person,
            **kwargs
    ):
        """
        Return all Customer records for which the given Person is the
        account holder.
        """
        customers = OrderedDict()

        # find customers for which person is account holder
        for customer in person.customer_accounts:
            customers.setdefault(customer.uuid, customer)

        # find customers for which person is primary shopper
        for shopper in person.customer_shoppers:
            if shopper.shopper_number == 1:
                customer = shopper.customer
                customers.setdefault(customer.uuid, customer)

        # nb. legacy
        for customer in person.customers:
            customers.setdefault(customer.uuid, customer)

        return list(customers.values())

    def get_active_shopper(
            self,
            customer,
            **kwargs
    ):
        """
        Return the "active" shopper record for the given customer.

        This should never return multiple shoppers, either one or none.
        """
        for shopper in customer.shoppers:
            if shopper.active:
                return shopper

    def deactivate_shopper(self, shopper, **kwargs):
        """
        Deactivate the given shopper, i.e. make it no longer active
        for the customer account to which it belongs.

        :param shopper: The shopper to be deactivated.

        :param end_date: Optional end date for the deactivation.  If
           not specified, "today" is assumed.
        """
        # declare end date for current shopper history, if applicable
        if 'end_date' in kwargs:
            end_date = kwargs['end_date']
        else:
            end_date = self.app.today()
        if end_date:
            history = shopper.get_current_history()
            if history:
                history.end_date = end_date

        # mark shopper as no longer active
        shopper.active = False

    def shopper_was_active(self, shopper, date, **kwargs):
        """
        Inspect the shopper's history to determine if it was
        considered *active* (for the parent customer account) on the
        given date.

        :param shopper: The shopper to be checked.

        :param date: The date to be checked.

        :returns: Boolean indicating whether shopper was active on
           that date.
        """
        # try to find (all) applicable history for shopper
        applicable = []
        for history in reversed(shopper.history):
            if history.start_date > date:
                # this history began after the date
                continue
            if history.end_date and history.end_date < date:
                # this history ended before the date
                continue
            # okay, got one
            applicable.append(history)

        # if we found at least one "applicable" history record, that
        # means the shopper *was* indeed active on this date
        if applicable:
            # nb. there should only be *one* applicable record,
            # otherwise overlapping history records are implied
            if len(applicable) != 1:
                log.error("found (%s) applicable history records for shopper %s: %s",
                          len(applicable), shopper.uuid, shopper)
            return True

        # if we can't prove shopper was active, we assume they were *inactive*
        return False

    def get_person(self, customer):
        """
        Returns the person associated with the given customer, if there is one.
        """
        warnings.warn("ClienteleHandler.get_person() is deprecated; "
                      "please use AppHandler.get_person() instead")

        return self.app.get_person(customer)

    def make_customer(self, person, **kwargs):
        """
        Create and return a new customer record.
        """
        customer = self.model.Customer()
        customer.name = person.display_name
        customer.account_holder = person
        return customer

    def get_first_phone(self, customer, **kwargs):
        """
        Return the first available phone record found, either for the
        customer, or its first person.
        """
        phone = customer.first_phone()
        if phone:
            return phone

        person = self.app.get_person(customer)
        if person:
            return person.first_phone()

    def get_first_phone_number(self, customer, **kwargs):
        """
        Return the first available phone number found, either for the
        customer, or its first person.
        """
        phone = self.get_first_phone(customer)
        if phone:
            return phone.number

    def get_first_email(self, customer, invalid=False, **kwargs):
        """
        Return the first available email record found, either for the
        customer, or its first person.
        """
        email = customer.first_email(invalid=invalid)
        if email:
            return email

        person = self.app.get_person(customer)
        if person:
            return person.first_email(invalid=invalid)

    def get_first_email_address(self, customer, invalid=False, **kwargs):
        """
        Return the first available email address found, either for the
        customer, or its first person.
        """
        email = self.get_first_email(customer, invalid=invalid)
        if email:
            return email.address


def get_clientele_handler(config, **kwargs):
    """
    Create and return the configured :class:`ClienteleHandler` instance.
    """
    spec = config.get('rattail', 'clientele.handler')
    if spec:
        factory = load_object(spec)
    else:
        factory = ClienteleHandler
    return factory(config, **kwargs)
