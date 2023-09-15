# Copyright 2023 Henix, henix.fr
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

"""opentf-ctl get qualitygate gitlab extension"""

from typing import Any, Dict, Optional, Tuple

import requests

from opentf.tools.ctlcommons import _error, _warning, _debug


########################################################################
# Gitlab MR note posting

NOTEST = 'NOTEST'
FAILURE = 'FAILURE'
SUCCESS = 'SUCCESS'
INVALIDSCOPE = 'INVALID_SCOPE'

FORMAT_BY_STATUS = {
    NOTEST: {
        'emoji': ':no_entry_sign:',
        'msg': 'no test',
        'cats': ':no_entry_sign: :joy_cat:',
    },
    FAILURE: {
        'emoji': ':x:',
        'msg': 'failure',
        'cats': ':x: :smile_cat:',
    },
    SUCCESS: {
        'emoji': ':white_check_mark:',
        'msg': 'success',
        'cats': ':white_check_mark: :cat:',
    },
    INVALIDSCOPE: {
        'emoji': ':exclamation:',
        'msg': 'invalid scope',
        'cats': ':exclamation: :smirk_cat:',
    },
}

NOTES_API_PATH = '/api/v4/projects/{project_id}/merge_requests/{merge_request_id}/notes'
NOTE_HEADER = '<h2>Quality gate status for mode {mode}</h2>'

DEFAULT_TIMEOUT = 10  # HTTP requests timeout

########################################################################
# API requests


def _already_has_note(
    base_url: str,
    path: str,
    mode: str,
    token: Optional[Dict[str, str]],
    last_note_id: int,
) -> Optional[str]:
    try:
        what = requests.get(base_url + path, params=token, timeout=DEFAULT_TIMEOUT)
        if what.status_code == 200:
            note_id = [
                note['id']
                for note in what.json()
                if (NOTE_HEADER.format(mode=mode) in note['body'])
                and (note['id'] != last_note_id)
            ]
            return note_id[0] if note_id else None
        _error(
            'Cannot retrieve notes from Gitlab: status code %s, error %s.',
            what.status_code,
            what.json(),
        )
    except Exception as err:
        _error('Exception while retrieving notes from Gitlab: %s.', str(err))
    return None


def _post_mr_note(
    base_url: str, path: str, data: Dict[str, Any], token: Optional[Dict[str, str]]
) -> Tuple[Dict[str, Any], int]:
    what = requests.post(
        base_url + path, data=data, params=token, timeout=DEFAULT_TIMEOUT
    )
    return what.json(), what.status_code


def _delete_mr_note(base_url: str, path: str, token: Optional[Dict[str, str]]) -> int:
    what = requests.delete(base_url + path, params=token, timeout=DEFAULT_TIMEOUT)
    return what.status_code


########################################################################
# Formatting


def _format_qualitygate_response(
    mode: str, qualitygate: Dict[str, Any], cats: bool
) -> str:
    emoji = 'cats' if cats else 'emoji'
    status = qualitygate['status']
    formatted = NOTE_HEADER.format(mode=mode)

    if status == FAILURE:
        formatted += f'<h2>Quality gate failed {FORMAT_BY_STATUS[status][emoji]}</h2>'
    elif status == SUCCESS:
        formatted += f'<h2>Quality gate passed {FORMAT_BY_STATUS[status][emoji]}</h2>'
    elif status == NOTEST:
        formatted += (
            f'<h2>Quality gate not applied {FORMAT_BY_STATUS[status][emoji]}</h2>'
        )
        formatted += 'Workflow contains no test matching quality gate scopes.'
    formatted += _get_rules_summary(qualitygate)

    warnings = list(qualitygate.get('warnings', [])) + [
        f'Rule <b>{name}</b>: {data["message"]}'
        for name, data in qualitygate['rules'].items()
        if data['result'] == INVALIDSCOPE
    ]
    if warnings:
        formatted += '<h2>Warnings :warning:</h2>'
        formatted += '<ul>'
        formatted += '\n'.join(f'<li>{msg}</li>' for msg in warnings)
        formatted += '</ul>'
    return formatted


def _get_rules_summary(qualitygate: Dict[str, Any]) -> str:
    rules_summary = '<h3>Rules summary</h3>'
    for name, data in qualitygate['rules'].items():
        status = data['result']
        result_emoji = FORMAT_BY_STATUS[status]['emoji']
        rules_summary += f"""{result_emoji} <b>{name.upper()}</b>: {FORMAT_BY_STATUS[status]['msg']}.
Tests: {data.get('tests_in_scope', 0)},
failed: {data.get('tests_failed', 0)},
passed: {data.get('tests_passed', 0)},
success ratio: {data.get('success_ratio', 'N/A')},
threshold: {data['threshold']}<br>"""
    return rules_summary


########################################################################


def publish_results(
    gl_push: str, gl_token: Optional[str], mode: str, qualitygate: Dict[str, Any]
) -> None:
    """Push a note to gitlab.

    `gl_push` format:

    `$CI_SERVER_URL,$CI_MERGE_REQUEST_PROJECT_ID,$CI_MERGE_REQUEST_IID[,cats]`

    # Required parameters

    - gl_push: a string
    - gl_token: a string or None
    - mode: a string
    - response: a dictionary
    """
    args = gl_push.split(',')
    if (args_len := len(args)) not in (3, 4):
        _error(
            'Cannot post results to GitLab. Invalid "gl_push" parameter.  Expected $CI_SERVER_URL, $CI_MERGE_REQUEST_PROJECT_ID, $CI_MERGE_REQUEST_IID, got: %s.',
            gl_push,
        )
        return
    if args_len == 3:
        base_url, project_id, merge_request_id, cats = *args, False
    else:
        base_url, project_id, merge_request_id, cats = args
        cats = cats == 'cats'
    path = NOTES_API_PATH.format(
        project_id=project_id, merge_request_id=merge_request_id
    )
    token = {'private_token': gl_token} if gl_token else None
    data = {'body': _format_qualitygate_response(mode, qualitygate, cats)}

    try:
        response, status = _post_mr_note(base_url, path, data, token)
        if status != 201:
            _warning(
                'Failed to post Quality gate results: response code %d, error message: %s.',
                status,
                response,
            )
            return
        note_id = _already_has_note(base_url, path, mode, token, response['id'])
        if note_id is None:
            return
        path += f'/{note_id}'
        status = _delete_mr_note(base_url, path, token)
        if status not in (204, 202):
            _debug(
                'Failed to remove previous quality gate results: response code %d.',
                status,
            )
    except Exception as err:
        _error('Error while posting results to Gitlab. %s.', str(err))
