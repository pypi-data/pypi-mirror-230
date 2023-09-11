import dunamai as _dunamai
from . import (
    api,
    client,
    data_types,
    openai_instrumentor,
    utils
)

__version__ = _dunamai.get_version("deepchecks_llm_client",
                                   third_choice=_dunamai.Version.from_any_vcs).serialize(style=_dunamai.Style.Pep440)


