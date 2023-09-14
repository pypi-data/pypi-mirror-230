from datetime import datetime, timezone
import json
from typing import Dict, List
from unittest.mock import MagicMock, Mock, patch

from click import ClickException
import pytest

from anyscale.aws_iam_policies import ANYSCALE_IAM_POLICIES, AnyscaleIAMPolicy
from anyscale.cli_logger import CloudSetupLogger
from anyscale.client.openapi_client.models import Cloud
from anyscale.utils.cloud_update_utils import (
    add_missing_parameters_to_template_body,
    detect_drift,
    is_template_policy_documents_up_to_date,
    merge_parameters,
    update_cloudformation_stack,
)


def get_mock_cloud():
    mock_cloud = Cloud(
        id="cloud_id_1",
        name="cloud_name_1",
        provider="AWS",
        region="us-west-2",
        credentials="credentials",
        creator_id="creator_id",
        type="PUBLIC",
        created_at=datetime.now(timezone.utc),
        config="",
        state="ACTIVE",
        is_bring_your_own_resource=False,
    )
    return mock_cloud


@pytest.mark.parametrize(
    ("mock_parameter_list", "expected_result"),
    [
        pytest.param([], False, id="no_parameters"),
        pytest.param(
            [
                {
                    "ParameterKey": policy.parameter_key,
                    "ParameterValue": policy.policy_document,
                }
                for policy in ANYSCALE_IAM_POLICIES
            ],
            True,
            id="up_to_date",
        ),
        pytest.param(
            [
                {
                    "ParameterKey": policy.parameter_key,
                    "ParameterValue": policy.policy_document + "extra",
                }
                for policy in ANYSCALE_IAM_POLICIES
            ],
            False,
            id="not_up_to_date",
        ),
    ],
)
def test_is_template_policy_documents_up_to_date(mock_parameter_list, expected_result):
    assert (
        is_template_policy_documents_up_to_date(mock_parameter_list) == expected_result
    )


@pytest.mark.parametrize(
    ("detection_failed", "timeout"),
    [
        pytest.param(True, False, id="detection_failed"),
        pytest.param(False, True, id="timeout"),
    ],
)
def test_detect_drift(detection_failed: bool, timeout: bool):
    # we don't use moto here since moto doesn't support drift detection
    mock_id = "mock_id"
    mock_describe_stack_drift_detection_status = Mock(
        return_value={"DetectionStatus": "DETECTION_COMPLETE",}
    )
    mock_detection_failed_reason = "mock"
    if detection_failed:
        mock_describe_stack_drift_detection_status = Mock(
            return_value={
                "DetectionStatus": "DETECTION_FAILED",
                "DetectionStatusReason": mock_detection_failed_reason,
            }
        )
    elif timeout:
        mock_describe_stack_drift_detection_status = Mock(
            return_value={"DetectionStatus": "DETECTION_IN_PROGRESS",}
        )
    mock_drifts = Mock()
    mock_cfn_client = MagicMock(
        detect_stack_drift=Mock(return_value={"StackDriftDetectionId": mock_id}),
        describe_stack_drift_detection_status=mock_describe_stack_drift_detection_status,
        describe_stack_resource_drifts=Mock(
            return_value={"StackResourceDrifts": mock_drifts}
        ),
    )
    with patch.multiple(
        "anyscale.utils.cloud_update_utils",
        _client=Mock(return_value=mock_cfn_client),
        DETECT_DRIFT_TIMEOUT_SECONDS=1,
    ):
        if not detection_failed and not timeout:
            assert detect_drift(Mock(), Mock(), CloudSetupLogger()) == mock_drifts
        else:
            with pytest.raises(ClickException) as e:
                detect_drift(Mock(), Mock(), CloudSetupLogger())
            if detection_failed:
                assert e.match(mock_detection_failed_reason)
            elif timeout:
                e.match("timeout")


