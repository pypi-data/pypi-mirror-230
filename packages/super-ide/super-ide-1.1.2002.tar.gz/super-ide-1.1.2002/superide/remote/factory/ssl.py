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

import certifi
from OpenSSL import SSL  # pylint: disable=import-error
from twisted.internet import ssl  # pylint: disable=import-error


class SSLContextFactory(ssl.ClientContextFactory):
    def __init__(self, host):
        self.host = host
        self.certificate_verified = False

    def getContext(self):
        ctx = super().getContext()
        ctx.set_verify(
            SSL.VERIFY_PEER | SSL.VERIFY_FAIL_IF_NO_PEER_CERT, self.verifyHostname
        )
        ctx.load_verify_locations(certifi.where())
        return ctx

    def verifyHostname(  # pylint: disable=unused-argument,too-many-arguments
        self, connection, x509, errno, depth, status
    ):
        cn = x509.get_subject().commonName
        if cn.startswith("*"):
            cn = cn[1:]
        if self.host.endswith(cn):
            self.certificate_verified = True
        return status
