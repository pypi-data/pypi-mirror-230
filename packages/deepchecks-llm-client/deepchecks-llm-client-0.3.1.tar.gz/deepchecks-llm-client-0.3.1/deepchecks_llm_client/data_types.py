import enum
import uuid
from dataclasses import dataclass

__all__ = ["Tag", "EnvType", "AnnotationType", "GoldenSetInteraction"]

from datetime import datetime


class Tag(str, enum.Enum):
    """
    Namespace for useful tags that deepchecks case use
    You can use `dc_client.set_tag()` to pass user tags to deepchecks

    USER_INPUT
        Relevant only for auto_collect=True, should contain the input as the user supply it

    INFORMATION_RETRIEVAL
        Relevant only for auto_collect=True, should contain the "information retrieval" if exist

    USER_ID
        The external user that used the AI model

    EXT_INTERACTION_ID
        An external unique id the user can set, this id can be used later on to annotate the interaction
        if EXT_INTERACTION_ID was not supplied by the user, deepchecks will try to capture openai response id
        (i.e. - {"id": <openai unique id>, ...} and will set it as the "ext_interaction_id" of the logged interaction
    """
    USER_INPUT = "user_input"
    INFORMATION_RETRIEVAL = "information_retrieval"
    USER_ID = "user_id"
    EXT_INTERACTION_ID = "ext_interaction_id"


class EnvType(str, enum.Enum):
    PROD = "PROD"
    EVAL = "EVAL"


class AnnotationType(str, enum.Enum):
    GOOD = "good"
    BAD = "bad"
    UNKNOWN = "unknown"


@dataclass
class GoldenSetInteraction:
    id: uuid.UUID
    ext_interaction_id: str
    user_input: str
    information_retrieval: str
    full_prompt: str
    response: str
    created_at: datetime


