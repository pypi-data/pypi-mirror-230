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

"""opentf-ctl workflow handling part"""

from typing import Any, Dict, Iterable, List, NoReturn, Optional, Tuple

import json
import os
import re
import sys

from time import sleep

import yaml

from opentf.tools.ctlcommons import (
    _make_params_from_selectors,
    _ensure_either_uuids_or_selectors,
    _ensure_options,
    _is_command,
    _get_arg,
    generate_output,
    _ensure_uuid,
    _error,
    _warning,
    _debug,
)
from opentf.tools.ctlconfig import read_configuration, CONFIG
from opentf.tools.ctlnetworking import (
    _observer,
    _receptionist,
    _killswitch,
    _get,
    _delete,
    _post,
)


########################################################################

# pylint: disable=broad-except

DEFAULT_COLUMNS = (
    'WORKFLOW_ID:.metadata.workflow_id',
    'STATUS:.status.phase',
    'NAME:.metadata.name',
)
WIDE_COLUMNS = (
    'WORKFLOW_ID:.metadata.workflow_id',
    'STATUS:.status.phase',
    'FIRST_SEEN_TIMESTAMP:.metadata.creationTimestamp',
    'NAME:.metadata.name',
)


WATCHED_EVENTS = (
    'ExecutionCommand',
    'ExecutionResult',
    'ExecutionError',
    'ProviderCommand',
    'GeneratorCommand',
    'Notification',
)

AUTOVARIABLES_PREFIX = 'OPENTF_RUN_'

WAIT_WARMUP_DELAY = 1
WAIT_DELAY = 5
REFRESH_DELAY = 10

MAX_COMMAND_LENGTH = 15

TIMESTAMP_PATTERN = re.compile(r'\[\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}\] ')

########################################################################
# Help messages

GETWORKFLOWS_COMMAND = 'get workflows'
GETWORKFLOW_COMMAND = 'get workflow _'
RUNWORKFLOW_COMMAND = 'run workflow _'
KILLWORKFLOW_COMMAND = 'kill workflow *'
DELETEWORKFLOW_COMMAND = 'delete workflow *'

RUN_WORKFLOW_HELP = '''Start a workflow

Examples:
  # Start the workflow defined in my_workflow.yaml
  opentf-ctl run workflow my_workflow.yaml

  # Start the workflow and wait until it completes
  opentf-ctl run workflow my_workflow.yaml --wait

  # Start the workflow and define an environment variable
  opentf-ctl run workflow my_workflow.yaml -e TARGET=example.com

  # Start a workflow and provide environment variables defined in a file
  opentf-ctl run workflow my_workflow.yaml -e variables

  # Start a workflow and provide a localy-defined environment variable
  export OPENTF_RUN_MYVAR=my_value
  opentf-ctl run workflow my_workflow.yaml  # variable 'MYVAR' will be defined

  # Start the wokflow and provide a local file
  opentf-ctl run workflow my_workflow.yaml -f key=./access_key.pem

Environment Variables:
  Environment variables with an 'OPENTF_RUN_' prefix will be defined without the prefix in the workflow and while running commands in execution environment.

Options:
  -e var=value: 'var' will be defined in the workflow and while running commands in execution environment.
  -e path/to/file: variables defined in file will be defined in the workflow and while running commands in execution environment.  'file' must contain one variable definition per line, of the form 'var=value'.
  -f name=path/to/file: the specified local file will be available for use by the workflow.  'name' is the file name specified in the `resources.files` part of the workflow.
  --namespace=default or -n=default: the workflow will run on the specified namespace.
  --wait or --watch or -w: wait for workflow completion.
  --step-depth=1 or -s=1: show nested steps to the given depth (only used with --wait).
  --job-depth=1 or -j=1: show nested jobs to the given depth (only used with --wait).
  --max-command-length=15 or -c=15: show the first n characters of running commands (only used with --wait).
  --selector=s or -l=s: selector (label query) to filter on, supports '=', '==', and '!='.  (e.g. -l key1=value1,key2=value2) (only used with --wait)
  --field-selector=s: selector (field query) to filter on, supports '=', '==', and '!='. (e.g. --field-selector key1=value1,key2=value2) (only used with --wait)
    (more at: https://opentestfactory.org/tools/running-commands#label-and-field-selectors)

Usage:
  opentf-ctl run workflow NAME [-e var=value]... [-e path/to/file] [-f name=path/to/file]... [--namespace=value] [--wait] [--job_depth=value] [--step_depth=value] [options]

Use "opentf-ctl options" for a list of global command-line options (applies to all commands).
'''

