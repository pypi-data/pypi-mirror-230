#! /usr/bin/env python3

import sys

from typing import (
    Any,
    List,
    Dict,
)

from .handleDateStrings import str_to_date

from .context.parameterContext import ParameterContext
from .context.dataContext import DataContext


class Domain:
    def _cleanupArray(
        self,
        data: List[str],
    ) -> List[str]:
        if "" in data:
            index = data.index("")
            data.pop(index)
        return data

    def _doNameservers(
        self,
        data: Dict[str, Any],
    ) -> None:
        tmp: List[str] = []
        for x in data["name_servers"]:
            if isinstance(x, str):
                tmp.append(x.strip().lower())
                continue

            # not a string but an array
            for y in x:
                tmp.append(y.strip().lower())

        self.name_servers: List[str] = []
        for x in tmp:
            x = x.strip(" .")  # remove any leading or trailing spaces and/or dots
            if x:
                if " " in x:
                    x, _ = x.split(" ", 1)
                    x = x.strip(" .")

                x = x.lower()
                if x not in self.name_servers:
                    self.name_servers.append(x)

        self.name_servers = sorted(self.name_servers)

    def _doStatus(
        self,
        data: Dict[str, Any],
    ) -> None:
        self.status = data["status"][0].strip()

        # sorted added to get predictable output during test
        # list(set(...))) to deduplicate results

        self.statuses = sorted(
            list(
                set(
                    [s.strip() for s in data["status"]],
                ),
            ),
        )
        if "" in self.statuses:
            self.statuses = self._cleanupArray(self.statuses)

    def _doOptionalFields(
        self,
        data: Dict[str, Any],
    ) -> None:
        # optional fields

        if "owner" in data:
            self.owner = data["owner"][0].strip()

        if "abuse_contact" in data:
            self.abuse_contact = data["abuse_contact"][0].strip()

        if "reseller" in data:
            self.reseller = data["reseller"][0].strip()

        if "registrant" in data:
            if "registrant_organization" in data:
                self.registrant = data["registrant_organization"][0].strip()
            else:
                self.registrant = data["registrant"][0].strip()

        if "admin" in data:
            self.admin = data["admin"][0].strip()

        if "emails" in data:
            # sorted added to get predictable output during test
            # list(set(...))) to deduplicate results

            self.emails = sorted(
                list(
                    set(
                        [s.strip() for s in data["emails"]],
                    ),
                ),
            )
            if "" in self.emails:
                self.emails = self._cleanupArray(self.emails)

    def _parseData(
        self,
        dc: DataContext,
    ) -> None:
        # process mandatory fields that we expect always to be present
        # even if we have None or ''
        self.registrar = dc.data["registrar"][0].strip()
        self.registrant_country = dc.data["registrant_country"][0].strip()

        # date time items
        self.creation_date = str_to_date(dc.data["creation_date"][0], self.tld)
        self.expiration_date = str_to_date(dc.data["expiration_date"][0], self.tld)
        self.last_updated = str_to_date(dc.data["updated_date"][0], self.tld)

        self.dnssec = dc.data["DNSSEC"]
        self._doStatus(dc.data)
        self._doNameservers(dc.data)

        # optional fields
        self._doOptionalFields(dc.data)

    def __init__(
        self,
        pc: ParameterContext,
        dc: DataContext,
    ) -> None:
        pass
        # self.init(pc=pc, dc=dc)

    def init(
        self,
        pc: ParameterContext,
        dc: DataContext,
    ) -> None:
        if pc.include_raw_whois_text and dc.whoisStr is not None:
            self.text = dc.whoisStr

        if dc.exeptionStr is not None:
            self._exception = dc.exeptionStr
            return

        if dc.data == {}:
            return

        if pc.verbose:
            print(dc.data, file=sys.stderr)

        k = "domain_name"
        if k in dc.data:
            self.name = dc.data["domain_name"][0].strip().lower()

        k = "tld"
        if k in dc.data:
            self.tld = dc.data[k].lower()

        if pc.withPublicSuffix and dc.hasPublicSuffix:
            self.public_suffix: str = str(dc.publicSuffixStr)

        if pc.return_raw_text_for_unsupported_tld is True:
            return

        self._parseData(dc)
