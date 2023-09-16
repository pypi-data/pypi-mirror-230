import json
import re
import secrets
import time
from typing import Dict, List, Optional, Set

from botocore.exceptions import ClientError
from click import ClickException
from pydantic import BaseModel

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


CUSTOMER_DRIFTS_POLICY_NAME = "Customer_Drifts_Policy"


class PropertyDifference(BaseModel):
    """
    PropertyDifference is a field in the drift response.
    It describes the difference between the expected and actual value of a property.

    Example:
    {
        "DifferenceType": "NOT_EQUAL",
        "PropertyPath": "/Policies/0/PolicyDocument/Statement/0/Sid",
        "ExpectedValue": "AllowAnyScaleCLI",
        "ActualValue": "AllowAnyScaleCLI2"
    }

    We use the PropertyPath to recognize the drift type and identify the policy and statement.
    """

    DifferenceType: str
    PropertyPath: str
    ExpectedValue: Optional[str]
    ActualValue: Optional[str]

    def get_policy_number(self) -> Optional[int]:
        """
        Get the policy number from the PropertyPath.
        If the PropertyPath is not a policy path, return None.
        """
        match = re.search(r"\/Policies\/(\d+)", self.PropertyPath)
        if match is None:
            return None
        return int(match.group(1))

    def get_statement_number(self) -> Optional[int]:
        """
        Get the statement number from the PropertyPath.
        If the PropertyPath is not a statement path, return None.
        """
        match = re.search(r"\/Statement\/(\d+)", self.PropertyPath)
        if match is None:
            return None
        return int(match.group(1))

    def is_add_or_remove_statement(self) -> bool:
        """
        Check if the PropertyPath is a statement path
        and the difference type is ADD or REMOVE.
        """
        if (
            re.match(
                r"\/Policies\/(\d+)\/PolicyDocument\/Statement\/(\d+)$",
                self.PropertyPath,
            )
            is not None
        ):
            if self.DifferenceType == "ADD" or self.DifferenceType == "REMOVE":
                return True
            else:
                raise ClickException(f"Drift {self.json()} cannot be resolved.")
        return False


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


def extract_cross_account_iam_role_drift(drifts: List[Dict]) -> Optional[Dict]:
    """
    Check if the cross account IAM role is drifted.
    If so, return the drift information.
    """
    for drift in drifts:
        # TODO (congding): don't hardcode "customerRole"
        if (
            drift["ResourceType"] == "AWS::IAM::Role"
            and drift["LogicalResourceId"] == "customerRole"
            and drift["StackResourceDriftStatus"] != "IN_SYNC"
        ):
            return drift
    return None


def get_all_sids_from_policy(policy: Dict) -> List[str]:
    """
    Get all the SIDs from the policy.
    SIDs (Statement ID) are used to identify the statements.
    """
    sids: List[str] = []
    for statement in policy["PolicyDocument"]["Statement"]:
        if "Sid" in statement:
            sids.append(statement["Sid"])
        else:
            raise ClickException(
                f"Statement {statement} in policy {policy['PolicyName']} doesn't have a Sid."
            )
    return sids


def get_sids_to_remove(
    diffs: List[Dict], expected_policies: List[Dict],
) -> Dict[str, Set[str]]:
    """
    Get the SIDs from the drifted statements to remove from the expected policies.
    """
    policy_names_to_overwrite = [policy.policy_name for policy in ANYSCALE_IAM_POLICIES]

    sids_to_remove: Dict[str, Set[str]] = {}

    for raw_diff in diffs:
        diff = PropertyDifference(**raw_diff)
        policy_number = diff.get_policy_number()
        if policy_number is None:
            # We'll skip the drift if it's not a policy drift
            # We only update the maintained inline policies
            # If there're other drifts (e.g., AssumeRolePolicyDocument drift)
            # we'll skip them and keep the drifts as is.
            continue
        try:
            policy_name = expected_policies[policy_number]["PolicyName"]
        except IndexError:
            continue
        if policy_name not in policy_names_to_overwrite:
            # Not a policy we care about
            # We only update the maintained inline policies
            # If the drifts are on other policies (e.g., newly created inline policies),
            # we'll skip them and keep the drifts as is.
            continue

        # Drift detected on a maintained policy
        statement_number = diff.get_statement_number()
        if statement_number is None:
            raise ClickException(
                f"Drift {diff} in policy {policy_name} cannot be resolved."
            )
        if diff.is_add_or_remove_statement():
            # Policy statement added or removed
            # No need to append to the drifted policy
            continue
        expected_statements = expected_policies[policy_number]["PolicyDocument"][
            "Statement"
        ]
        try:
            sid = expected_statements[statement_number]["Sid"]
            if policy_name not in sids_to_remove:
                sids_to_remove[policy_name] = set()
            sids_to_remove[policy_name].add(sid)
        except IndexError:
            continue

    return sids_to_remove