def _get_cloudformation_template_and_parameters():
    cfn_template_body = """Description: This template creates the resources necessary for an anyscale cloud.
Transform: AWS::LanguageExtensions
Parameters:
  AnyscaleCrossAccountIAMRoleName:
    Description: Name of the cross account IAM role.
    Type: String

  AnyscaleCrossAccountIAMPolicySteadyState:
    Description: Stead state IAM policy document
    Type: String

  AnyscaleCrossAccountIAMPolicyServiceSteadyState:
    Description: Stead state IAM policy document for services
    Type: String

  AnyscaleCrossAccountIAMPolicyInitialRun:
    Description: Initial run IAM policy document
    Type: String

Resources:
  customerRole:
    Type: 'AWS::IAM::Role'
    Properties:
      RoleName: !Ref AnyscaleCrossAccountIAMRoleName
      AssumeRolePolicyDocument:
        Statement:
          - Action: 'sts:AssumeRole'
            Effect: Allow
            Principal:
              AWS: 525325868955
            Sid: 'AnyscaleControlPlaneAssumeRole'
        Version: 2012-10-17
      Path: /

  IAMPermissionEC2SteadyState:
    Type: AWS::IAM::Policy
    Properties:
      PolicyDocument: !Ref AnyscaleCrossAccountIAMPolicySteadyState
      PolicyName: Anyscale_IAM_Policy_Steady_State
      Roles:
        - !Ref customerRole

  IAMPermissionServiceSteadyState:
    Type: AWS::IAM::Policy
    Properties:
      PolicyDocument: !Ref AnyscaleCrossAccountIAMPolicyServiceSteadyState
      PolicyName: Anyscale_IAM_Policy_Service_Steady_State
      Roles:
        - !Ref customerRole

  IAMPermissionEC2InitialRun:
    Type: AWS::IAM::Policy
    Properties:
      PolicyDocument: !Ref AnyscaleCrossAccountIAMPolicyInitialRun
      PolicyName: Anyscale_IAM_Policy_Initial_Setup
      Roles:
        - !Ref customerRole
"""
    mock_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "IAM",
                "Effect": "Allow",
                "Action": ["iam:PassRole", "iam:GetInstanceProfile"],
                "Resource": "*",
            },
        ],
    }
    parameters = [
        {
            "ParameterKey": "AnyscaleCrossAccountIAMRoleName",
            "ParameterValue": "anyscale-iam-role",
        },
        {
            "ParameterKey": "AnyscaleCrossAccountIAMPolicySteadyState",
            "ParameterValue": json.dumps(mock_policy),
        },
        {
            "ParameterKey": "AnyscaleCrossAccountIAMPolicyServiceSteadyState",
            "ParameterValue": json.dumps(mock_policy),
        },
        {
            "ParameterKey": "AnyscaleCrossAccountIAMPolicyInitialRun",
            "ParameterValue": json.dumps(mock_policy),
        },
    ]
    return cfn_template_body, parameters