GET_WORKFLOW_HELP = '''Get a workflow status

Examples:
  # Get the current status of a workflow
  opentf-ctl get workflow 9ea3be45-ee90-4135-b47f-e66e4f793383

  # Get the status of a workflow and wait until its completion
  opentf-ctl get workflow 9ea3be45-ee90-4135-b47f-e66e4f793383 --watch

  # Get the status of a workflow, showing first-level nested steps
  opentf-ctl get workflow 9ea3be45-ee90-4135-b47f-e66e4f793383 --step_depth=2

Options:
  --step-depth=1 or -s=1: show nested steps to the given depth.
  --job-depth=1 or -j=1: show nested jobs to the given depth.
  --max-command-length=15 or -c=15: show the first n characters of running commands.
  --watch or -w: wait until workflow completion or cancellation, displaying status updates as they occur.
  --output=format or -o format: show information in specified format (json or yaml).
    (more at: https://opentestfactory.org/tools/running-commands#output-formats)
  --selector=s or -l=s: selector (label query) to filter on, supports '=', '==', and '!='.  (e.g. -l key1=value1,key2=value2)
  --field-selector=s: selector (field query) to filter on, supports '=', '==', and '!='. (e.g. --field-selector key1=value1,key2=value2)
    (more at: https://opentestfactory.org/tools/running-commands#label-and-field-selectors)

Usage:
  opentf-ctl get workflow WORKFLOW_ID [--step_depth=value] [--job_depth=value] [--watch] [options]

Use "opentf-ctl options" for a list of global command-line options (applies to all commands).
'''

GET_WORKFLOWS_HELP = '''List active and recent workflows

Examples:
  # List the IDs of active and recent workflows
  opentf-ctl get workflows

  # Get the status of active and recent workflows
  opentf-ctl get workflows --output=wide

  # Get just the workflow IDs of active and recent workflows
  opentf-ctl get workflows --output=custom-columns=ID:.metadata.workflow_id

Options:
  --output={yaml,json} or -o {yaml,json}: show information as YAML or JSON.
  --output=wide or -o wide: show additional information.
  --output=custom-columns= or -o custom-columns=: show specified information.
    (more at: https://opentestfactory.org/tools/running-commands#output-formats)
  --selector=s or -l=s: selector (label query) to filter on, supports '=', '==', and '!='.  (e.g. -l key1=value1,key2=value2)
  --field-selector=s: selector (field query) to filter on, supports '=', '==', and '!='. (e.g. --field-selector key1=value1,key2=value2)
    (more at: https://opentestfactory.org/tools/running-commands#label-and-field-selectors)

Usage:
  opentf-ctl get workflows [--output=wide] [options]

Use "opentf-ctl options" for a list of global command-line options (applies to all commands).
'''

KILL_WORKFLOW_HELP = '''Kill a running workflow

Example:
  # Kill all workflows in namespace foo
  opentf-ctl kill workflow --field-selector=metadata.namespace==foo

  # Kill all running workflows
  opentf-ctl kill workflow --all

  # Kill the specified workflow
  opentf-ctl kill workflow 9ea3be45-ee90-4135-b47f-e66e4f793383

Options:
  --all: kill all running workflows
  --selector=s or -l=s: selector (label query) to filter on, supports '=', '==', and '!='.  (e.g. -l key1=value1,key2=value2)
  --field-selector=s: selector (field query) to filter on, supports '=', '==', and '!='. (e.g. --field-selector key1=value1,key2=value2)
    (more at: https://opentestfactory.org/tools/running-commands#label-and-field-selectors)

Usage:
  opentf-ctl kill|delete workflow (WORKFLOW_ID... | --selector label | --all) [options]

Use "opentf-ctl options" for a list of global command-line options (applies to all commands).
'''


########################################################################
# Helpers


def _file_not_found(name: str, err: Any) -> NoReturn:
    _error('File not found: %s.', name)
    _debug('Error is: %s.', err)
    sys.exit(2)


def _read_variables_file(file: str, variables: Dict[str, str]) -> None:
    """Read file and add variables.

    Abort with an error code 2 if the file does not exist or contains
    invalid content.
    """
    try:
        with open(file, 'r', encoding='utf-8') as varfile:
            for line in varfile:
                if '=' not in line:
                    _error(
                        'Invalid format in file %s, was expecting var=value.',
                        file,
                    )
                    sys.exit(2)
                var, _, value = line.strip().partition('=')
                variables[var] = value
    except FileNotFoundError as err:
        _file_not_found(file, err)


