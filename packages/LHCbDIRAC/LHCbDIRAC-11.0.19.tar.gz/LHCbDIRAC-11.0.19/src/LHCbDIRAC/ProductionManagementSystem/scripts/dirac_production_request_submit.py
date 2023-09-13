#!/usr/bin/env python
###############################################################################
# (c) Copyright 2022 CERN for the benefit of the LHCb Collaboration           #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "LICENSE".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################
"""Create production requests from a YAML document"""
import json
import yaml

from pathlib import Path
from prompt_toolkit import prompt, HTML
from prompt_toolkit.validation import Validator, ValidationError
from typing import Optional


from DIRAC import gLogger, exit as DIRACExit
from DIRAC.Core.Base.Script import Script
from DIRAC.Core.Utilities.ReturnValues import convertToReturnValue, returnValueOrRaise
from DIRAC.Core.Security.ProxyInfo import getProxyInfo

from LHCbDIRAC.ProductionManagementSystem.Utilities.Models import parse_obj, ProductionBase


def parseArgs():
    doSubmit = False
    createFiletypes = False
    outputFilename: Path | None = None

    @convertToReturnValue
    def enableSubmit(_):
        nonlocal doSubmit
        doSubmit = True

    @convertToReturnValue
    def enableCreateFiletypes(_):
        nonlocal createFiletypes
        createFiletypes = True

    @convertToReturnValue
    def setOutputFilename(filename):
        nonlocal outputFilename
        outputFilename = Path(filename)

    switches = [
        ("", "submit", "Actually create steps and submit productions", enableSubmit),
        ("", "create-filetypes", "Create missing file types", enableCreateFiletypes),
        ("", "output-json=", "Write the production IDs to a JSON file", setOutputFilename),
    ]
    Script.registerSwitches(switches)
    Script.registerArgument("yaml_path: Path to the YAML file containing productions to submit")
    Script.parseCommandLine(ignoreErrors=False)
    (yaml_path,) = Script.getPositionalArgs()
    return Path(yaml_path), doSubmit, createFiletypes, outputFilename


@Script()
def main():
    yamlPath, doSubmit, createFiletypes, outputFilename = parseArgs()

    productionRequests = [parse_obj(spec) for spec in yaml.safe_load(yamlPath.read_text())]
    productionIDs = submitProductionRequests(productionRequests, dryRun=not doSubmit, createFiletypes=createFiletypes)
    if productionIDs and outputFilename:
        outputFilename.write_text(json.dumps(productionIDs))
    if not doSubmit:
        gLogger.always('This was a dry run! Pass "--submit" to actually submit production requests.')


def submitProductionRequests(
    productionRequests: list[ProductionBase], *, dryRun=True, createFiletypes
) -> dict[int, list[int]]:
    """Submit a collection of production requests

    :param productionRequests: List of production requests to submit
    :param dryRun: Set to False to actually submit the production requests
    """
    from LHCbDIRAC.BookkeepingSystem.Client.BookkeepingClient import BookkeepingClient
    from LHCbDIRAC.ProductionManagementSystem.Utilities.ModelCompatibility import retValToListOfDict

    # Register filetypes
    requiredFileTypes = set()
    for prod in productionRequests:
        for step in prod.steps:
            requiredFileTypes |= {x.type for x in step.input}
            requiredFileTypes |= {x.type for x in step.output}
    knownFileTypes = {x["FileType"] for x in retValToListOfDict(BookkeepingClient().getAvailableFileTypes())}
    if missingFileTypes := requiredFileTypes - knownFileTypes:
        if not createFiletypes:
            raise NotImplementedError(f"Unknown file types that need to be registered: {missingFileTypes!r}")
        if not dryRun:
            for missingFileType in missingFileTypes:
                returnValueOrRaise(BookkeepingClient().insertFileTypes(missingFileType.upper(), "", "1"))

    # Create steps and submit production requests
    productionIDs = {}
    for i, prod in enumerate(productionRequests, start=1):
        gLogger.always("Considering production", f"{i} of {len(productionRequests)}: {prod.name}")
        productionIDs.update(_submitProductionRequests(prod, dryRun=dryRun))
    return productionIDs


