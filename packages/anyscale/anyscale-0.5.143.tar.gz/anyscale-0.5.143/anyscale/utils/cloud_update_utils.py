import secrets
import time
from typing import Dict, List, Set

from click import ClickException

import anyscale
from anyscale.aws_iam_policies import (
    ANYSCALE_IAM_POLICIES,
    AnyscaleIAMPolicy,
)
from anyscale.cli_logger import CloudSetupLogger, pad_string
from anyscale.util import (
    _client,
    confirm,
    generate_inline_policy_parameter,
    generate_inline_policy_resource,
    get_anyscale_cross_account_iam_policies,
)


DETECT_DRIFT_TIMEOUT_SECONDS = 60 * 5  # 5 minutes
CREATE_CHANGE_SET_TIMEOUT_SECONDS = 60 * 5  # 5 minutes
UPDATE_CLOUDFORMATION_STACK_TIMEOUT_SECONDS = 60 * 5  # 5 minutes


def format_drifts(drifts: List[Dict]) -> str:
    padding_size = 40
    outputs: List[str] = []
    outputs.append(
        f'{pad_string("Resource Type", padding_size)}'
        f'{pad_string("Resource Id", padding_size)}'
        f'{pad_string("Drift status", padding_size)}'
    )
    outputs.append(
        f'{pad_string("-------------", padding_size)}'
        f'{pad_string("-----------", padding_size)}'
        f'{pad_string("------------", padding_size)}'
    )
    for drift in drifts:
        outputs.append(
            f'{pad_string(drift["ResourceType"], padding_size)}'
            f'{pad_string(drift["PhysicalResourceId"], padding_size)}'
            f'{pad_string(drift["StackResourceDriftStatus"], padding_size)}'
        )
    return "\n".join(outputs)


def is_template_policy_documents_up_to_date(template_parameters: List[Dict]) -> bool:
    """
    Check if the policy documents in the cfn template are up to date.
    """
    parameter_dict = {
        p["ParameterKey"]: p["ParameterValue"] for p in template_parameters
    }
    for policy in ANYSCALE_IAM_POLICIES:
        if policy.parameter_key not in parameter_dict:
            return False
        if parameter_dict[policy.parameter_key] != policy.policy_document:
            return False
    return True


def is_cross_account_iam_role_drifted(drifts: List[Dict]) -> bool:
    """
    Check if the cross account IAM role is drifted.
    """
    for drift in drifts:
        if (
            drift["ResourceType"] == "AWS::IAM::Role"
            and drift["LogicalResourceId"] == "customerRole"
            and drift["StackResourceDriftStatus"] != "IN_SYNC"
        ):
            return True
    return False


def detect_drift(stack_name: str, region: str, logger: CloudSetupLogger) -> List[Dict]:
    """
    Detect drifts on cloudformation stack.
    More about drifts on cfn stack: https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-stack-drift.html
    """
    cfn_client = _client("cloudformation", region)

    with logger.spinner("Detecting drift on cloudformation stack..."):
        # Init drift detection
        drift_detection_id = cfn_client.detect_stack_drift(StackName=stack_name)[
            "StackDriftDetectionId"
        ]

        # Polling drift detection status
        end_time = time.time() + DETECT_DRIFT_TIMEOUT_SECONDS
        while time.time() < end_time:
            time.sleep(1)
            response = cfn_client.describe_stack_drift_detection_status(
                StackDriftDetectionId=drift_detection_id
            )
            if response["DetectionStatus"] == "DETECTION_COMPLETE":
                drift_response = cfn_client.describe_stack_resource_drifts(
                    StackName=stack_name,
                    StackResourceDriftStatusFilters=[
                        "MODIFIED",
                        "DELETED",
                        "NOT_CHECKED",
                    ],
                )
                drifts = drift_response["StackResourceDrifts"]
                logger.info("Drift detection completed.")
                return drifts
            elif response["DetectionStatus"] == "DETECTION_FAILED":
                raise ClickException(
                    f'Drift detection failed. Error: {response["DetectionStatusReason"]}'
                )
    raise ClickException("Drift detection timeout. Please try again later.")


def merge_parameters(
    existing_parameters: List[Dict], parameters_to_update: List[Dict]
) -> List[Dict]:
    """
    Overwrite the existing parameters with the parameters to update.
    If the parameter to update does not exist in the existing parameters, add it to the existing parameters.

    The returned parameter list should contain all the combined parameters.
    """
    returned_parameters: Dict = {
        p["ParameterKey"]: p["ParameterValue"] for p in existing_parameters
    }
    for p in parameters_to_update:
        returned_parameters[p["ParameterKey"]] = p["ParameterValue"]
    return [
        {"ParameterKey": k, "ParameterValue": v} for k, v in returned_parameters.items()
    ]


