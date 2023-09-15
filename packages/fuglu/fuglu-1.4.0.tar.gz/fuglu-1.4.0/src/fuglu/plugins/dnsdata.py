# -*- coding: utf-8 -*-
#   Copyright Fumail Project
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
#

from fuglu.shared import ScannerPlugin, DUNNO
from fuglu.extensions.dnsquery import lookup, QTYPE_MX, QTYPE_A, QTYPE_NS, QTYPE_AAAA
from fuglu.stringencode import force_uString
from fuglu.mshared import BasicMilterPlugin, BMPRCPTMixin, BMPEOBMixin
import fuglu.connectors.asyncmilterconnector as asm
import fuglu.connectors.milterconnector as sm
from operator import itemgetter


LOOKUP_TYPES = [QTYPE_A, QTYPE_AAAA, QTYPE_MX, 'MXA', QTYPE_NS, 'NSA']


class DNSData(ScannerPlugin, BasicMilterPlugin, BMPRCPTMixin, BMPEOBMixin):
    """
Perform DNS lookups on sender or recipient domain and store them in suspect tag for later use

Plugin wrrites the following tags:
 * dnsdata.sender
 * dnsdata.recipient
    """

    def __init__(self, config, section=None):
        super().__init__(config, section)
        self.logger = self._logger()
        self.requiredvars = {
            'recipient_lookups': {
                'default': '',
                'description': 'comma separated list of dns lookup types to perform on recipient domains. supports %s MXA=get A of all MX, NSA=get A of all NS' % ','.join(LOOKUP_TYPES),
            },

            'sender_lookups': {
                'default': '',
                'description': 'comma separated list of dns lookup types to perform on sender domain. supports same types as recipient_lookup',
            },
            'state': {
                'default': asm.RCPT,
                'description': f'comma/space separated list states this plugin should be '
                               f'applied ({",".join(BasicMilterPlugin.ALL_STATES.keys())})'
            }
        }

    @staticmethod
    def _sort_mx(result):
        """
        sort MX ascending by prio, strip prio from lookup response
        """
        sortable_result = [(int(s[0]), s[1]) for s in [r.split() for r in sorted(result)]]
        sorted_result = sorted(sortable_result, key=itemgetter(0))
        return [s[1] for s in sorted_result]

    @staticmethod
    def _do_lookup_a(result):
        aresult = []
        for rec in result:
            res = lookup(rec, QTYPE_A) or []
            for ip in res:  # maintain previous result order (important for MXA)
                if not ip in aresult:
                    aresult.append(ip)
        return aresult

    def _do_lookups(self, domain, qtypes):
        results = {}
        for qtype in qtypes:
            lookupqtype = qtype[:2] if qtype in ['MXA', 'NSA'] else qtype
            result = lookup(domain, lookupqtype)
            if qtype in [QTYPE_MX, 'MXA'] and result:
                result = self._sort_mx(result)
            if qtype in ['MXA', 'NSA'] and result:
                result = self._do_lookup_a(result)
            if result is not None:
                results[qtype] = [r.rstrip('.') for r in result]
        return results

    def _run(self, suspect, recipients):
        if suspect.tags.get('dnsdata.sender') is None:
            sender_lookups = [l.upper() for l in self.config.getlist(self.section, 'sender_lookups')]
            sender_results = self._do_lookups(suspect.from_domain, sender_lookups)
            suspect.tags['dnsdata.sender'] = sender_results
            self.logger.debug(f'{suspect.id} dnsdata for senderdomain {suspect.from_domain} values {sender_results}')

        recipient_lookups = [l.upper() for l in self.config.getlist(self.section, 'recipient_lookups')]
        for recipient in recipients:
            rcpt_domain = recipient.rsplit('@', 1)[-1]
            recipient_tagname = f'dnsdata.recipient.{rcpt_domain.lower()}'
            if suspect.tags.get(recipient_tagname) is None:
                rcpt_results = self._do_lookups(rcpt_domain, recipient_lookups)
                suspect.tags[recipient_tagname] = rcpt_results
                self.logger.debug(f'{suspect.id} dnsdata for rcpt domain {rcpt_domain} {rcpt_results}')

    def examine(self, suspect):
        self._run(suspect, suspect.recipients)
        return DUNNO, None

    def examine_rcpt(self, sess, recipient):
        self._run(sess, [force_uString(recipient)])
        return sm.CONTINUE, None

    def examine_eob(self, sess):
        self._run(sess, [force_uString(r) for r in sess.recipients])
        return sm.CONTINUE, None

    def lint(self, state=None):
        ok = self.check_config()
        if not ok:
            print('ERROR: failed to check config')

        sender_lookups = [l.upper() for l in self.config.getlist(self.section, 'sender_lookups')]
        for item in sender_lookups:
            if item not in LOOKUP_TYPES:
                ok = False
                print(f'WARNING: invalid sender lookup type {item}')

        recipient_lookups = [l.upper() for l in self.config.getlist(self.section, 'recipient_lookups')]
        for item in recipient_lookups:
            if item not in LOOKUP_TYPES:
                ok = False
                print(f'WARNING: invalid recipient lookup type {item}')

        return ok
