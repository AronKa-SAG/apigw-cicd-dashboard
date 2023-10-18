import json
import logging
import os
from pathlib import Path
import itertools
from unittest.mock import MagicMock, patch
import pytest
from utilities.connection.ApigwUtil import ApigwUtil
from utilities.adaptBuildEnvironment import adaptBuildPreTest
from utilities.assets.Application import Application


##############################
# Testing function: check_for_same_alias_name
##############################
def create_alias_file(file_path: Path, alias_list: list):
    with open(file_path, "w") as f:
        json.dump(alias_list, f)
    return file_path

@pytest.mark.parametrize("global_alias_list, project_alias_list, expected_output", [
    ([{"alias": {"name": "alias1"}}], [{"alias": {"name": "alias1"}}], True),
    ([{"alias": {"name": "alias1"}}], [{"alias": {"name": "alias2"}}], False)
])
def test_check_for_same_alias_name(global_alias_list: list, project_alias_list: list, expected_output: bool):
    # Test 1: Both global and project alias files exist and contain matching aliases
    global_alias_file = create_alias_file(Path("global_aliases.json"), global_alias_list)
    project_alias_file = create_alias_file(Path("project_aliases.json"), project_alias_list)
    assert adaptBuildPreTest.check_for_same_alias_name(global_alias_file, project_alias_file) == expected_output
    
    # Clean up
    os.remove("global_aliases.json")
    os.remove("project_aliases.json")

def test_missing_file_check_for_same_alias_name():
    # Test 3: Global alias file does not exist
    global_alias_file = Path("non_existent_file.json")
    project_alias_list = [{"alias": {"name": "alias2"}}]
    project_alias_file = create_alias_file(Path("project_aliases.json"), project_alias_list)
    assert adaptBuildPreTest.check_for_same_alias_name(global_alias_file, project_alias_file) == False

    # Test 4: Project alias file does not exist
    global_alias_list = [{"alias": {"name": "alias1"}}]
    global_alias_file = create_alias_file(Path("global_aliases.json"), global_alias_list)
    project_alias_file = Path("non_existent_file.json")
    assert adaptBuildPreTest.check_for_same_alias_name(global_alias_file, project_alias_file) == False
    
    # Clean up
    os.remove("global_aliases.json")
    os.remove("project_aliases.json")


##############################
# Testing function: check_applications
##############################
def create_applications(app_names: list):
    return [Application({"name": name, "id": "test-id"}) for name in app_names]

@patch("utilities.connection.ApigwUtil")
def test_check_applications(mock_apigw_util):
    # Test 1: No applications found
    mock_apigw_util.get_assets.return_value = None
    apigw_connect = ApigwUtil()
    assert adaptBuildPreTest.check_applications(apigw_connect) == True

    # Test 2: All applications have valid names
    mock_apigw_util.get_assets.return_value = create_applications(["app_dev", "app_test", "app_qs", "app_prod"])
    apigw_connect = ApigwUtil()
    assert adaptBuildPreTest.check_applications(apigw_connect) == True

    # Test 3: One application has an invalid name
    mock_apigw_util.get_assets.return_value = create_applications(["app_dev", "app_test", "app_qs", "app_prod", "invalid_app"])
    apigw_connect = ApigwUtil()
    assert adaptBuildPreTest.check_applications(apigw_connect) == False