def generate_drifted_statements_to_append(
    actual_policies: List[Dict], undrifted_sid: Dict[str, Set[str]]
) -> List[Dict]:
    """
    Generate the drifted statements to append to the drifted policy.

    Iterate through the actual policies and skip the undrifted statements.
    For the drifted statements, we'll append them to the drifted statements list.

    """
    no_sid_cnt = 0
    sid_suffix = str(secrets.token_hex(4))
    drifted_statements: List[Dict] = []

    for actual_policy in actual_policies:
        policy_name = actual_policy["PolicyName"]
        if policy_name not in undrifted_sid:
            # Not a policy we care about
            continue
        statements = actual_policy["PolicyDocument"]["Statement"]
        for statement in statements:
            sid = statement.get("Sid", None)
            if sid is None:
                # No sid in the statement
                # Generate a new sid
                statement["Sid"] = f"Drifted{no_sid_cnt}{sid_suffix}"
                no_sid_cnt += 1
                drifted_statements.append(statement)
            elif sid not in undrifted_sid[policy_name]:
                # drifted statement
                statement["Sid"] = f"{statement['Sid']}Drifted{sid_suffix}"
                drifted_statements.append(statement)

    return drifted_statements


def get_all_sids(expected_policies) -> Dict[str, Set[str]]:
    all_sids: Dict[str, Set[str]] = {}
    policies_to_overwrite = [policy.policy_name for policy in ANYSCALE_IAM_POLICIES]
    for policy in expected_policies:
        if policy["PolicyName"] not in policies_to_overwrite:
            continue
        if policy["PolicyDocument"]["Version"] != "2012-10-17":
            raise ClickException(
                f"Unexpected policy version {policy['PolicyDocument']['Version']} for policy {policy['PolicyName']}"
            )
        all_sids[policy["PolicyName"]] = set(get_all_sids_from_policy(policy))
    return all_sids


def extract_drifted_statements(drift: Dict) -> List[Dict]:  # noqa: PLR0912
    """
    Extract the drifted statements from the role drift information.

    1) About SID (Statement ID):
    Each inline policy contains a list of statements, and each statement has a SID (Statement ID).
    We use the SID to identify the statements.
    Anyscale-maintained policies is guaranteed to have a SID for each statement.

    2) Get drifted statements:
    Step 1: Get all the SIDs from the expected policies.
    Step 2: Leverage the drift detection result to identify the drifted statements.
    If there's a drift on a statement, we will add it to a set of SIDs to remove.
    Step 3: Remove the drifted SIDs and get a set of undrifted SIDs.
    Step 4: Get all the statements from the actual policy and filter out the undrfited SIDs.
    """
    # Get all sids from expected policies
    expected_policies = json.loads(drift["ExpectedProperties"])["Policies"]
    all_sids = get_all_sids(expected_policies)

    # Remove drifted statements
    diffs = drift["PropertyDifferences"]
    sids_to_remove = get_sids_to_remove(diffs, expected_policies)

    undrifted_sid: Dict[str, Set[str]] = {}
    for policy_name, sids in all_sids.items():
        if policy_name not in sids_to_remove:
            undrifted_sid[policy_name] = sids
            continue
        undrifted_sid[policy_name] = sids.difference(sids_to_remove[policy_name])

    # Get drifted statements
    actual_policies = json.loads(drift["ActualProperties"])["Policies"]
    drifted_statements = generate_drifted_statements_to_append(
        actual_policies, undrifted_sid
    )

    return drifted_statements


