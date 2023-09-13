# Copyright 2021-2023 Henix, henix.fr
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""opentf-ctl"""

from typing import Any, Dict, List, Union

import sys

from datetime import datetime

import jwt

from opentf.tools.ctlcommons import (
    _is_command,
    _error,
    _warning,
)

########################################################################

# pylint: disable=broad-except


########################################################################
# Help messages

GENERATE_TOKEN_HELP = '''Generate a signed token

Example:
  # Generate token interactively
  opentf-ctl generate token using path/to/private.pem

Usage:
  opentf-ctl generate token using NAME [options]

Use "opentf-ctl options" for a list of global command-line options (applies to all commands).
'''

VIEW_TOKEN_HELP = '''View token payload

Example:
  # Display token payload
  opentf-ctl view token $TOKEN

Usage:
  opentf-ctl view token TOKEN [options]

Use "opentf-ctl options" for a list of global command-line options (applies to all commands).
'''

VALIDATE_TOKEN_HELP = '''Validate token signature

Example:
  # Validate token
  opentf-ctl check token $TOKEN using path/to/public.pub

Usage:
  opentf-ctl check token TOKEN using NAME [options]

Use "opentf-ctl options" for a list of global command-line options (applies to all commands).
'''


########################################################################
# JWT tokens

ALLOWED_ALGORITHMS = [
    'ES256',  # ECDSA signature algorithm using SHA-256 hash algorithm
    'ES384',  # ECDSA signature algorithm using SHA-384 hash algorithm
    'ES512',  # ECDSA signature algorithm using SHA-512 hash algorithm
    'RS256',  # RSASSA-PKCS1-v1_5 signature algorithm using SHA-256 hash algorithm
    'RS384',  # RSASSA-PKCS1-v1_5 signature algorithm using SHA-384 hash algorithm
    'RS512',  # RSASSA-PKCS1-v1_5 signature algorithm using SHA-512 hash algorithm
    'PS256',  # RSASSA-PSS signature using SHA-256 and MGF1 padding with SHA-256
    'PS384',  # RSASSA-PSS signature using SHA-384 and MGF1 padding with SHA-384
    'PS512',  # RSASSA-PSS signature using SHA-512 and MGF1 padding with SHA-512
]


def _load_pem_private_key(privatekey: str) -> Any:
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.backends import default_backend
    from cryptography.exceptions import UnsupportedAlgorithm

    try:
        with open(privatekey, 'rb') as keyfile:
            pem = keyfile.read()
        try:
            return serialization.load_pem_private_key(pem, None, default_backend())
        except ValueError as err:
            _error(
                'This does not seem to be a valid private key in PEM format: %s.', err
            )
            sys.exit(2)
        except TypeError:
            from getpass import getpass

            try:
                passphrase = getpass(
                    'This private key is encrypted, please enter the passphrase: '
                )
                if not passphrase:
                    _error('Passphrase cannot be empty, the private key is encrypted.')
                    sys.exit(2)
                return serialization.load_pem_private_key(
                    pem, passphrase.encode('utf-8'), backend=default_backend()
                )
            except ValueError as err:
                _error(str(err))
                sys.exit(2)
    except UnsupportedAlgorithm as err:
        _error(
            'The serialized key type is not supported by the OpenSSL version "cryptography" is using: %s.',
            err,
        )
        sys.exit(2)
    except IsADirectoryError:
        _error(
            'The specified private key must be a file, not a directory: %s.', privatekey
        )
        sys.exit(2)
    except FileNotFoundError:
        _error('The specified private key could not be found: %s.', privatekey)
        sys.exit(2)


def _generate_token(privatekey: str) -> None:
    private_key = _load_pem_private_key(privatekey)
    algorithm = (
        input('Please specify an algorithm (RS512 if unspecified): ').strip() or 'RS512'
    )
    print('The specified algorithm is:', algorithm)
    while not (
        issuer := input(
            'Please enter the issuer (your company or department): '
        ).strip()
    ):
        _warning('The issuer cannot be empty.')
    while not (
        subject := input(
            'Please enter the subject (you or the person you are making this token for): '
        )
    ):
        _warning('The subject cannot be empty.')
    exp = (
        input(
            'Please specify an expiration date in YYYY/MM/DD format (never if unspecified): '
        ).strip()
        or None
    )
    if exp:
        try:
            exp = int(datetime.strptime(exp, '%Y/%m/%d').timestamp())
        except ValueError:
            _error('Invalid expiration date format, must be YYYY/MM/DD.')
            sys.exit(2)

    try:
        payload: Dict[str, Union[str, int]] = {'iss': issuer, 'sub': subject}
        if exp:
            payload['exp'] = exp
        token = jwt.encode(payload, private_key, algorithm=algorithm)
    except NotImplementedError:
        _error('Algorithm not supported: %s.', algorithm)
        sys.exit(2)
    except Exception as err:
        _error('Could not generate token: %s.', err)
        sys.exit(2)

    print('The signed token is:')
    print(token)


def generate_token(privatekey: str) -> None:
    """Generate JWT token.

    # Required parameters

    - privatekey: a non-empty string (a file name)

    # Raised exceptions

    Abort with an error code 2 if something went wrong.
    """
    try:
        _generate_token(privatekey)
    except KeyboardInterrupt:
        print('^C')
        sys.exit(1)


def view_token(token: str) -> None:
    """View JWT token payload.

    # Required parameters

    - token: a non-empty string (a JWT token)

    # Raised exceptions

    Abort with an error code 2 if something went wrong.
    """
    try:
        payload = jwt.decode(token, options={'verify_signature': False})
        print('The token payload is:')
        if 'exp' in payload:
            payload['exp'] = datetime.fromtimestamp(payload['exp']).strftime('%Y/%m/%d')
        print(payload)
    except Exception as err:
        _error('The specified token is invalid: %s', err)
        print(token)
        sys.exit(2)


def check_token(token: str, keyname: str) -> None:
    """Check JWT token signature.

    # Required parameters

    - token: a non-empty string (a JWT token)
    - keyname: a non-empty string (a file name)

    # Raised exceptions

    Abort with an error code 2 if something went wrong.
    """
    try:
        with open(keyname, 'r', encoding='utf-8') as keyfile:
            key = keyfile.read()
    except IsADirectoryError:
        _error('The specified public key must be a file, not a directory: %s.', keyname)
        sys.exit(2)
    except FileNotFoundError:
        _error('The specified public key could not be found: %s.', keyname)
        sys.exit(2)

    try:
        payload = jwt.decode(token, key, algorithms=ALLOWED_ALGORITHMS)
        print(
            f'The token is signed by the {keyname} public key.  The token payload is:'
        )
        print(payload)
    except jwt.exceptions.InvalidSignatureError:
        _error('The token is not signed by %s.', keyname)
        sys.exit(102)
    except (TypeError, AttributeError) as err:
        _error(
            'The specified key does not looks like a public key.'
            + '  Got "%s" while reading the provided key.',
            err,
        )
        sys.exit(2)
    except ValueError as err:
        _error(err.args[0])
        sys.exit(2)
    except Exception as err:
        _error('Could not validate token signature: %s.', err)
        sys.exit(2)


########################################################################
# Helpers


def print_tokens_help(args: List[str]) -> None:
    """Display help."""
    if _is_command('generate token', args):
        print(GENERATE_TOKEN_HELP)
    elif _is_command('view token', args):
        print(VIEW_TOKEN_HELP)
    elif _is_command('check token', args):
        print(VALIDATE_TOKEN_HELP)
    else:
        _error('Unknown command.  Use --help to list known commands.')
        sys.exit(1)


########################################################################
# Main


def tokens_cmd():
    """Process tokens command."""
    if _is_command('generate token using _', sys.argv):
        if len(sys.argv) > 5:
            _error(
                f'"opentf-ctl generate token" does not take options.  Got "{" ".join(sys.argv[5:])}".'
            )
            sys.exit(2)
        generate_token(sys.argv[4])
        sys.exit(0)
    if _is_command('view token _', sys.argv):
        if len(sys.argv) > 4:
            _error(
                f'"opentf-ctl view token" does not take options.  Got "{" ".join(sys.argv[4:])}".'
            )
            sys.exit(2)
        view_token(sys.argv[3])
        sys.exit(0)
    if _is_command('check token _ using _', sys.argv):
        if len(sys.argv) > 6:
            _error(
                f'"opentf-ctl check token" does not take options.  Got "{" ".join(sys.argv[6:])}".'
            )
            sys.exit(2)
        check_token(sys.argv[3], sys.argv[5])
        sys.exit(0)
    if _is_command('check token _', sys.argv):
        _error('Missing required parameter.  Use "check token --help" for details.')
        sys.exit(2)
    else:
        _error('Unknown command.  Use --help to list known commands.')
        sys.exit(1)
