"""Auxiliary functions for serving the web page.
"""

from flask import request

from ...core.files import dirContents
from .kernel import FEATURES


def getFormData(web):
    """Get form data.

    The TF browser user interacts with the web app by clicking and typing,
    as a result of which a HTML form gets filled in.
    This form as regularly submitted to the web server with a request
    for a new incarnation of the page: a response.

    The values that come with a request, must be peeled out of the form,
    and stored as logical values.

    Most of the data has a known function to the web server,
    but there is also a list of webapp dependent options.
    """

    form = {}

    form["resetForm"] = request.form.get("resetForm", "")
    submitter = request.form.get("submitter", "")
    form["submitter"] = submitter

    form["sec0"] = request.form.get("sec0", "")
    form["sec1"] = request.form.get("sec1", "")
    form["sec2"] = request.form.get("sec2", "")
    form["annoset"] = request.form.get("annoset", "")
    form["duannoset"] = request.form.get("duannoset", "")
    form["rannoset"] = request.form.get("rannoset", "")
    form["dannoset"] = request.form.get("dannoset", "")
    form["freqsort"] = request.form.get("freqsort", "")
    form["kindsort"] = request.form.get("kindsort", "")
    form["etxtsort"] = request.form.get("etxtsort", "")
    form["sfind"] = request.form.get("sfind", "")
    form["sfinderror"] = request.form.get("sfinderror", "")
    activeEntity = request.form.get("activeentity", "")
    form["activeentity"] = int(activeEntity) if activeEntity else None
    form["activekind"] = request.form.get("activekind", "")
    form["efind"] = request.form.get("efind", "")
    tokenStart = request.form.get("tokenstart", "")
    form["tokenstart"] = int(tokenStart) if tokenStart else None
    tokenEnd = request.form.get("tokenend", "")
    form["tokenend"] = int(tokenEnd) if tokenEnd else None
    valSelectProto = {feat: request.form.get(f"{feat}_select", "") for feat in FEATURES}
    valSelect = {}
    for (feat, valProto) in valSelectProto.items():
        valSelect[feat] = (
            set(valProto.split(","))
            if valProto
            else {"⌀"}
            if submitter == "lookupq"
            else set()
        )

    form["valselect"] = valSelect
    # eKindSelect
    eKindPButton = request.form.get("ekindpbutton", "")
    eIdPButton = request.form.get("eidpbutton", "")
    eKindXButton = request.form.get("ekindxbutton", "")
    eIdXButton = request.form.get("eidxbutton", "")
    eKindSave = request.form.get("ekindsave", "")
    eIdSave = request.form.get("eidsave", "")
    eKindV = request.form.get("ekindv", "")
    eIdV = request.form.get("eidv", "")
    savEKind = eKindV if eKindSave else eKindPButton
    savEId = eIdV if eIdSave else eIdPButton
    form["savEKind"] = savEKind
    form["savEId"] = savEId
    form["delEKind"] = eKindXButton
    form["delEId"] = eIdXButton
    form["scope"] = request.form.get("scope", "a")
    excludedTokens = request.form.get("excludedtokens", "")
    form["excludedTokens"] = (
        {int(t) for t in excludedTokens.split(",")} if excludedTokens else set()
    )

    return form


def annoSets(annoDir):
    """Get the existing annotation sets.

    Parameters
    ----------
    annoDir: string
        The directory under which the distinct annotation sets can be found.
        The names of these subdirectories are the names of the annotation sets.

    Returns
    -------
    set
        The annotation sets, sorted by name.
    """
    return set(dirContents(annoDir)[1])