def add_missing_parameters_to_template_body(
    template_body: str, missing_parameters: Set[str]
) -> str:
    """
    Add missing parameters to template body.

    For AnyscaleCLIVersion, we only need to add the parameter part.
    For other parameters for inline IAM policies, we need to add both parameter and resource definitions.
    """
    # Get all the missing parameters' policy information
    policy_dict: Dict[str, AnyscaleIAMPolicy] = {}
    for policy in ANYSCALE_IAM_POLICIES:
        if policy.parameter_key in missing_parameters:
            policy_dict[policy.parameter_key] = policy

    parameter_substitutions = ["Parameters:"]
    resource_substitutions = ["Resources:"]

    for parameter_key in missing_parameters:
        if parameter_key == "AnyscaleCLIVersion":
            parameter_substitutions.append(
                "  AnyscaleCLIVersion:\n    Description: Anyscale CLI version\n    Type: String\n"
            )
        else:
            policy = policy_dict[parameter_key]
            parameter_substitutions.append(
                generate_inline_policy_parameter(policy) + "\n"
            )
            resource_substitutions.append(
                generate_inline_policy_resource(policy) + "\n"
            )

    template_body = template_body.replace(
        "Parameters:", "\n".join(parameter_substitutions),
    )

    template_body = template_body.replace(
        "Resources:", "\n".join(resource_substitutions),
    )
    return template_body


def update_cloudformation_stack(
    stack_name: str,
    parameters: List[Dict],
    region: str,
    logger: CloudSetupLogger,
    yes: bool = False,
):
    cfn_client = _client("cloudformation", region)

    template_body = cfn_client.get_template(
        StackName=stack_name, TemplateStage="Original"
    )["TemplateBody"]

    # Get updated parameter list
    # We update the following 2 types of parameters:
    # 1. AnyscaleCLIVersion: the version of CLI
    # 2. Parameters that define the inline policy documents for the cross account IAM role
    # Other parameters should remain unchanged.
    updated_parameters: List[Dict] = get_anyscale_cross_account_iam_policies()
    updated_parameters.append(
        {"ParameterKey": "AnyscaleCLIVersion", "ParameterValue": anyscale.__version__}
    )

    missing_parameters: Set[str] = set(
        {p["ParameterKey"] for p in updated_parameters}
    ).difference(set({p["ParameterKey"] for p in parameters}))
    if len(missing_parameters) > 0:
        template_body = add_missing_parameters_to_template_body(
            template_body, missing_parameters
        )

    updated_parameters = merge_parameters(parameters, updated_parameters)

    # Create change set
    with logger.spinner("Creating change set for cloud update..."):
        response = cfn_client.create_change_set(
            StackName=stack_name,
            ChangeSetName=f"AnyscaleCloudUpdate{str(secrets.token_hex(4))}",
            TemplateBody=template_body,
            Parameters=updated_parameters,
            Capabilities=["CAPABILITY_NAMED_IAM", "CAPABILITY_AUTO_EXPAND"],
            ChangeSetType="UPDATE",
        )

        change_set_id = response["Id"]

        # Polling change set status
        end_time = time.time() + CREATE_CHANGE_SET_TIMEOUT_SECONDS
        while time.time() < end_time:
            time.sleep(1)
            response = cfn_client.describe_change_set(
                ChangeSetName=change_set_id, StackName=stack_name
            )
            if response["Status"] == "CREATE_COMPLETE":
                break
            elif response["Status"] == "FAILED":
                cfn_client.delete_change_set(ChangeSetName=change_set_id)
                raise ClickException(
                    f"Failed to create change set for cloud update. {response['StatusReason']}"
                )
        else:
            raise ClickException(
                "Timeout when creating change set for cloud update. Please try again later."
            )

    # Preview change set
    stack_id = response["StackId"]
    stack_url = f"https://{region}.console.aws.amazon.com/cloudformation/home?region={region}#/stacks/stackinfo?stackId={stack_id}"
    change_set_url = f"https://{region}.console.aws.amazon.com/cloudformation/home?region={region}#/stacks/changesets/changes?stackId={stack_id}&changeSetId={change_set_id}"
    logger.info(f"Change set created at {change_set_url}")
    confirm(
        "Please review the change set before updating the stack. Do you want to proceed with the update?",
        yes,
    )

    # Execute change set
    with logger.spinner("Executing change set for cloud update..."):
        response = cfn_client.execute_change_set(ChangeSetName=change_set_id)

        # Polling cfn stack status
        end_time = time.time() + UPDATE_CLOUDFORMATION_STACK_TIMEOUT_SECONDS
        while time.time() < end_time:
            time.sleep(1)
            response = cfn_client.describe_stacks(StackName=stack_name)
            stack = response["Stacks"][0]
            if stack["StackStatus"] == "UPDATE_COMPLETE":
                break
            elif stack["StackStatus"] == "UPDATE_ROLLBACK_COMPLETE":
                raise ClickException(
                    f"Failed to execute change set. Please check the cloudformation stack events for more details ({stack_url})"
                )
        else:
            raise ClickException(
                f"Timeout when executing change set. Please check the cloudformation stack events for more details ({stack_url})"
            )
