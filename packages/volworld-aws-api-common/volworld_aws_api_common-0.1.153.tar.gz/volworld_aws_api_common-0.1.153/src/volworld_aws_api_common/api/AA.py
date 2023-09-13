from typing import Final
from volworld_common.api.CA import CA


# ====== A: Attribute ======
class AA(CA):
    AppBar: Final[str] = "ab"

    BottomAppBar: Final[str] = "btmab"

    CheckBox: Final[str] = "chkbx"
    Circle: Final[str] = "cce"

    Dialog: Final[str] = "dlg"

    Editor: Final[str] = "edr"

    Filled: Final[str] = "fld"

    LearnerRefWf: Final[str] = "lwf"
    LearnerSaLogId: Final[str] = "lrsalid"
    Link: Final[str] = "lnk"
    Logout: Final[str] = "lgo"

    Memorized: Final[str] = "mmd"
    Menu: Final[str] = "mu"
    MoreActions: Final[str] = "mact"

    NextPage: Final[str] = "nxp"

    PreviousPage: Final[str] = "prp"

    QuestWfCycleId: Final[str] = "qwcid"
    QuestWfCycleElmId: Final[str] = "qwcelmId"

    Switch: Final[str] = "sth"

    To: Final[str] = "to"
    Token: Final[str] = "tk"

    WordIndexList: Final[str] = "windlst"
    WordLearningState: Final[str] = "wls"
    WordSimilarity: Final[str] = "wsmy"
    WordTags: Final[str] = "wtgs"

AAList = [AA, CA]
