import base64
import copy
import json
import os
import secrets

from dynaconf import Dynaconf
import yaml

from truera.utils import service_utils


def _override_tenant_specific_config_if_present(config, tenant_id, logger):
    ailens_home_value = os.environ.get("AILENS_HOME", None)
    tenant_config_path = os.path.join(
        ailens_home_value, "config", "tenant_specific_config.yaml"
    )
    dynaconf_settings = Dynaconf(settings_files=[tenant_config_path])
    # reload fresh config for tenant id from source file
    tenant_config = dynaconf_settings.get(tenant_id, fresh=True)

    if tenant_config is not None:
        if logger:
            logger.info(
                "Loaded tenant-specific configurations: {}".
                format(tenant_config)
            )
        for key, value in tenant_config.items():
            # dynamic configs takes precedence over static ones
            if key in config:
                if isinstance(value, dict):
                    # If the value is a dictionary, update the nested dictionary recursively
                    nested_dict = config.setdefault(key, {})
                    if isinstance(nested_dict, dict):
                        nested_dict.update(value)
                else:
                    config[key] = value

    return config


def get_config_value(
    config, key1, key2, default=None, tenant_id=None, logger=None
):
    config = copy.deepcopy(config)  # avoid mutating default (static) config

    if tenant_id is not None:
        config = _override_tenant_specific_config_if_present(
            config, tenant_id, logger
        )

    if not key1 in config:
        return default
    inner_config = config[key1]
    if not key2:
        return inner_config
    if not key2 in inner_config:
        return default
    return inner_config[key2]


def get_config_value_arbitrary_depth(
    config, keys, default, tenant_id=None, logger=None
):
    config = copy.deepcopy(config)  # avoid mutating default (static) config

    if tenant_id is not None:
        config = _override_tenant_specific_config_if_present(
            config, tenant_id, logger
        )

    for key in keys:
        if not key in config:
            return default
        config = config[key]

    return config


def get_token_secret_and_algorithm(secret_file_path, *, logger=None):
    token_secret_file = os.path.expandvars(secret_file_path)

    jwt_encode_secret = None

    if os.path.isfile(token_secret_file):
        with open(token_secret_file, 'rb') as fp:
            jwt_encode_secret = base64.standard_b64decode(fp.read())
    else:
        msg = "Secret file does not exist, secret generated, but will not work upon restart."
        if logger:
            logger.warning(msg)
        else:
            print(msg)
        jwt_encode_secret = secrets.token_hex(512)
    jwt_token_algorithm = 'HS512'

    return jwt_encode_secret, jwt_token_algorithm


def read_config_file(file_path, buffer=None, print_result=True):
    service_utils.print_and_buffer(
        buffer, "Looking for configuration file: {}".format(file_path)
    )
    if (not os.path.exists(file_path)):
        raise ValueError("Config file not found")

    # TODO(apoorv) Replace with a typed config object.
    with open(file_path) as fp:
        config = yaml.safe_load(fp)

    if print_result:
        service_utils.print_and_buffer(buffer, json.dumps(config, indent=2))
    return config


def read_env_var(
    env_var_name,
    raise_if_missing=True,
    default=None,
    buffer=None,
    print_result=True
):
    env_var_value = os.environ.get(env_var_name, default)

    if not env_var_value and raise_if_missing:
        raise ValueError(
            "Cannot find required environment variable: [{}]".
            format(env_var_name)
        )
    if print_result:
        service_utils.print_and_buffer(
            buffer,
            "Env var {} has value {}".format(env_var_name, env_var_value)
        )
    return env_var_value


def get_artifactrepo_uri_path():
    return "/api/artifacts/artifactrepo"
