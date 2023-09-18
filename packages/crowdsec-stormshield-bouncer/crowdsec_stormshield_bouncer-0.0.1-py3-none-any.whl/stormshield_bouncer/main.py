import argparse
import signal
import sys
from ipaddress import ip_address
from time import sleep

import paramiko
import yaml
from pycrowdsec.client import StreamClient
from scp import SCPClient
from stormshield.sns.sslclient import SSLClient

from stormshield_bouncer.utils import (
    generate_base_config,
    logger,
    set_default_config,
    set_logging,
    validated_config,
)


def get_config(path):
    with open(path, "r") as f:
        return yaml.safe_load(f)


def run_api_commands(config, commands):
    conn = SSLClient(
        host=config["stormshield"]["host"],
        user=config["stormshield"]["api_username"],
        password=config["stormshield"]["api_password"],
        port=config["stormshield"]["api_port"],
        sslverifyhost=config["stormshield"]["api_ssl_verify_host"],
        sslverifypeer=False,
    )
    while True:
        resp = conn.send_command("MODIFY ON FORCE")
        if "Ok" in resp.output or "already have this level" in resp.output:
            break

    while True:
        resp = conn.send_command("MODIFY MONITOR FORCE")
        if "Ok" in resp.output or "already have this level" in resp.output:
            break

    for command in commands:
        resp = conn.send_command(command)
        logger.info(f"{command} {resp}")
    conn.disconnect()


def do_cleanup(config):
    run_api_commands(config, ["MONITOR ADDRESSLIST DELETE Type=BlackList Name1=Crowdsec"])
    ssh_connection = get_ssh_connection(config)
    update_objects(
        ssh_connection=ssh_connection,
        remote_path="/data/Main/ConfigFiles/object",
        new_content=[],
    )
    run_api_commands(
        config,
        [
            "CONFIG OBJECT GROUP DELETE NAME=Crowdsec UPDATE=1",
            "CONFIG OBJECT GROUP DELETE NAME=CrowdsecDeleteGroup UPDATE=1",
        ],
    )


def get_ssh_connection(config):
    ssh_connection = paramiko.SSHClient()
    ssh_connection.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    if config["stormshield"].get("ssh_private_key_path"):
        ssh_connection.connect(
            hostname=config["stormshield"]["host"],
            port=config["stormshield"]["ssh_port"],
            username=config["stormshield"]["ssh_username"],
            password=config["stormshield"]["ssh_password"],
            key_filename=config["stormshield"]["ssh_private_key_path"],
            allow_agent=True,
        )
    else:
        ssh_connection.connect(
            hostname=config["stormshield"]["host"],
            port=config["stormshield"]["ssh_port"],
            username=config["stormshield"]["ssh_username"],
            password=config["stormshield"]["ssh_password"],
            allow_agent=True,
            look_for_keys=False,
        )
    return ssh_connection


def run(config, cleanup=False):
    if cleanup:
        config["log_media"] = "stdout"

    set_logging(config)
    if cleanup:
        do_cleanup(config)
        exit(0)

    lapi_client = StreamClient(
        api_key=config["crowdsec"]["lapi_key"],
        lapi_url=config["crowdsec"]["lapi_url"],
        interval=config["crowdsec"]["update_frequency"],
        include_scenarios_containing=config["crowdsec"]["include_scenarios_containing"],
        exclude_scenarios_containing=config["crowdsec"]["exclude_scenarios_containing"],
        only_include_decisions_from=config["crowdsec"]["only_include_decisions_from"],
        ca_cert_path=config["crowdsec"].get("ca_cert_path"),
        cert_path=config["crowdsec"].get("cert_path"),
        key_path=config["crowdsec"].get("key_path"),
        scopes=["ip"],
    )
    lapi_client.run()

    run_api_commands(
        config,
        [
            "CONFIG OBJECT GROUP NEW NAME=Crowdsec UPDATE=1",
            "CONFIG OBJECT GROUP NEW NAME=CrowdsecDeleteGroup UPDATE=1",
        ],
    )

    current_ip_state = set()
    while True:
        received_ips = {ip.split("/")[0] for ip in lapi_client.get_current_decisions().keys()}

        new_ips = received_ips - current_ip_state
        if new_ips:
            logger.info(f"Received {len(new_ips)} new IPs")

        deleted_ips = current_ip_state - received_ips

        if deleted_ips:
            logger.info(f"Received {len(deleted_ips)} deleted IPs")

        new_ip_state = current_ip_state.union(new_ips) - deleted_ips

        if new_ip_state == current_ip_state:
            logger.info("No changes in IP state")
            run_api_commands(
                config, ["MONITOR ADDRESSLIST ADD Type=BlackList Name1=Crowdsec Timeout=100000"]
            )
            sleep(config["crowdsec"]["update_frequency"])
            continue

        new_objects = [
            f"crowdsec_ip_{int(ip_address(ip))}={ip},resolve=static" for ip in new_ip_state
        ]

        deleted_objects = [
            f"crowdsec_ip_{int(ip_address(ip))}={ip},resolve=static" for ip in deleted_ips
        ]

        try:
            ssh_connection = get_ssh_connection(config)
            update_objects(
                ssh_connection=ssh_connection,
                remote_path="/data/Main/ConfigFiles/object",
                new_content=new_objects + deleted_objects,
            )

            update_groups(
                ssh_connection=ssh_connection,
                remote_path="/data/Main/ConfigFiles/objectgroup",
                group_name="[Crowdsec]",
                new_content=[f"crowdsec_ip_{int(ip_address(ip))}" for ip in new_ip_state],
            )

            if deleted_ips:
                update_groups(
                    ssh_connection=ssh_connection,
                    remote_path="/data/Main/ConfigFiles/objectgroup",
                    group_name="[CrowdsecDeleteGroup]",
                    new_content=[f"crowdsec_ip_{int(ip_address(ip))}" for ip in deleted_ips],
                )
        finally:
            ssh_connection.close()

        run_api_commands(
            config,
            [
                "MONITOR ADDRESSLIST ADD Type=BlackList Name1=Crowdsec Timeout=100000",
                "MONITOR ADDRESSLIST DELETE Type=BlackList Name1=CrowdsecDeleteGroup",
            ],
        )
        current_ip_state = new_ip_state
        sleep(config["crowdsec"]["update_frequency"])


