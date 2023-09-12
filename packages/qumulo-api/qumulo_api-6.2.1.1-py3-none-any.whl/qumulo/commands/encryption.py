# Copyright (c) 2020 Qumulo, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy of
# the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.


import argparse

import qumulo.lib.opts

from qumulo.rest.encryption import KmipKeyStoreConfigPut
from qumulo.rest_client import RestClient


class RotateEncryptionKeysCommand(qumulo.lib.opts.Subcommand):
    NAME = 'rotate_encryption_keys'
    SYNOPSIS = 'Rotate the at-rest encryption master keys.'

    @staticmethod
    def main(rest_client: RestClient, _args: argparse.Namespace) -> None:
        resp = rest_client.encryption.rotate_keys()
        assert not resp, f'Unexpected response from key rotation API: {resp}'
        print('Key rotation complete')


class EncryptionGetStatusCommand(qumulo.lib.opts.Subcommand):
    NAME = 'encryption_get_status'
    SYNOPSIS = 'Get at-rest encryption status.'

    @staticmethod
    def main(rest_client: RestClient, _args: argparse.Namespace) -> None:
        resp = rest_client.encryption.status()
        print(resp)


class RotateEncryptionKeysV2Command(qumulo.lib.opts.Subcommand):
    # XXX nmccausland: We can rename this and get rid of the V1 command once this endpoint is made
    # public.
    NAME = 'encryption_rotate_keys_v2'
    SYNOPSIS = 'Rotate the at-rest encryption master keys.'

    @staticmethod
    def options(parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            '--key-id',
            type=str,
            dest='key_id',
            default=None,
            help='The key ID of the master key if using a Key Management System',
        )

    @staticmethod
    def main(rest_client: RestClient, args: argparse.Namespace) -> None:
        rest_client.encryption.rotate_keys_v2(key_id=args.key_id)
        print('Key rotation complete')


class KeyStoreStatusCommand(qumulo.lib.opts.Subcommand):
    NAME = 'encryption_get_key_store_status'
    SYNOPSIS = 'Get the status of the active at-rest encryption key store.'

    @staticmethod
    def main(rest_client: RestClient, _args: argparse.Namespace) -> None:
        resp = rest_client.encryption.get_key_store_status()
        print(resp)


class GetEncryptionKeyStoreCommand(qumulo.lib.opts.Subcommand):
    NAME = 'encryption_get_key_store'
    SYNOPSIS = 'Get the active at-rest encryption configuration.'

    @staticmethod
    def main(rest_client: RestClient, _args: argparse.Namespace) -> None:
        resp = rest_client.encryption.get_key_store_config()
        print(resp)


class PutEncryptionKeyStoreCommand(qumulo.lib.opts.Subcommand):
    NAME = 'encryption_set_key_store'
    SYNOPSIS = 'Set the active at-rest encryption configuration.'

    @staticmethod
    def options(parser: argparse.ArgumentParser) -> None:
        subparsers = parser.add_subparsers(dest='key_store_type', required=True)

        kmip_parser = subparsers.add_parser(
            'kms', help='Set a KMS (Key Management System) configuration'
        )
        kmip_parser.add_argument(
            '--client-cert',
            type=str,
            dest='client_cert',
            required=True,
            help='The path to the client certificate file used to connect to the KMIP server.',
        )
        kmip_parser.add_argument(
            '--client-private-key',
            type=str,
            dest='client_private_key',
            required=True,
            help=(
                'The path to the file containing the client private key used to connect to the KMIP'
                ' server.'
            ),
        )
        kmip_parser.add_argument(
            '--hostname',
            type=str,
            dest='hostname',
            required=True,
            help='The hostname where the KMIP server can be reached.',
        )

        # According to the specification, the port should be 5696 but we allow overriding it for
        # testing and handling non-standard configurations.
        # http://docs.oasis-open.org/kmip/profiles/v1.4/os/kmip-profiles-v1.4-os.html#_Toc491431402
        default_port = '5696'
        kmip_parser.add_argument(
            '--port',
            type=str,
            dest='kmip_server_port',
            required=False,
            default=default_port,
            help='The hostname where the KMIP server can be reached. Defaults to 5696',
        )
        kmip_parser.add_argument(
            '--key-id',
            type=str,
            dest='key_id',
            required=True,
            help='The key ID of the master key if using a Key Management System',
        )
        kmip_parser.add_argument(
            '--server-ca-cert',
            type=str,
            dest='server_ca_cert',
            required=True,
            help='The path to a file containing the CA cert of the KMIP server.',
        )

        # Local doesn't need any parameters
        subparsers.add_parser('local', help='Create a local at-rest encryption configuration')

    @staticmethod
    def main(rest_client: RestClient, args: argparse.Namespace) -> None:
        key_store_config = None
        if args.key_store_type == 'kms':
            client_cert_data = ''
            with open(args.client_cert) as f:
                client_cert_data = f.read()

            client_private_key_data = ''
            with open(args.client_private_key) as f:
                client_private_key_data = f.read()

            server_ca_cert_data = ''
            with open(args.server_ca_cert) as f:
                server_ca_cert_data = f.read()

            key_store_config = KmipKeyStoreConfigPut(
                client_cert=client_cert_data,
                client_private_key=client_private_key_data,
                hostname=args.hostname,
                key_id=args.key_id,
                port=args.kmip_server_port,
                server_ca_cert=server_ca_cert_data,
            )

        rest_client.encryption.put_key_store_config(config=key_store_config)
