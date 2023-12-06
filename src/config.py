from dynaconf import Dynaconf

settings = Dynaconf(
    settings_files=["config/config.json"],
)