@pytest.mark.parametrize(
    (
        "create_change_set_error",
        "create_change_set_timeout",
        "update_stack_error",
        "update_stack_timeout",
    ),
    [
        pytest.param(True, False, False, False, id="create_change_set_error"),
        pytest.param(False, True, False, False, id="create_change_set_timeout"),
        pytest.param(False, False, True, False, id="update_stack_error"),
        pytest.param(False, False, False, True, id="update_stack_timeout"),
        pytest.param(False, False, False, False, id="happy-path"),
    ],
)
def test_update_cloudformation_stack(
    create_change_set_error,
    create_change_set_timeout,
    update_stack_error,
    update_stack_timeout,
):
    mock_stack_name = "mock_stack_name"
    mock_region = "mock_region"
    mock_change_set_id = "mock_change_set_id"
    mock_template_body, mock_parameters = _get_cloudformation_template_and_parameters()
    mock_change_set = {
        "Status": "CREATE_COMPLETE",
        "StackId": "mock_stack_id",
    }
    if create_change_set_error:
        mock_change_set = {
            "Status": "FAILED",
            "StatusReason": "mock_status_reason",
        }
    elif create_change_set_timeout:
        mock_change_set = {
            "Status": "CREATE_IN_PROGRESS",
        }
    mock_stacks = {
        "Stacks": [{"StackName": mock_stack_name, "StackStatus": "UPDATE_COMPLETE",}]
    }
    if update_stack_error:
        mock_stacks["Stacks"][0]["StackStatus"] = "UPDATE_ROLLBACK_COMPLETE"
    elif update_stack_timeout:
        mock_stacks["Stacks"][0]["StackStatus"] = "UPDATE_IN_PROGRESS"

    mock_cfn_client = MagicMock(
        get_template=Mock(return_value={"TemplateBody": mock_template_body}),
        create_change_set=Mock(return_value={"Id": mock_change_set_id}),
        describe_change_set=Mock(return_value=mock_change_set),
        delete_change_set=Mock(),
        execute_change_set=Mock(),
        describe_stacks=Mock(return_value=mock_stacks),
    )
    with patch.multiple(
        "anyscale.utils.cloud_update_utils",
        _client=Mock(return_value=mock_cfn_client),
        CREATE_CHANGE_SET_TIMEOUT_SECONDS=1,
        UPDATE_CLOUDFORMATION_STACK_TIMEOUT_SECONDS=1,
    ):
        if (
            create_change_set_error
            or create_change_set_timeout
            or update_stack_error
            or update_stack_timeout
        ):
            with pytest.raises(ClickException) as e:
                update_cloudformation_stack(
                    mock_stack_name,
                    mock_parameters,
                    mock_region,
                    CloudSetupLogger(),
                    True,
                )
            if create_change_set_error:
                assert e.match("Failed to create change set")
                mock_cfn_client.delete_change_set.assert_called_once_with(
                    ChangeSetName=mock_change_set_id
                )
                mock_cfn_client.execute_change_set.assert_not_called()
            elif create_change_set_timeout:
                assert e.match("Timeout when creating change set")
                mock_cfn_client.execute_change_set.assert_not_called()
            elif update_stack_error:
                assert e.match("Failed to execute change set")
                mock_cfn_client.execute_change_set.assert_called_once_with(
                    ChangeSetName=mock_change_set_id
                )
            elif update_stack_timeout:
                assert e.match("Timeout when executing change set")
                mock_cfn_client.execute_change_set.assert_called_once_with(
                    ChangeSetName=mock_change_set_id
                )
        else:
            update_cloudformation_stack(
                mock_stack_name, mock_parameters, mock_region, CloudSetupLogger(), True,
            )


@pytest.mark.parametrize(
    ("existing_parameters", "parameters_to_update", "expected_merged_parameters"),
    [
        pytest.param(
            [
                {"ParameterKey": "key1", "ParameterValue": "value1"},
                {"ParameterKey": "key2", "ParameterValue": "value2"},
            ],
            [
                {"ParameterKey": "key1", "ParameterValue": "value1"},
                {"ParameterKey": "key2", "ParameterValue": "newvalue2"},
            ],
            [
                {"ParameterKey": "key1", "ParameterValue": "value1"},
                {"ParameterKey": "key2", "ParameterValue": "newvalue2"},
            ],
        ),
        pytest.param(
            [
                {"ParameterKey": "key1", "ParameterValue": "value1"},
                {"ParameterKey": "key2", "ParameterValue": "value2"},
                {"ParameterKey": "key4", "ParameterValue": "value4"},
            ],
            [
                {"ParameterKey": "key1", "ParameterValue": "newvalue1"},
                {"ParameterKey": "key3", "ParameterValue": "newvalue3"},
            ],
            [
                {"ParameterKey": "key1", "ParameterValue": "newvalue1"},
                {"ParameterKey": "key2", "ParameterValue": "value2"},
                {"ParameterKey": "key4", "ParameterValue": "value4"},
                {"ParameterKey": "key3", "ParameterValue": "newvalue3"},
            ],
            id="missing_parameters",
        ),
    ],
)
def test_merge_parameters(
    existing_parameters: List[Dict],
    parameters_to_update: List[Dict],
    expected_merged_parameters: List[str],
):
    assert (
        merge_parameters(existing_parameters, parameters_to_update)
        == expected_merged_parameters
    )


