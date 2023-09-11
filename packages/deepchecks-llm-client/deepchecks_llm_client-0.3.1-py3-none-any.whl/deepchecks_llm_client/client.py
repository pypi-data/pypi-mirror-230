import logging
import typing as t

from deepchecks_llm_client.api import API
from deepchecks_llm_client.data_types import Tag, EnvType, AnnotationType, GoldenSetInteraction
from deepchecks_llm_client.openai_instrumentor import OpenAIInstrumentor
from deepchecks_llm_client.utils import handle_exceptions, set_verbosity

__all__ = ["dc_client", "DeepchecksLLMClient"]

logging.basicConfig()
logger = logging.getLogger(__name__)
init_logger = logging.Logger(__name__ + ".init")

DEFAULT_APP_NAME = 'DefaultApp'
DEFAULT_VERSION_NAME = '0.0.1'
DEFAULT_ENV_TYPE = EnvType.PROD


class DeepchecksLLMClient:
    def __init__(self):
        self.api: API = None
        self.instrumentor: OpenAIInstrumentor = None

    @handle_exceptions(init_logger)
    def init(self,
             host: str,
             api_token: str,
             app_name: str,
             version_name: str = DEFAULT_VERSION_NAME,
             env_type: EnvType = DEFAULT_ENV_TYPE,
             auto_collect: bool = True,
             init_verbose: bool = True,
             verbose: bool = False,
             log_level: int = logging.WARNING
             ):
        """
        Connect to Deepchecks LLM Server

        Parameters
        ==========
        host : str
            Deepchecks host to communicate with
        api_token : str
            Deepchecks API Token (can be generated from the UI)
        app_name : str
            Application name to connect to, if Application name does not exist
            SDK will create it automatically
        version_name : str, default='1.0.0'
            Version name to connect to inside the application,
            if Version name does not exist SDK will create it automatically,
        env_type : EnvType, default=EnvType.PROD
            could be EnvType.PROD (for 'Production') or EnvType.EVAL (for 'Evaluation')
        auto_collect : bool, default=True
            Auto collect calls to LLM Models
        init_verbose: bool, default=True
            Write log messages during the init phase and non-prod phases such as golden_set()
        verbose : bool, default=False
            Write log messages (by default we are in silence mode)
        log_level: int, default=logging.WARNING
            In case that verbose or init_verbose is True,
            this parameter will set SDK loggers logging level

        Returns
        =======
        None
        """
        logger.setLevel(log_level)
        set_verbosity(init_verbose, init_logger)
        set_verbosity(verbose, logger)

        if host is not None and api_token is not None:
            self.api = API.instantiate(host=host, token=api_token)
        else:
            raise ValueError('host/token parameters must be provided')

        if app_name is None:
            raise ValueError('app_name must be supplied')

        app = self.api.get_application(app_name)
        if not app:
            raise Exception(f'Application: "{app_name}", does not exist, please create it via the UI')

        self.app_name(app_name).version_name(version_name).env_type(env_type)

        self.instrumentor = None
        if auto_collect:
            self.instrumentor = OpenAIInstrumentor(self.api, verbose, log_level)
            self.instrumentor.perform_patch()

    @handle_exceptions(logger, return_self=True)
    def app_name(self, new_app_name: str):
        if self.api:
            self.api.app_name(new_app_name)
        return self

    @handle_exceptions(logger, return_self=True)
    def version_name(self, new_version_name: str):
        if self.api:
            self.api.version_name(new_version_name)
        return self

    @handle_exceptions(logger, return_self=True)
    def env_type(self, new_env_type: EnvType):
        if self.api:
            self.api.env_type(new_env_type)
        return self

    @handle_exceptions(logger)
    def set_tags(self, tags: t.Dict[Tag, str]):
        if self.api:
            self.api.set_tags(tags)

    @handle_exceptions(logger)
    def annotate(self, ext_interaction_id: str, annotation: AnnotationType):
        if self.api:
            self.api.annotate(ext_interaction_id, annotation)

    @handle_exceptions(logger)
    def log_interaction(self,
                        user_input: str,
                        model_response: str,
                        full_prompt: str = None,
                        information_retrieval: str = None,
                        annotation: AnnotationType = None,
                        ext_interaction_id: str = None):
        if self.api:
            self.api.log_interaction(user_input=user_input, model_response=model_response,
                                     full_prompt=full_prompt, information_retrieval=information_retrieval,
                                     annotation=annotation, ext_interaction_id=ext_interaction_id)

    @handle_exceptions(init_logger)
    def golden_set(self, version_name: str | None = None) -> t.Iterable[GoldenSetInteraction]:
        """
        Fetch all that interactions from the golden set (EnvType.EVAL)

        Parameters
        ----------
        version_name : str
            version name to fetch interactions from, if no version name was supplied
            the latest created version in the application will be used (mostly useful
            when integrating the golden set rerun in the CI)

        Returns
        -------
        Iterable collection of interactions

        """
        if not self.api:
            raise Exception("dc_client was not initialized correctly, please re-create it")

        golden_set_version = self._get_golden_set_version(version_name)

        offset = 0
        limit = 20

        while True:
            interactions = self.api.get_interactions(golden_set_version["id"], limit=limit, offset=offset)
            for interaction in interactions:
                yield GoldenSetInteraction(id=interaction["id"],
                                           ext_interaction_id=interaction.get("ext_interaction_id"),
                                           user_input=interaction["input"]["data"] if interaction.get("input") else None,
                                           information_retrieval=interaction["information_retrieval"]["data"] if interaction.get("information_retrieval") else None,
                                           full_prompt=interaction["prompt"]["data"] if interaction.get("prompt") else None,
                                           response=interaction["response"]["data"] if interaction.get("response") else None,
                                           created_at=interaction["created_at"])

            # If the size of the data is less than the limit, we've reached the end
            if len(interactions) < limit:
                break

            offset += limit

    @handle_exceptions(init_logger)
    def golden_set_generation_completed(self):
        """
        This function indicate deepchecks that golden set generation completed
        It helps to finalize golden set related actions, for instance: train topics
        model and extract topics (the model will be used later on to extract topics
        from production data)

        Returns
        -------
        None

        """
        if not self.api:
            raise Exception("dc_client was not initialized correctly, please re-create it")

        self.api.generate_topics()

    def _get_golden_set_version(self, version_name):

        app = self.api.get_application(self.api.get_app_name())
        if not app:
            raise Exception(f"Application: '{self.api.get_app_name()}', does not exist")
        if version_name:
            golden_set_version = next((ver for ver in app["versions"] if ver["name"] == version_name), None)
            if not golden_set_version:
                raise Exception(f"Could not find version '{version_name}', in application '{self.api.get_app_name()}'")
        else:
            golden_set_version = max(app["versions"], key=lambda x: x['created_at'])
            if not golden_set_version:
                raise Exception(f"Could not find versions to select from in application '{self.api.get_app_name()}'")
        return golden_set_version


# LLM Client publicly accessed singleton
dc_client: DeepchecksLLMClient = DeepchecksLLMClient()


