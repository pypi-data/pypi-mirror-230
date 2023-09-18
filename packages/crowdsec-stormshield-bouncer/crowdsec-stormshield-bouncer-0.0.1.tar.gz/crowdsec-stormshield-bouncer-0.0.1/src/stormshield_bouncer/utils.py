import logging
import sys
from logging.handlers import RotatingFileHandler

from pytimeparse import parse as parse_time


class CustomFormatter(logging.Formatter):
    FORMATS = {
        logging.ERROR: "[%(asctime)s] %(levelname)s - %(message)s",
        logging.WARNING: "[%(asctime)s] %(levelname)s - %(message)s",
        logging.DEBUG: "[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)s - %(message)s",
        "DEFAULT": "[%(asctime)s] %(levelname)s - %(message)s",
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno, self.FORMATS["DEFAULT"])
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


logger = logging.getLogger("")
default_handler = logging.StreamHandler(sys.stdout)
default_formatter = CustomFormatter()
default_handler.setFormatter(default_formatter)
logger.addHandler(default_handler)
logger.setLevel(logging.INFO)


def get_log_level(log_level) -> int:
    log_level_by_str = {
        "debug": logging.DEBUG,
        "info": logging.INFO,
        "warning": logging.WARNING,
        "error": logging.ERROR,
    }
    if log_level not in log_level_by_str:
        raise ValueError(f"Invalid log level: {log_level}")
    return log_level_by_str[log_level.lower()]


def set_default_config(config):
    if not config.get("crowdsec"):
        config["crowdsec"] = {}

    if not config["crowdsec"].get("include_scenarios_containing"):
        config["crowdsec"]["include_scenarios_containing"] = []
    if not config["crowdsec"].get("exclude_scenarios_containing"):
        config["crowdsec"]["exclude_scenarios_containing"] = []
    if not config["crowdsec"].get("only_include_decisions_from"):
        config["crowdsec"]["only_include_decisions_from"] = []
    if not config["crowdsec"].get("update_frequency"):
        config["crowdsec"]["update_frequency"] = "30s"

    if not config.get("log_level"):
        config["log_level"] = "info"
    if not config.get("log_mode"):
        config["log_mode"] = "stdout"
    if not config.get("log_file") and config["log_mode"] == "file":
        config["log_file"] = "/var/log/crowdsec-stormshield-bouncer.log"
        logger.info(f"Logging to {config['log_file']}")

    return config


def validated_config(config):
    if not config["crowdsec"].get("lapi_url"):
        raise ValueError("crowdsec.lapi_url is not set")
    if not config["crowdsec"].get("lapi_key"):
        raise ValueError("crowdsec.lapi_key is not set")

    res = parse_time(config["crowdsec"]["update_frequency"])
    if not res:
        raise ValueError(
            "crowdsec.update_frequency is not a valid duration. Example: 1d, 1h, 1m, 1s"
        )

    config["crowdsec"]["update_frequency"] = res

    if not config.get("stormshield"):
        raise ValueError("stormshield config is not set")

    if not config["stormshield"].get("host"):
        raise ValueError("stormshield.host is not set")

    if not config["stormshield"].get("ssh_username"):
        raise ValueError("stormshield.ssh_username is not set")

    if not config["stormshield"].get("ssh_password") and not config["stormshield"].get(
        "ssh_private_key_path"
    ):
        raise ValueError("stormshield.ssh_password or stormshield.ssh_private_key_path is not set")

    if not config["stormshield"].get("api_username"):
        raise ValueError("stormshield.api_username is not set")

    if not config["stormshield"].get("api_password"):
        raise ValueError("stormshield.api_password is not set")

    if not config["stormshield"].get("api_port"):
        raise ValueError("stormshield.api_port is not set")

    return config


def set_logging(config):
    global logger
    list(map(logger.removeHandler, logger.handlers))
    logger.setLevel(get_log_level(config["log_level"]))
    if config["log_mode"] == "stdout":
        handler = logging.StreamHandler(sys.stdout)
    elif config["log_mode"] == "stderr":
        handler = logging.StreamHandler(sys.stderr)
    elif config["log_mode"] == "file":
        handler = RotatingFileHandler(config["log_file"], mode="a+")
    else:
        raise ValueError(f"Invalid log mode: {config['log_mode']}")

    formatter = CustomFormatter()
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.info(f"Started Stormshield Bouncer")


def generate_base_config():
    base_cfg = f"""
# CrowdSec Config
crowdsec:
  lapi_key: <CROWDSEC_LAPI_KEY>
  lapi_url: "http://localhost:8080/"
  update_frequency: 30s
  include_scenarios_containing: []
  exclude_scenarios_containing: []
  only_include_decisions_from: []
  insecure_skip_verify: false
  key_path: ""  # Used for TLS authentification with CrowdSec LAPI
  cert_path: "" # Used for TLS authentification with CrowdSec LAPI
  ca_cert_path: "" # Used for TLS authentification with CrowdSec LAPI

# Stormshield Config
stormshield:
  host: <STORMSHIELD_HOST>

  ssh_port: 22  # SSH port
  ssh_username: admin
  ssh_password: <STORMSHIELD_SSH_PASSWORD> # optional if using private key auth
  ssh_private_key_path: <SSH_PRIVATE_KEY_PATH> # optional if using password auth

  api_username: admin 
  api_password: <STORMSHIELD_API_PASSWORD>
  api_port: 443
  api_ssl_verify_host: false

# Log Config
log_level: info
log_media: "stdout"
log_dir: "/var/log/"
    """
    print(base_cfg)