def read_content_at_path(ssh_connection, remote_path):
    stdin, stdout, stderr = ssh_connection.exec_command(f"cat {remote_path}")
    return stdout.read().decode()


def update_objects(ssh_connection, remote_path, new_content):
    existing_content = read_content_at_path(ssh_connection, remote_path)
    # Delete lines starting with 'crowdsec_ip'
    lines = existing_content.split("\n")
    filtered_lines = [line for line in lines if not line.strip().startswith("crowdsec_ip")]

    # Find the [Host] section
    host_index = -1
    for idx, line in enumerate(filtered_lines):
        if line.strip().startswith("[Host]"):
            host_index = idx
            break

    if host_index != -1:
        # Insert the new content after [Host]
        modified_content = (
            "\n".join(filtered_lines[: host_index + 1])
            + "\n"
            + "\n".join(new_content)
            + "\n"
            + "\n".join(filtered_lines[host_index + 1 :])
        )

        # Write the modified content to a temporary file
        temp_filename = "temp_remote_file"
        with open(temp_filename, "w") as temp_file:
            temp_file.write(modified_content)

        # Use SCPClient to upload the temporary file to the remote path
        with SCPClient(ssh_connection.get_transport()) as scp:
            scp.put(temp_filename, remote_path)


def update_groups(ssh_connection, remote_path, group_name, new_content):
    # Read the existing remote file content
    existing_content = read_content_at_path(ssh_connection, remote_path)

    # Find the start and end indices of [Crowdsec] section
    start_index = existing_content.find(group_name)
    if start_index != -1:
        end_index = existing_content.find("[", start_index + 1)
        if end_index == -1:
            end_index = len(existing_content)

        # Construct the modified content
        modified_content = (
            existing_content[: start_index + len(group_name) + 1]
            + "\n".join(new_content)
            + "\n"
            + existing_content[end_index:]
        )

        # Write the modified content to a temporary file
        temp_filename = "temp_remote_file"
        with open(temp_filename, "w") as temp_file:
            temp_file.write(modified_content)

        # Use SCPClient to upload the temporary file to the remote path
        with SCPClient(ssh_connection.get_transport()) as scp:
            scp.put(temp_filename, remote_path)


def main():
    parser = argparse.ArgumentParser(description="CrowdSec Stormshield Bouncer")
    parser.add_argument(
        "-c",
        "--config",
        help="Path to the configuration file",
        default="crowdsec-stormshield-bouncer.yaml",
    )
    parser.add_argument("-g", help="Generate base config", default=False, action="store_true")
    parser.add_argument(
        "-d",
        help="Deletes all the configurations that could've beeen created by the bouncer on your stormshield appliance.",
        default=False,
        action="store_true",
    )

    args = parser.parse_args()
    if args.g:
        generate_base_config()
        sys.exit(0)

    config = get_config(args.config)
    config = set_default_config(config)
    config = validated_config(config)

    def signal_handler(sig, frame):
        logger.info("Caught signal, exiting...")
        do_cleanup(config)
        exit(0)

    if not args.d:
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

    run(config, args.d)


if __name__ == "__main__":
    main()