def _submitProductionRequests(prod: ProductionBase, *, dryRun=True) -> dict[int, list[int]]:
    from LHCbDIRAC.BookkeepingSystem.Client.BookkeepingClient import BookkeepingClient
    from LHCbDIRAC.ProductionManagementSystem.Client.ProductionRequestClient import ProductionRequestClient
    from LHCbDIRAC.ProductionManagementSystem.Utilities.Models import ProductionStates
    from LHCbDIRAC.ProductionManagementSystem.Utilities.ModelCompatibility import (
        find_step_id,
        make_subprod_legacy_dict,
        production_to_legacy_dict,
        step_to_step_manager_dict,
    )

    prc = ProductionRequestClient()

    for j, step in enumerate(prod.steps, start=1):
        step.id = find_step_id(j, step)
        if step.id is not None:
            gLogger.info(f"Step {j} of {len(prod.steps)}: Found existing step with ID {step.id=}")
            continue

        if step.application.nightly is not None:
            raise ValueError("Nightly builds cannot be used for submitted productions")

        step_info = step_to_step_manager_dict(j, step)
        gLogger.verbose("Running insertStep with", step_info)
        if not dryRun:
            step.id = returnValueOrRaise(BookkeepingClient().insertStep(step_info))
            gLogger.info(f"Step {j} of {len(prod.steps)}: Created step with ID {step.id=}")

    if prod.id is not None:
        raise RuntimeError(f"{prod.id} has already been submitted")
    request_info, sub_productions = production_to_legacy_dict(prod)

    if not dryRun:
        # adding author
        if not prod.author:
            res = getProxyInfo()
            if not res["OK"]:
                gLogger.error("Could not get proxy info", res["Message"])
                DIRACExit(1)
            prod.author = res["Value"]["username"]
        # adding who to inform
        if not prod.inform:
            inform = prompt(HTML("<b>Type a comma-separated list of users to inform (or none)</b> "), default="")
            if inform:
                prod.inform = [username.strip() for username in inform.split(",")]
        # adding priority
        if not prod.priority:
            priorities = ["1a", "1b", "2a", "2b"]

            class PriorityValidator(Validator):
                def validate(self, document):
                    text = document.text
                    if text and text not in priorities:
                        raise ValidationError(message="not a priority")

            prod.priority = prompt(
                HTML(f"<b>Choose a priority among {priorities}</b> "), default="2b", validator=PriorityValidator()
            )

        request_info, sub_productions = production_to_legacy_dict(prod)
        gLogger.verbose("Creating production request with", request_info)
        prod.id = returnValueOrRaise(prc.createProductionRequest(request_info))
        # adding conditions_id
        if not prod.input_dataset.conditions_id:
            prod.input_dataset.conditions_id = BookkeepingClient().getDataTakingConditionId(
                prod.input_dataset.conditions_description
            )

    sub_prod_ids = []
    for sub_prod in sub_productions:
        if prod.state != ProductionStates.NEW:
            raise RuntimeError("Can only add sub productions to productions in state 'New'")
        sub_prod_info = make_subprod_legacy_dict(sub_prod, prod.id)
        gLogger.verbose("Creating production sub request with", request_info)
        if not dryRun:
            sub_prod_id = returnValueOrRaise(prc.createProductionRequest(sub_prod_info))
            sub_prod_ids.append(sub_prod_id)

    prod.state = ProductionStates.SUBMITTED
    productionIDs = {}
    if not dryRun:
        returnValueOrRaise(prc.updateProductionRequest(prod.id, {"RequestState": prod.state.value}))
        gLogger.always(f"Submitted production {prod.id} with sub productions {sub_prod_ids}")
        productionIDs[prod.id] = sub_prod_ids
    return productionIDs


if __name__ == "__main__":
    main()