def test_add_missing_parameters_to_template_body():
    mock_template_body, mock_parameters = _get_cloudformation_template_and_parameters()
    mock_new_policy = AnyscaleIAMPolicy(
        parameter_key="NewParameter",
        parameter_description="NewParameter description",
        resource_logical_id="NewParameterResource",
        policy_name="New_Parameter_Policy",
        policy_document='{"Version": "2012-10-17", "Statement": []}',
    )
    mock_parameters.append(
        {
            "ParameterKey": mock_new_policy.parameter_key,
            "ParameterValue": mock_new_policy.policy_document,
        }
    )
    with patch.multiple(
        "anyscale.utils.cloud_update_utils", ANYSCALE_IAM_POLICIES=[mock_new_policy]
    ):
        modified_template_body = add_missing_parameters_to_template_body(
            mock_template_body, ["NewParameter", "AnyscaleCLIVersion"]
        )
        assert (
            modified_template_body
            == f"""Description: This template creates the resources necessary for an anyscale cloud.
Transform: AWS::LanguageExtensions
Parameters:
  {mock_new_policy.parameter_key}:
    Description: {mock_new_policy.parameter_description}
    Type: String

  AnyscaleCLIVersion:
    Description: Anyscale CLI version
    Type: String

  AnyscaleCrossAccountIAMRoleName:
    Description: Name of the cross account IAM role.
    Type: String

  AnyscaleCrossAccountIAMPolicySteadyState:
    Description: Stead state IAM policy document
    Type: String

  AnyscaleCrossAccountIAMPolicyServiceSteadyState:
    Description: Stead state IAM policy document for services
    Type: String

  AnyscaleCrossAccountIAMPolicyInitialRun:
    Description: Initial run IAM policy document
    Type: String

Resources:
  {mock_new_policy.resource_logical_id}:
    Type: AWS::IAM::Policy
    Properties:
      PolicyDocument: !Ref {mock_new_policy.parameter_key}
      PolicyName: {mock_new_policy.policy_name}
      Roles:
        - !Ref customerRole

  customerRole:
    Type: 'AWS::IAM::Role'
    Properties:
      RoleName: !Ref AnyscaleCrossAccountIAMRoleName
      AssumeRolePolicyDocument:
        Statement:
          - Action: 'sts:AssumeRole'
            Effect: Allow
            Principal:
              AWS: 525325868955
            Sid: 'AnyscaleControlPlaneAssumeRole'
        Version: 2012-10-17
      Path: /

  IAMPermissionEC2SteadyState:
    Type: AWS::IAM::Policy
    Properties:
      PolicyDocument: !Ref AnyscaleCrossAccountIAMPolicySteadyState
      PolicyName: Anyscale_IAM_Policy_Steady_State
      Roles:
        - !Ref customerRole

  IAMPermissionServiceSteadyState:
    Type: AWS::IAM::Policy
    Properties:
      PolicyDocument: !Ref AnyscaleCrossAccountIAMPolicyServiceSteadyState
      PolicyName: Anyscale_IAM_Policy_Service_Steady_State
      Roles:
        - !Ref customerRole

  IAMPermissionEC2InitialRun:
    Type: AWS::IAM::Policy
    Properties:
      PolicyDocument: !Ref AnyscaleCrossAccountIAMPolicyInitialRun
      PolicyName: Anyscale_IAM_Policy_Initial_Setup
      Roles:
        - !Ref customerRole
"""
        )
