# -------------------------------------------------------------------------
# Copyright 2023-2023, Boling Consulting Solutions, bcsw.net
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License
# -------------------------------------------------------------------------

from typing import Union, Optional

from tls_packet.auth.tls_handshake import TLSHandshake
from tls_packet.packet import PARSE_ALL


class ClientDiffieHellmanPublic:
    """
    Client Diffie-Hellman Public Value

        This structure conveys the client's Diffie-Hellman public value
        (Yc) if it was not already included in the client's certificate.

        The encoding used for Yc is determined by the enumerated
        PublicValueEncoding.  This structure is a variant of the client
        key exchange message, and not a message in itself.

    Structure of this message:

      enum { implicit, explicit } PublicValueEncoding;

      implicit
         If the client has sent a certificate which contains a suitable
         Diffie-Hellman key (for fixed_dh client authentication), then
         Yc is implicit and does not need to be sent again.  In this
         case, the client key exchange message will be sent, but it MUST
         be empty.

      explicit
         Yc needs to be sent.

      struct {
          select (PublicValueEncoding) {
              case implicit: struct { };
              case explicit: opaque dh_Yc<1..2^16-1>;
          } dh_public;
      } ClientDiffieHellmanPublic;

      dh_Yc
         The client's Diffie-Hellman public value (Yc).
    """
    def __init__(self):
        self.x = 0

    @staticmethod
    def parse(frame: bytes, *args, max_depth: Optional[int] = PARSE_ALL, **kwargs) -> Union[TLSHandshake, None]:
        """ Frame to RSAPreMasterSecret """
        raise NotImplementedError("TODO: Not yet supported")

    def pack(self, payload: Optional[Union[bytes, None]] = None) -> bytes:
        """
        For all key exchange methods, the same algorithm is used to convert
        the pre_master_secret into the master_secret.  The pre_master_secret
        should be deleted from memory once the master_secret has been
        computed.

          master_secret = PRF(pre_master_secret, "master secret",
                              ClientHello.random + ServerHello.random)
                              [0..47];

        The master secret is always exactly 48 bytes in length.  The length
        of the premaster secret will vary depending on key exchange method.

           A conventional Diffie-Hellman computation is performed.  The
           negotiated key (Z) is used as the pre_master_secret, and is converted
           into the master_secret, as specified above.  Leading bytes of Z that
           contain all zero bits are stripped before it is used as the
           pre_master_secret.

           Note: Diffie-Hellman parameters are specified by the server and may
           be either ephemeral or contained within the server's certificate.
        """
        return b''



