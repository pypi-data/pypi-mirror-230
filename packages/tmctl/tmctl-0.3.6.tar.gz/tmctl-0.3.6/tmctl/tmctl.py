import os
import sys

import fire
import logging
import yaml
import requests

from .controller import (
    CommonOption,
    Catalog,
    Cluster,
    File,
    HelmChart,
    MountFile,
    VeriftyCatalog,
)


class TMCtl(object):
    """
    Admin CLI for Trino Cluster Manager\n
    preparation file
        ./config.yaml or ~/.idp/config.yaml setting
    usage:
        ex) tmctl <group> <command> <yaml file>
        ex) tmctl <catalog, cluster, file, mount, helm_chart ..> <ls, rm, delete, submit ..> <manual.yaml>
        ex) tmctl catalog ls
        ex) tmctl catalog submit test.yaml
    """

    def __init__(
        self,
        url=None,
        username=None,
        password=None,
        output=None,
        indent=4,
        log_level="WARNING",
        verbose=False,
    ):
        self._config = self._init_config()

        admin_url = url or self._config["admin"]["url"]
        output = output or "json"
        indent = indent or 4
        username = username or self._config["admin"].get("username", None)
        password = password or self._config["admin"].get("password", None)

        session = requests.session()
        self._try_login(
            session, admin_url=admin_url, username=username, password=password
        )

        common_option = CommonOption(
            admin_url=admin_url,
            session=session,
            output=output,
            indent=indent,
            username=username,
            password=password,
        )

        response = session.get(admin_url + "/v1/catalogs/verify/enabled")
        verify = response.json()["data"]

        if verify:
            self.catalog = VeriftyCatalog(common_option)
        else:
            self.catalog = Catalog(common_option)

        self.cluster = Cluster(common_option)
        self.helm_chart = HelmChart(common_option)
        self.file = File(common_option)
        self.mount = MountFile(common_option)

        log_config = self._config.get("logging", None) or {}

        self._init_cluster_manager_health_check(admin_url)
        self._init_logging(log_config, log_level, verbose)

    def _init_cluster_manager_health_check(self, admin_url):
        try:
            response = requests.get(admin_url + "/")
            if response.status_code != 204:
                print(f"[ERROR] cluster_manager is not ready : {admin_url}")
                exit(1)
        except Exception:
            print(f"[ERROR] cluster_manager is not ready : {admin_url}")
            exit(1)

    def _init_config(self):
        config = None
        try:
            config = yaml.load(open("./config.yaml", "r"), Loader=yaml.Loader)
        except Exception:
            pass

        if not config:
            try:
                home_directory = os.path.expanduser("~")
                config = yaml.load(
                    open(f"{home_directory}/.idp/config.yaml", "r"), Loader=yaml.Loader
                )
            except Exception:
                pass

        return config

    def _init_logging(self, log_config, log_level, verbose):
        handler = log_config.get("handler", "stdout")
        format = log_config.get("format", None)

        level = log_level

        if verbose:
            level = "DEBUG"

        root = logging.getLogger()
        root.setLevel(level)

        if handler:
            if handler == "stdout":
                handler = logging.StreamHandler(sys.stdout)
                handler.setLevel(level)
                if format:
                    handler.setFormatter(logging.Formatter(format))

                root.addHandler(handler)

        logging.debug("[SUCCESS] initializing logging object complete")

    def _try_login(
        self, session: requests.session, admin_url: str, username: str, password: str
    ) -> None:
        try:
            response = session.post(
                f"{admin_url}/v1/auth/login",
                data={"username": username, "password": password},
            )

            if response.status_code in [401, 422]:
                raise Exception("Invalid username or password")
            elif response.status_code == 404:
                logging.warning("Server authentication is not enabled")
        except Exception as e:
            logging.warning(e)
            exit(1)


if __name__ == "__main__":
    fire.Fire(TMCtl)
