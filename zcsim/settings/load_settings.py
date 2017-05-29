import os
import logging

#pylint: disable=import-error
import yaml

logger = logging.getLogger(__name__)


class SettingsCache:
    """ Caches settings loaded from disk """

    cached_settings = {}

    def __init__(self, settings_folder=os.path.dirname(os.path.abspath(__file__)),
                 default_config_filename="config"):
        """ Initialise with shared config settings

        Steps taken:

        1. Look for a file in `settings_folder` called `default_config_filename`
        and try to load from it. Save the results.

            settings = get_settings()

        This can then be used like a function which returns the settings without
        loading from the file repeatedly

        Args:
            settings_folder (str): Absolute path of settings files
            default_config_filename (str): base config filenames
        """

        self.settings_folder = settings_folder
        self.default_config_filename = default_config_filename

        self.loaded = False

    def load_from_disk(self, base_dir, environment):
        """ Load settings from disk """

        filename = "{:s}.yaml".format(environment)

        abs_path = os.path.join(base_dir, filename)

        logger.info("Reading from %s", abs_path)
        print("Reading settings from %s", abs_path)

        try:
            with open(abs_path) as s_file:
                vals = s_file.read()
                logger.info("Read from file: %s", vals)
                loaded = yaml.load(vals)
        except FileNotFoundError as e:
            logger.error("Unable to find settings file %r", e)
            # raise
            with open(abs_path, "w") as s_file:
                pass
            return self.load_from_disk(base_dir, environment)
        except IOError as e:
            logger.error("Unable to load from from %s", abs_path)
            raise
        except yaml.scanner.ScannerError as e:
            logger.error("Error in reading settings file (%s): %s", abs_path, e)
            raise

        if loaded:
            self.cached_settings.update(**loaded)
        else:
            logger.warning("Nothing in settings file")

        self.loaded = True

    def __call__(self):
        if not self.loaded:
            self.load_from_disk(self.settings_folder,
                                self.default_config_filename)

        return self.cached_settings


env = os.getenv("ZCSIM_ENV", "testing")
print("Got env: {}".format(env))
settings_filename = 'config_{:s}'.format(env)
get_settings = SettingsCache(default_config_filename=settings_filename)
