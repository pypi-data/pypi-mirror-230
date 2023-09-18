import json
import click
import click_log
from base64 import b64decode
from re import search as regex_search

from convisoappsec.common.box import ContainerWrapper, convert_sarif_to_sastbox1
from convisoappsec.flow.graphql_api.beta.models.issues.iac import CreateIacFindingInput
from convisoappsec.flowcli import help_option
from convisoappsec.flowcli.common import (
    asset_id_option,
    on_http_error,
    project_code_option,
)
from convisoappsec.flowcli.context import pass_flow_context
from convisoappsec.logger import LOGGER

click_log.basic_config(LOGGER)


@click.command()
@click_log.simple_verbosity_option(LOGGER)
@project_code_option(
    help="Not required when --no-send-to-flow option is set",
    required=False
)
@asset_id_option(required=False)
@click.option(
    '-r',
    '--repository-dir',
    default=".",
    show_default=True,
    type=click.Path(
        exists=True,
        resolve_path=True,
    ),
    required=False,
    help="The source code repository directory.",
)
@click.option(
    "--send-to-flow/--no-send-to-flow",
    default=True,
    show_default=True,
    required=False,
    help="""Enable or disable the ability of send analysis result
    reports to flow. When --send-to-flow option is set the --project-code
    option is required""",
    hidden=True
)
@click.option(
    "--scanner-timeout",
    hidden=True,
    required=False,
    default=7200,
    type=int,
    help="Set timeout for each scanner"
)
@click.option(
    "--parallel-workers",
    hidden=True,
    required=False,
    default=2,
    type=int,
    help="Set max parallel workers"
)
@click.option(
    "--deploy-id",
    default=None,
    required=False,
    hidden=True,
    envvar=("CONVISO_DEPLOY_ID", "FLOW_DEPLOY_ID")
)
@help_option
@pass_flow_context
def run(
    flow_context,
    project_code,
    asset_id,
    repository_dir,
    send_to_flow,
    scanner_timeout,
    parallel_workers,
    deploy_id
):
    '''
      This command will perform IAC analysis at the source code. The analysis
      results can be reported or not to flow application.

    '''
    perform_command(
        flow_context,
        project_code,
        asset_id,
        repository_dir,
        send_to_flow,
        scanner_timeout,
        parallel_workers,
        deploy_id
    )

def deploy_results_to_conviso(
    conviso_api, results_filepaths, project_code, deploy_id, repository_dir, token, scanner_timeout):
    results_context = click.progressbar(
        results_filepaths, label="Sending SASTBox reports to Conviso Platform"
    )

    with results_context as reports:
        for report_name in reports:

            compatible_report_filepath = convert_sarif_to_sastbox1(
                report_name, repository_dir, token, scanner_timeout
            )

            with open(compatible_report_filepath) as report_file:
                conviso_api.findings.create(
                    project_code=project_code,
                    commit_refs=None,
                    finding_report_file=report_file,
                    default_report_type="sast",
                    deploy_id=deploy_id,
                )
    pass


def deploy_results_to_conviso_beta(
    conviso_api, results_filepaths, asset_id, deploy_id, repository_dir, token, scanner_timeout
):
    results_context = click.progressbar(
        results_filepaths, label="Sending SASTBox reports to Conviso Platform BETA"
    )

    with results_context as reports:
        for report_path in reports:

            compatible_report_filepath = convert_sarif_to_sastbox1(
                report_path, repository_dir, token, scanner_timeout
            )
            
            with open(compatible_report_filepath) as report_file:
                report_content = json.load(report_file)

                issues = report_content.get("issues", [])
                for issue in issues:
                    issue_model = CreateIacFindingInput(
                        asset_id=asset_id,
                        file_name=issue.get("filename"),
                        vulnerable_line=issue.get("line"),
                        title=issue.get("title"),
                        description=issue.get("description"),
                        severity=issue.get("severity"),
                        deploy_id=deploy_id,
                        code_snippet=parse_code_snippet(issue.get("evidence")),
                        reference=parse_conviso_references(issue.get("references")),
                        first_line=parse_first_line_number(issue.get("evidence")),
                    )

                    conviso_api.issues.create_iac(issue_model)
    pass