def _add_files(args: List[str], files: Dict[str, Any]) -> None:
    """Handling -f file command-line options."""
    process = False
    for option in args:
        if option == '-f':
            process = True
            continue
        if option.startswith('-f='):
            process = True
            option = option[3:]
        if process:
            process = False
            name, path = option.split('=')
            try:
                files[name] = open(path, 'rb')
            except FileNotFoundError as err:
                _file_not_found(path, err)


def _add_variables(args: List[str], files: Dict[str, Any]) -> None:
    """Handling -e file and -e var=value command-line options."""
    # OPENTF_CONFIG and OPENTF_TOKEN are explicitly excluded to prevent
    # unexpected leak
    variables = {
        key[len(AUTOVARIABLES_PREFIX) :]: value
        for key, value in os.environ.items()
        if key.startswith(AUTOVARIABLES_PREFIX)
        and key not in ('OPENTF_CONFIG', 'OPENTF_TOKEN')
    }
    process = False
    for option in args:
        if option == '-e':
            process = True
            continue
        if option.startswith('-e='):
            process = True
            option = option[3:]
        if process:
            process = False
            if '=' in option:
                var, _, value = option.partition('=')
                variables[var] = value
            else:
                _read_variables_file(option, variables)
    if variables:
        files['variables'] = '\n'.join(f'{k}={v}' for k, v in variables.items())


