###############################################################################
# (c) Copyright 2019 CERN for the benefit of the LHCb Collaboration           #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "LICENSE".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################

"""Test for Production Models"""

import os
import glob
import pytest
import yaml
from pathlib import Path

from LHCbDIRAC.ProductionManagementSystem.Utilities.Models import parse_obj
from LHCbDIRAC.ProductionManagementSystem.Utilities.ModelCompatibility import step_to_step_manager_dict

test_yamls_dir = os.path.dirname(__file__)
test_yamls = glob.glob("*.yaml", root_dir=test_yamls_dir)


@pytest.mark.parametrize(
    "yaml_to_test",
    [test_yamls_dir + "/" + test_yaml for test_yaml in test_yamls],
)
def test_models(yaml_to_test):
    p = Path(yaml_to_test)
    for pr in yaml.safe_load(p.read_text()):
        assert parse_obj(pr)


sprucing_expected_step_info = {
    "ApplicationName": "Moore",
    "ApplicationVersion": "v54r15",
    "CONDDB": "",
    "DDDB": "",
    "DQTag": "",
    "OptionFiles": '{"entrypoint": '
    '"Hlt2Conf.Sprucing_production:pass_spruce_production", '
    '"extra_options": {"input_raw_format": 0.5, "input_type": '
    '"RAW", "simulation": false, "data_type": "Upgrade", '
    '"geometry_version": "trunk", "conditions_version": "master", '
    '"compression": "ZSTD:1", "output_type": "ROOT", '
    '"input_process": "Hlt2", "process": "Spruce"}, "extra_args": '
    "[]}",
    "ExtraPackages": "",
    "ProcessingPass": "SprucingPass23",
    "StepName": "Passthrough sprucing",
    "isMulticore": "N",
    "Visible": "Y",
    "mcTCK": "",
    "Usable": "Yes",
    "SystemConfig": "",
}


@pytest.mark.parametrize(
    "yaml_to_test",
    [test_yamls_dir + "/" + test_yaml for test_yaml in test_yamls],
)
def test_step_to_step_manager_dict(yaml_to_test):
    p = Path(yaml_to_test)
    for pr in yaml.safe_load(p.read_text()):
        p = parse_obj(pr)
        for j, step in enumerate(p.steps, start=1):
            step_info = step_to_step_manager_dict(j, step)
            if step.processing_pass == "SprucingPass23":
                assert step_info["Step"] == sprucing_expected_step_info
                assert step_info["InputFileTypes"] == [
                    {"FileType": "MDF", "Visible": "Y"},
                ]
                assert step_info["OutputFileTypes"] == [
                    {"FileType": "SL.DST", "Visible": "N"},
                    {"FileType": "CHARM.DST", "Visible": "N"},
                    {"FileType": "B2CC.DST", "Visible": "N"},
                    {"FileType": "RD.DST", "Visible": "N"},
                    {"FileType": "BANDQ.DST", "Visible": "N"},
                    {"FileType": "QEE.DST", "Visible": "N"},
                    {"FileType": "B2OC.DST", "Visible": "N"},
                    {"FileType": "BNOC.DST", "Visible": "N"},
                ]