def perform_command(
    flow_context, project_code, asset_id, repository_dir, send_to_flow, scanner_timeout, parallel_workers, deploy_id
):
    
    if send_to_flow and not flow_context.experimental and not project_code:
        raise click.MissingParameter(
            "It is required when sending reports to Conviso Platform API.",
            param_type="option",
            param_hint="--project-code",
        )

    if send_to_flow and flow_context.experimental and not asset_id:
        raise click.MissingParameter(
            "It is required when sending reports to Conviso Platform using experimental API.",
            param_type="option",
            param_hint="--asset-id",
        )
    
    try:
        REQUIRED_CODEBASE_PATH = '/code'
        IAC_IMAGE_NAME = 'sastbox-iac-scanner-checkov'
        IAC_SCAN_FILENAME = '/{}.sarif'.format(IAC_IMAGE_NAME)
        containers_map = {
            IAC_IMAGE_NAME: {
                'repository_dir': repository_dir,
                'repository_name': IAC_IMAGE_NAME,
                'tag': 'latest',
                'command': [
                    '-v',
                    '--codebase', REQUIRED_CODEBASE_PATH,
                    '--output', IAC_SCAN_FILENAME
                ],
            },
        }

        LOGGER.info('\U0001F4AC Preparing Environment')
        conviso_rest_api = flow_context.create_conviso_rest_api_client()
        token = conviso_rest_api.docker_registry.get_sast_token()
        scanners_wrapper = ContainerWrapper(
            token=token,
            containers_map=containers_map,
            logger=LOGGER,
            timeout=scanner_timeout
        )

        LOGGER.info('\U0001F4AC Starting IaC')
        scanners_wrapper.run()

        results_filepaths = []#[str(r.results) for r in scanners_wrapper.scanners]
        for r in scanners_wrapper.scanners:
            report_filepath = r.results
            if report_filepath:
                 results_filepaths.append(report_filepath)

        LOGGER.info('\U0001F4AC Processing Results')
        if send_to_flow:
                    
            if flow_context.experimental:
                conviso_beta_api = flow_context.create_conviso_api_client_beta()

                deploy_results_to_conviso_beta(
                     conviso_beta_api,
                     results_filepaths,
                     asset_id,
                     deploy_id=deploy_id,
                     repository_dir=repository_dir,
                     token=token,
                     scanner_timeout=scanner_timeout
                )
            else:
                deploy_results_to_conviso(
                    conviso_rest_api,
                    results_filepaths,
                    project_code,
                    deploy_id,
                    repository_dir=repository_dir,
                    token=token,
                    scanner_timeout=scanner_timeout,
                )
        LOGGER.info('\U00002705 IaC Scan Finished')

    except Exception as e:
        on_http_error(e)
        raise click.ClickException(str(e)) from e


def parse_conviso_references(references=[]):
    DIVIDER = "\n"

    return DIVIDER.join(references)


def parse_code_snippet(encoded_base64):
    decoded_text = b64decode(encoded_base64).decode("utf-8")

    lines = decoded_text.split("\n")

    cleaned_lines = []
    for line in lines:
        cleaned_line = line.split(": ", 1)[-1]
        cleaned_lines.append(cleaned_line)

    code_snippet = "\n".join(cleaned_lines)

    return code_snippet


def parse_first_line_number(encoded_base64):
    decoded_text = b64decode(encoded_base64).decode("utf-8")

    regex = r"^(\d+):"

    result = regex_search(regex, decoded_text)

    if result and result.group(1):
        return result.group(1)

    LINE_NUMBER_WHEN_NOT_FOUND = 1
    return LINE_NUMBER_WHEN_NOT_FOUND

EPILOG = '''
Examples:

  \b
  1 - Reporting the results to Conviso Platform API:
    1.1 - Running an analysis at all commit range:
      $ export CONVISO_API_KEY='your-api-key'
      $ export CONVISO_PROJECT_CODE='your-project-code'
      $ {command}

'''  # noqa: E501

SHORT_HELP = "Perform Infrastructure Code analysis"

command = 'conviso iac run'
run.short_help = SHORT_HELP
run.epilog = EPILOG.format(
    command=command,
)