def _get_workflow_manifest(what: Iterable[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """Return workflow manifest.

    # Required parameters

    - what: a collection of messages.

    # Returned value

    If manifest is not found in `what`, returns `None`.
    """
    for manifest in what:
        if manifest.get('kind') == 'Workflow':
            return manifest
    return None


def _get_manifests(workflows_ids) -> Iterable[Dict[str, Any]]:
    for workflow_id in workflows_ids:
        response = _get_first_page(workflow_id)
        if response.status_code == 200:
            wf = _get_workflow_manifest(response.json()['details']['items'])
            if wf:
                wf['status'] = {'phase': response.json()['details']['status']}
            else:
                wf = {'metadata': {'workflow_id': workflow_id}}
            yield wf
        else:
            print(workflow_id, 'got response code', response.status_code)


def _handle_maybe_outdated(response) -> NoReturn:
    if response.status_code in (404, 405):
        _error('Could not get workflows list.  Maybe an outdated orchestrator version.')
        _debug('(Return code was %d.)', response.status_code)
    else:
        _error(
            'Could not get workflows list.  Return code was %d.',
            response.status_code,
        )
    sys.exit(2)


def _get_workflows(params: Optional[Dict[str, Any]] = None) -> List[str]:
    response = _get(
        _observer(),
        '/workflows',
        'Could not get workflows list',
        handler=_handle_maybe_outdated,
        params=params,
        raw=True,
    )
    if params and not response.headers.get('X-Processed-Query'):
        _error(
            'The orchestrator does not support selectors, please specify explicit workflow IDs or upgrade your orchestrator.'
        )
        sys.exit(2)
    try:
        result = response.json()
    except Exception as err:
        _error('Could not get workflows list: %s.', err)
        sys.exit(2)
    return result['details']['items']


def list_workflows() -> None:
    """List active and recent workflows."""
    generate_output(
        list(_get_manifests(_get_workflows(_make_params_from_selectors()))),
        DEFAULT_COLUMNS,
        WIDE_COLUMNS,
    )


def _handle_maybe_details(response) -> NoReturn:
    _error(response.json()['message'])
    if response.json().get('details'):
        _error(response.json()['details'].get('error'))
    sys.exit(1)


def run_workflow(workflow_name: str) -> None:
    """Run a workflow.

    # Required parameters

    - workflow_name: a file name

    # Returned value

    Returns the workflow ID if everything was OK.

    # Raised exceptions

    Abort with an error code of 1 if the workflow was not properly
    received by the orchestrator.

    Abort with an error code of 2 if a parameter was invalid (file not
    found or invalid format).
    """
    try:
        files = {'workflow': open(workflow_name, 'r', encoding='utf-8')}
        _add_files(sys.argv[1:], files)
        _add_variables(sys.argv[1:], files)

        ns = _get_arg('--namespace=') or _get_arg('-n=') or CONFIG.get('namespace')
        result = _post(
            _receptionist(),
            '/workflows' + (f'?namespace={ns}' if ns is not None else ''),
            files=files,
            statuses=(201,),
            handler=_handle_maybe_details,
        )
        if not isinstance(result, dict):
            _error(
                'Internal error: was expecting a dictionary, got a %s while querying /workflows.',
                result.__class__,
            )
            sys.exit(2)
        print('Workflow', result['details']['workflow_id'], 'is running.')
    except FileNotFoundError as err:
        _file_not_found(workflow_name, err)
    except Exception as err:
        _error('Could not start workflow: %s.', err)
        sys.exit(2)

    if '--wait' in sys.argv or '--watch' in sys.argv or '-w' in sys.argv:
        url = (
            _observer()
            + f'/workflows/{result["details"]["workflow_id"]}/status?per_page=1'
        )
        params = _make_params_from_selectors()
        sleep(WAIT_WARMUP_DELAY)
        try:
            while (
                _get(url, params=params, handler=lambda _: False, raw=True).status_code
                != 200
            ):
                sleep(WAIT_DELAY)
            get_workflow(result['details']['workflow_id'], watch=True)
        except Exception as err:
            _error('Could not show workflow execution result: %s.', err)
            sys.exit(2)


def _emit_prefix(event: Dict[str, Any], file=sys.stdout) -> None:
    cts = event['metadata'].get('creationTimestamp')
    job_id = event['metadata'].get('job_id')
    print(
        f'[{cts[:19] if cts else "":19}]',
        f'[job {job_id}] ' if job_id else '',
        end='',
        file=file,
    )


def _emit_command(
    event: Dict[str, Any],
    silent: bool,
    namespace: Optional[str] = None,
    max_command_length: Optional[int] = MAX_COMMAND_LENGTH,
    file=sys.stdout,
) -> None:
    if event['metadata']['step_sequence_id'] == -1:
        _emit_prefix(event, file)
        print(
            'Requesting execution environment providing',
            event['runs-on'],
            'for job' if namespace is None else f"in namespace '{namespace}' for job",
            repr(event['metadata']['name']),
            file=file,
        )
    elif event['metadata']['step_sequence_id'] == -2:
        _emit_prefix(event, file)
        print(
            'Releasing execution environment for job',
            repr(event['metadata']['name']),
            file=file,
        )
    elif not silent:
        _emit_prefix(event, file)
        print(' ' * (len(event['metadata'].get('step_origin', []))), end='', file=file)
        if len(event['scripts']):
            command = event['scripts'][0]
            if max_command_length is not None and len(command) > max_command_length:
                command = command[:max_command_length] + '...'
        else:
            command = 'None'
        print('Running command:', command, file=file)


def _emit_notification(event: Dict[str, Any], silent: bool, file=sys.stdout) -> None:
    if '--show-notifications' not in sys.argv and '-a' not in sys.argv:
        return
    if 'spec' in event and 'logs' in event['spec']:
        verbosity = ('-v' in sys.argv) or ('--verbose' in sys.argv)
        for log in event['spec']['logs']:
            if TIMESTAMP_PATTERN.match(log):
                log = log[26:]
            if (
                log.startswith('[DEBUG]')
                or log.startswith('DEBUG')
                or '] DEBUG in' in log
            ):
                if silent or not verbosity:
                    continue
            _emit_prefix(event, file=file)
            if event['metadata']['name'] != 'log notification':
                print(f'[{event["metadata"]["name"]}] {log}', file=file)
            else:
                print(log, file=file)


def _emit_result(event: Dict[str, Any], silent: bool, file=sys.stdout) -> None:
    for item in event.get('logs', []):
        _emit_prefix(event, file)
        print(item.rstrip(), file=file)
    if event['status'] == 0 or silent:
        return
    _emit_prefix(event, file)
    print('Status code was:', event['status'], file=file)


def _emit_executionerror(event: Dict[str, Any], file) -> None:
    _emit_prefix(event, file)
    if details := event.get('details'):
        if 'error' in details:
            print('ERROR:', details['error'], flush=True, file=file)
        else:
            print('ERROR: An ExecutionError occurred:', flush=True, file=file)
            for key, val in details.items():
                print(f'{key}: {val}', flush=True, file=file)
    else:
        print(f'An ExecutionError occurred: {event}', flush=True, file=file)


def emit_event(
    kind: str,
    event: Dict[str, Any],
    step_depth: int,
    job_depth: int,
    output_format: Optional[str],
    first: bool,
    namespace: Optional[str],
    max_command_length: Optional[int] = MAX_COMMAND_LENGTH,
    file=sys.stdout,
) -> None:
    """Emit event.

    # Required parameters

    - kind: a string, the event kind (`Workflow`, ...)
    - event: a dictionary
    - step_depth: an integer (0 = infinite details)
    - job_depth: an integer (0 = infinite details)
    - output_format: a string or None (`json`, `yaml`, or None)
    - first: a boolean
    - namespace: a string or None

    # Optional parameters

    - file: a stream
    """
    if output_format == 'json':
        if first:
            print('    ', end='', file=file)
        else:
            print(',\n    ', end='', file=file)
        print(
            '    '.join(json.dumps(event, indent=2).splitlines(keepends=True)),
            end='',
            file=file,
        )
        return
    if output_format == 'yaml':
        print('- ', end='', file=file)
        print(
            '  '.join(yaml.safe_dump(event).splitlines(keepends=True)),
            end='',
            file=file,
        )
        return

    if kind == 'Workflow':
        print('Workflow', event['metadata']['name'], flush=True, file=file)
        if namespace is not None:
            print(f"(running in namespace '{namespace}')", file=file)
        return
    if kind not in WATCHED_EVENTS:
        return
    if kind == 'ExecutionError':
        _emit_executionerror(event, file)
        return

    silent = False
    if job_depth and len(event['metadata'].get('job_origin', [])) >= job_depth:
        silent = True
    elif step_depth and len(event['metadata'].get('step_origin', [])) >= step_depth:
        silent = True

    if kind == 'ExecutionResult':
        _emit_result(event, silent, file)
    elif kind == 'ExecutionCommand':
        _emit_command(event, silent, namespace, max_command_length, file)
    elif kind == 'Notification':
        _emit_notification(event, silent, file)
    elif not silent:
        _emit_prefix(event, file)
        print(' ' * (len(event['metadata'].get('step_origin', []))), end='', file=file)
        print('Running function', event['metadata']['name'], flush=True, file=file)


def _get_first_page(workflow_id: str, params=None):
    """Return a requests.Response, to get following pages if needed."""

    def _handler_unknown_workflowid(response):
        if response.status_code == 404:
            _error(
                'Could not find workflow %s.  The ID is incorrect or too recent or too old.',
                workflow_id,
            )
            sys.exit(1)
        _error(
            'Could not get workflow %s.  Got status code %d (%s).',
            workflow_id,
            response.status_code,
            response.text,
        )
        sys.exit(1)

    return _get(
        _observer(),
        f'/workflows/{workflow_id}/status',
        params=params,
        handler=_handler_unknown_workflowid,
        raw=True,
    )


def _get_outputformat(allowed: Iterable[str]) -> Optional[str]:
    """Ensure the specified format, if any, is in the allowed set."""
    output_format = _get_arg('--output=') or _get_arg('-o=')
    if '-o' in sys.argv and not output_format:
        _error('Missing value for option "-o" (was expecting %s).', ', '.join(allowed))
        sys.exit(-2)
    if output_format is not None and output_format not in allowed:
        _error(
            'Unexpected output format specified: %s (was expecting %s).',
            output_format,
            ', '.join(allowed),
        )
        sys.exit(2)
    return output_format


def _get_workflow_events(workflow_id: str, watch: bool) -> Iterable[Dict[str, Any]]:
    """Yield events.

    If `watch` is True, yields events as they come, til the workflow
    completes.  Otherwise, yields events from the currently available
    page(s).
    """
    current_item = 0
    response = _get_first_page(workflow_id, _make_params_from_selectors())
    current_page = _observer() + f'/workflows/{workflow_id}/status'
    params = _make_params_from_selectors()

    while True:
        status = response.json()
        for event in status['details']['items'][current_item:]:
            yield event

        if 'next' in response.links:
            current_item = 0
            if (
                CONFIG.get('orchestrator', {})
                .get('services', {})
                .get('observer', {})
                .get('force-base-url', False)
            ):
                current_page = (
                    _observer()
                    + f'/workflows/{workflow_id}/status?'
                    + response.links['next']['url'].partition('?')[2]
                )
            else:
                current_page = response.links['next']['url']
            response = _get(current_page, raw=True)
            continue

        if not watch:
            break
        if response.json()['details']['status'] != 'RUNNING':
            break

        current_item = len(status['details']['items'])
        while len(status['details']['items']) <= current_item:
            sleep(REFRESH_DELAY)
            response = _get(current_page, params=params, raw=True)
            status = response.json()
            if len(status['details']['items']) != current_item:
                break
            if 'next' in response.links:
                break
            if current_item == 0 and len(status['details']['items']) == 0:
                _warning(f'Could not find items matching selectors: {params}')
                break


def _get_detailsoptions() -> Tuple[int, int, Optional[int]]:
    """Read output details options.

    If the details options are invalid, abort with an error code 2.

    Command lines parameters win over configuration file.  If neither
    are provided, defaults to 1 for job depth and step depth, and
    MAX_COMMAND_LENGTH for max command lenght.

    # Returned value

    A tuple of three integers: job_depth, step_depth, and
    max_command_length.
    """
    job_depth = _get_arg('--job-depth=') or _get_arg('-j=') or CONFIG.get('job-depth')
    if job_depth is None:
        job_depth = 1
    try:
        job_depth = int(job_depth)
    except ValueError:
        _error(f'--job-depth must be an integer.  Got: {job_depth}.')
        sys.exit(2)
    step_depth = (
        _get_arg('--step-depth=') or _get_arg('-s=') or CONFIG.get('step-depth')
    )
    if step_depth is None:
        step_depth = 1
    try:
        step_depth = int(step_depth)
    except ValueError:
        _error(f'--step-depth must be an integer.  Got: {step_depth}.')
        sys.exit(2)
    max_command_length = (
        _get_arg('--max-command-length=')
        or _get_arg('-c=')
        or CONFIG.get('max-command-length')
    )
    if max_command_length is None:
        max_command_length = MAX_COMMAND_LENGTH
    try:
        max_command_length = int(max_command_length) or None
    except ValueError:
        _error(f'--max-command-length must be an integer.  Got: {max_command_length}.')
        sys.exit(2)
    return job_depth, step_depth, max_command_length


def get_workflow(workflow_id: str, watch=False) -> None:
    """Get a workflow.

    # Required parameters

    - workflow_id: a string

    # Optional parameters

    - watch: a boolean (False by default)

    # Returned value

    None.

    # Raised exceptions

    Abort with an error code 1 if the workflow could not be found on the
    orchestrator.

    Abort with an error code 2 if another error occurred.
    """
    workflow_id = _ensure_uuid(workflow_id, _get_workflows)

    job_depth, step_depth, max_command_length = _get_detailsoptions()
    output_format = _get_outputformat(allowed=('yaml', 'json'))

    if output_format == 'json':
        print('{\n  "items": [')
    elif output_format == 'yaml':
        print('items:')

    first = True
    namespace = None
    cancelation_event = None
    try:
        for event in _get_workflow_events(workflow_id, watch):
            kind = event.get('kind', 'None')
            if kind == 'WorkflowCanceled':
                cancelation_event = event
            if kind == 'Workflow':
                namespace = event['metadata'].get('namespace')
            emit_event(
                kind,
                event,
                job_depth=job_depth,
                step_depth=step_depth,
                output_format=output_format,
                first=first,
                namespace=namespace,
                max_command_length=max_command_length,
            )
            first = False
    except KeyboardInterrupt:
        print('^C')
        sys.exit(1)
    except BrokenPipeError:
        _error('BrokenPipeError: [Errno 32] Broken pipe')
        sys.exit(1)

    status = _get_first_page(workflow_id, _make_params_from_selectors()).json()

    if output_format == 'json':
        print('\n  ],\n  "status":', json.dumps(status['details']['status']))
        print('}')
        return
    if output_format == 'yaml':
        yaml.safe_dump({'status': status['details']['status']}, sys.stdout)
        return

    workflow_status = status['details']['status']
    if workflow_status == 'DONE':
        print('Workflow completed successfully.')
    elif workflow_status == 'RUNNING':
        print('Workflow is running.')
    elif workflow_status == 'FAILED':
        if (
            cancelation_event
            and cancelation_event.get('details', {}).get('status') == 'cancelled'
        ):
            print('Workflow cancelled.')
        else:
            print('Workflow failed.')
    else:
        _warning(
            'Unexpected workflow status: %s (was expecting DONE, RUNNING, or FAILED).',
            workflow_status,
        )


def delete_workflow(workflow_ids: List[str]) -> None:
    """Kill workflow.

    # Required parameter

    - workflow_ids: a possibly empty list of strings (UUIDs)

    # Raised exceptions

    Abort with an error code 1 if the orchestrator replied with an
    unexpected status code (!= 200).

    Abort with an error code 2 if an error occurred while contacting the
    orchestrator.
    """

    def _notknown(response):
        if response.status_code == 404:
            _error(f'Workflow {workflow_id} is not known.')
        else:
            _error(f'Could not check if workflow {workflow_id} exists.')
        _error('Could not kill workflow.')
        sys.exit(1)

    workflow_ids = _ensure_either_uuids_or_selectors(
        workflow_ids, _get_workflows, {'fieldSelector': 'status.phase==RUNNING'}
    )
    for workflow_id in workflow_ids:
        workflow_id = _ensure_uuid(workflow_id, _get_workflows)

        _ = _get(_observer(), f'/workflows/{workflow_id}/status', handler=_notknown)
        _ = _delete(_killswitch(), f'/workflows/{workflow_id}')
        print(f'Killing workflow {workflow_id}.')


########################################################################
# Helpers


def print_workflow_help(args: List[str]):
    """Display help."""
    if _is_command('run workflow', args):
        print(RUN_WORKFLOW_HELP)
    elif _is_command(GETWORKFLOWS_COMMAND, args):
        print(GET_WORKFLOWS_HELP)
    elif _is_command('get workflow', args):
        print(GET_WORKFLOW_HELP)
    elif _is_command('kill workflow', args) or _is_command('delete workflow', args):
        print(KILL_WORKFLOW_HELP)
    else:
        _error('Unknown command.  Use --help to list known commands.')
        sys.exit(1)


def workflow_cmd():
    """Interact with workflows."""
    if _is_command(GETWORKFLOWS_COMMAND, sys.argv):
        _ensure_options(
            GETWORKFLOWS_COMMAND,
            sys.argv[1:],
            extra=[
                ('--output', '-o'),
                ('--selector', '-l'),
                ('--field-selector',),
            ],
        )
        read_configuration()
        list_workflows()
    elif _is_command(RUNWORKFLOW_COMMAND, sys.argv):
        workflow = _ensure_options(
            RUNWORKFLOW_COMMAND,
            sys.argv[1:],
            extra=[
                ('--step-depth', '-s'),
                ('--job-depth', '-j'),
                ('--max-command-length', '-c'),
                ('--namespace', '-n'),
                ('--selector', '-l'),
                ('--field-selector',),
            ],
            multi=[
                ('-e',),
                ('-f',),
            ],
            flags=[
                ('--wait', '--watch', '-w'),
                ('--show-notifications', '-a'),
                ('--verbose', '-v'),
            ],
        )
        read_configuration()
        run_workflow(workflow)
    elif _is_command(GETWORKFLOW_COMMAND, sys.argv):
        workflow_id = _ensure_options(
            GETWORKFLOW_COMMAND,
            sys.argv[1:],
            extra=[
                ('--step-depth', '-s'),
                ('--job-depth', '-j'),
                ('--max-command-length', '-c'),
                ('--output', '-o'),
                ('--selector', '-l'),
                ('--field-selector',),
            ],
            flags=[
                ('--watch', '-w'),
                ('--show-notifications', '-a'),
                ('--verbose', '-v'),
            ],
        )
        read_configuration()
        get_workflow(workflow_id, '--watch' in sys.argv or '-w' in sys.argv)
    elif _is_command(KILLWORKFLOW_COMMAND, sys.argv):
        workflow_ids = _ensure_options(
            KILLWORKFLOW_COMMAND,
            sys.argv[1:],
            extra=[
                ('--selector', '-l'),
                ('--field-selector',),
            ],
            flags=[('--all',)],
        )
        read_configuration()
        delete_workflow(workflow_ids)
    elif _is_command(DELETEWORKFLOW_COMMAND, sys.argv):
        workflow_ids = _ensure_options(
            DELETEWORKFLOW_COMMAND,
            sys.argv[1:],
            extra=[
                ('--selector', '-l'),
                ('--field-selector',),
            ],
            flags=[('--all',)],
        )
        read_configuration()
        delete_workflow(workflow_ids)
    else:
        _error('Unknown command.  Use --help to list known commands.')
        sys.exit(1)
