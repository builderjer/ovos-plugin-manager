from ovos_plugin_manager.utils import normalize_lang, load_plugin, \
    find_plugins, PluginTypes, PluginConfigTypes
from ovos_config import Configuration
from ovos_utils.log import LOG
from ovos_plugin_manager.templates.keywords import KeywordExtractor


def find_keyword_extract_plugins() -> dict:
    """
    Find all installed plugins
    @return: dict plugin names to entrypoints
    """
    return find_plugins(PluginTypes.KEYWORD_EXTRACTION)


def load_keyword_extract_plugin(module_name: str) -> type(KeywordExtractor):
    """
    Get an uninstantiated class for the requested module_name
    @param module_name: Plugin entrypoint name to load
    @return: Uninstantiated class
    """
    return load_plugin(module_name, PluginTypes.KEYWORD_EXTRACTION)


def get_keyword_extract_configs() -> dict:
    """
    Get valid plugin configurations by plugin name
    @return: dict plugin names to list of dict configurations
    """
    from ovos_plugin_manager.utils.config import load_configs_for_plugin_type
    return load_configs_for_plugin_type(PluginTypes.KEYWORD_EXTRACTION)


def get_keyword_extract_module_configs(module_name: str) -> dict:
    """
    Get valid configurations for the specified plugin
    @param module_name: plugin to get configuration for
    @return: dict configurations by language (if provided)
    """
    from ovos_plugin_manager.utils.config import load_plugin_configs
    return load_plugin_configs(module_name,
                               PluginConfigTypes.KEYWORD_EXTRACTION, True)


def get_keyword_extract_lang_configs(lang: str,
                                     include_dialects: bool = False) -> dict:
    """
    Get a dict of plugin names to list valid configurations for the requested
    lang.
    @param lang: Language to get configurations for
    @param include_dialects: consider configurations in different locales
    @return: dict {`plugin_name`: `valid_configs`]}
    """
    from ovos_plugin_manager.utils.config import get_plugin_language_configs
    return get_plugin_language_configs(PluginTypes.KEYWORD_EXTRACTION, lang,
                                       include_dialects)


def get_keyword_extract_supported_langs() -> dict:
    """
    Return a dict of plugin names to list supported languages
    @return: dict plugin names to list supported languages
    """
    from ovos_plugin_manager.utils.config import get_plugin_supported_languages
    return get_plugin_supported_languages(PluginTypes.KEYWORD_EXTRACTION)


def get_keyword_extract_config(config: dict = None) -> dict:
    """
    Get relevant configuration for factory methods
    @param config: global Configuration OR plugin class-specific configuration
    @return: plugin class-specific configuration
    """
    from ovos_plugin_manager.utils.config import get_plugin_config
    config = config or Configuration()
    return get_plugin_config(config, "keyword_extract")


class OVOSKeywordExtractorFactory:
    """ reads mycroft.conf and returns the globally configured plugin """
    MAPPINGS = {
        # default split at sentence boundaries
        # usually helpful in other plugins and included in base class
        "dummy": "ovos-keyword-plugin-dummy"
    }

    @staticmethod
    def get_class(config=None):
        """Factory method to get a KeywordExtractor engine class based on configuration.

        The configuration file ``mycroft.conf`` contains a ``keyword_extract`` section with
        the name of a KeywordExtractor module to be read by this method.

        "keyword_extract": {
            "module": <engine_name>
        }
        """
        config = get_keyword_extract_config(config)
        keyword_extract_module = config.get("module", "ovos-keyword-plugin-dummy")
        if keyword_extract_module in OVOSKeywordExtractorFactory.MAPPINGS:
            keyword_extract_module = OVOSKeywordExtractorFactory.MAPPINGS[keyword_extract_module]
        return load_keyword_extract_plugin(keyword_extract_module)

    @staticmethod
    def create(config=None):
        """Factory method to create a KeywordExtractor engine based on configuration.

        The configuration file ``mycroft.conf`` contains a ``keyword_extract`` section with
        the name of a KeywordExtractor module to be read by this method.

        "keyword_extract": {
            "module": <engine_name>
        }
        """
        config = config or get_keyword_extract_config()
        plugin = config.get("module") or "ovos-keyword-plugin-dummy"
        plugin_config = config.get(plugin) or {}
        try:
            clazz = OVOSKeywordExtractorFactory.get_class(config)
            return clazz(plugin_config)
        except Exception:
            LOG.exception(f'Keyword extraction plugin {plugin} '
                          f'could not be loaded!')
            return KeywordExtractor()
