"""Main controller for Flask

This module contains the main controller that Flask invokes when serving
the annotation tool.
"""

import re

from flask import render_template

from ...core.files import initTree, annotateDir, dirCopy, dirMove, dirRemove, dirExists

from .servelib import getFormData, annoSets
from .kernel import loadData
from .tables import (
    composeE,
    composeS,
    composeQ,
    saveEntity,
    delEntity,
    filterS,
)
from .wrap import wrapAnnoSets, wrapEntityHeaders, wrapEntityFeats, wrapMessages


def serveNer(web):
    """Serves the NE annotation tool.

    Parameters
    ----------
    web: object
        The flask web app
    """

    web.console("START controller")
    aContext = web.context
    appName = aContext.appName.replace("/", " / ")

    kernelApi = web.kernelApi
    app = kernelApi.app
    api = app.api
    F = api.F
    slotType = F.otype.slotType

    annoDir = annotateDir(app, "ner")
    initTree(annoDir, fresh=False)
    sets = annoSets(annoDir)

    form = getFormData(web)
    resetForm = form["resetForm"]

    css = kernelApi.css()

    templateData = {}
    messages = []

    for (k, v) in form.items():
        if not resetForm or k not in templateData:
            templateData[k] = v

    valSelect = templateData["valselect"]
    chosenAnnoSet = templateData["annoset"]
    dupAnnoSet = templateData["duannoset"]
    renamedAnnoSet = templateData["rannoset"]
    deleteAnnoSet = templateData["dannoset"]

    if deleteAnnoSet:
        annoPath = f"{annoDir}/{deleteAnnoSet}"
        dirRemove(annoPath)
        if dirExists(annoPath):
            messages.append(("error", f"""Could not remove {deleteAnnoSet}"""))
        else:
            chosenAnnoSet = ""
            sets -= {deleteAnnoSet}
        templateData["dannoset"] = ""

    if dupAnnoSet and chosenAnnoSet:
        if not dirCopy(
            f"{annoDir}/{chosenAnnoSet}", f"{annoDir}/{dupAnnoSet}", noclobber=True
        ):
            messages.append(
                ("error", f"""Could not copy {chosenAnnoSet} to {dupAnnoSet}""")
            )
        else:
            sets = sets | {dupAnnoSet}
            chosenAnnoSet = dupAnnoSet
        templateData["duannoset"] = ""

    if renamedAnnoSet and chosenAnnoSet:
        if not dirMove(f"{annoDir}/{chosenAnnoSet}", f"{annoDir}/{renamedAnnoSet}"):
            messages.append(
                ("error", f"""Could not rename {chosenAnnoSet} to {renamedAnnoSet}""")
            )
        else:
            sets = (sets | {renamedAnnoSet}) - {chosenAnnoSet}
            chosenAnnoSet = renamedAnnoSet
        templateData["rannoset"] = ""

    if chosenAnnoSet and chosenAnnoSet not in sets:
        initTree(f"{annoDir}/{chosenAnnoSet}", fresh=False)
        sets |= {chosenAnnoSet}

    templateData["annoSets"] = wrapAnnoSets(annoDir, chosenAnnoSet, sets)

    web.annoSet = chosenAnnoSet

    loadData(web)

    sortKey = None
    sortDir = None

    for key in ("freqsort", "kindsort", "etxtsort"):
        currentState = templateData[key]
        if currentState:
            sortDir = "u" if currentState == "d" else "d"
            sortKey = key
            break

    sFind = templateData["sfind"]
    sFind = (sFind or "").strip()
    sFindRe = None
    errorMsg = ""

    if sFind:
        try:
            sFindRe = re.compile(sFind)
        except Exception as e:
            errorMsg = str(e)

    activeEntity = templateData["activeentity"]
    activeKind = templateData["activekind"]

    templateData["appName"] = appName
    templateData["slotType"] = slotType
    templateData["resetForm"] = ""
    tokenStart = templateData["tokenstart"]
    tokenEnd = templateData["tokenend"]
    scope = templateData["scope"]

    savEKind = templateData["savEKind"]
    savEId = templateData["savEId"]
    delEKind = templateData["delEKind"]

    excludedTokens = templateData["excludedTokens"]

    (sentences, nFind, nVisible, nEnt) = filterS(
        web, sFindRe, tokenStart, tokenEnd, valSelect
    )

    report = None

    if (savEKind or delEKind) and tokenStart and tokenEnd:
        saveSentences = (
            filterS(web, None, tokenStart, tokenEnd, valSelect)[0]
            if sFindRe and scope == "a"
            else sentences
        )
        if savEKind or delEKind:
            report = []

            if savEKind:
                report.append(saveEntity(web, savEKind, savEId, saveSentences, excludedTokens))
            if delEKind:
                report.append(delEntity(web, delEKind, saveSentences, excludedTokens))
            (sentences, nFind, nVisible, nEnt) = filterS(
                web, sFindRe, tokenStart, tokenEnd, valSelect
            )

    composeQ(
        web,
        templateData,
        sFind,
        sFindRe,
        errorMsg,
        valSelect,
        nFind,
        nEnt,
        nVisible,
        scope,
        report,
    )

    hasEntity = tokenStart and tokenEnd
    limited = not hasEntity

    templateData["entities"] = composeE(web, activeEntity, activeKind, sortKey, sortDir)
    templateData["entityfeats"] = wrapEntityFeats(web)
    templateData["entityheaders"] = wrapEntityHeaders(sortKey, sortDir)

    web.console("start compose sentences")
    templateData["sentences"] = composeS(web, sentences, limited, excludedTokens)
    web.console("end compose sentences")
    templateData["messages"] = wrapMessages(messages)
    messages = []

    result = render_template(
        "ner/index.html",
        css=css,
        **templateData,
    )
    web.console("END controller")
    with open("/Users/me/Downloads/test.html", "w") as fh:
        fh.write(result)
    return result