def append_statements_to_customer_drifts_policy(
    region: str, role_name: str, statements: List[Dict]
):
    """
    Append statements to the customer drfits policy.
    If the inline policy doesn't exist, create it.
    """
    iam = _client("iam", region)
    policy_document = None
    try:
        policy = iam.get_role_policy(
            RoleName=role_name, PolicyName=CUSTOMER_DRIFTS_POLICY_NAME,
        )
        policy_document = policy["PolicyDocument"]
    except ClientError as e:
        if e.response["Error"]["Code"] != "NoSuchEntity":
            raise e
    # Create the policy
    if policy_document is None:
        policy_document = {
            "Version": "2012-10-17",
            "Statement": [],
        }

    # Append new statements
    for statement in statements:
        policy_document["Statement"].append(statement)  # type: ignore
    try:
        iam.put_role_policy(
            RoleName=role_name,
            PolicyName=CUSTOMER_DRIFTS_POLICY_NAME,
            PolicyDocument=json.dumps(policy_document),
        )
    except ClientError as e:
        raise ClickException(
            f"Failed to append statements to the drifted policy. Error: {e}"
        )


class DriftHandler:
    def __init__(self, region: str, logger: CloudSetupLogger):
        self.region = region
        self.logger = logger

    def detect_drift(self, stack_name: str) -> List[Dict]:
        """
        Detect drifts on cloudformation stack.
        More about drifts on cfn stack: https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-stack-drift.html
        """
        cfn_client = _client("cloudformation", self.region)

        with self.logger.spinner("Detecting drift on cloudformation stack..."):
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
                    self.logger.info("Drift detection completed.")
                    return drifts
                elif response["DetectionStatus"] == "DETECTION_FAILED":
                    raise ClickException(
                        f'Drift detection failed. Error: {response["DetectionStatusReason"]}'
                    )
        raise ClickException("Drift detection timeout. Please try again later.")

    def resolve_drift(self, drift: Dict):
        """
        Resolve the drift on the cross account IAM role.

        1) Drifts we care about:
        We only resolve the drifts on the Anyscale-maintained inline policies (defined in ANYSCALE_IAM_POLICIES).
        For other drifts, we'll skip them and keep the drifts as is.

        2) How to resolve the drift:
        We first identify the drifted statements in the Anyscale-maintained inline policies from the drift detection response.
        Then we append the drifted statements to the Customer_Drifts_Policy of the cross account IAM role.
        The reason is that we'll overwrite the Anyscale-maintained inline policies and we don't want to lose the drifted statements.
        If the customer removes some of the statements, they'll need to remove it again manually.
        """
        try:
            drifted_statements = extract_drifted_statements(drift)
            if len(drifted_statements) == 0:
                self.logger.info("No drifted statements found.")
                return True
            role_name = drift["PhysicalResourceId"]
            append_statements_to_customer_drifts_policy(
                self.region, role_name, drifted_statements
            )
            self.logger.info(
                f"Drifted statements have been appended to the policy {CUSTOMER_DRIFTS_POLICY_NAME} of the role {role_name}."
            )
            return True
        except Exception as e:  # noqa: BLE001
            self.logger.error(f"Failed to resolve drift. Error: {e}")
            return False


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


def try_delete_customer_drifts_policy(cloud):
    iam_client = _client("iam", cloud.region)
    role_name = cloud.credentials.split("/")[-1]
    try:
        iam_client.delete_role_policy(
            RoleName=role_name, PolicyName=CUSTOMER_DRIFTS_POLICY_NAME
        )
    except ClientError as e:
        if e.response["Error"]["Code"] != "NoSuchEntity":
            raise ClickException(
                f"Failed to delete inline policy {CUSTOMER_DRIFTS_POLICY_NAME} in role {role_name}: {e}"
            )
