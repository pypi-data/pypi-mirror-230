from dataclasses import dataclass
import datetime
import json
import logging
import os
import time

import requests
import yaml


@dataclass
class CommonOption:
    admin_url: str
    session: requests.Session = None
    output: str = "json"
    indent: int = 4
    username: str = None
    password: str = None


@dataclass
class CommonResponse:
    status: bool
    message: str = None
    data: dict = None


class AdminClient(object):
    def __init__(
        self,
        common_option: CommonOption,
        base_url: str = None,
    ):
        self._common_option = common_option
        self._admin_url = self._common_option.admin_url
        self._output = self._common_option.output
        self._indent = self._common_option.indent

        self._base_url = base_url
        self._session = common_option.session or requests.session()

    def _response_to_object(self, response: dict) -> CommonResponse:
        return CommonResponse(
            status=response.get("status", None) or None,
            message=response.get("message", None) or {},
            data=response.get("data", None) or {},
        )

    def _extract_namespace(self, cluster) -> str:
        settings = cluster.get("settings", None) or {}
        namespace = settings.get("namespace", None) or None

        changed_name = cluster["name"].replace("_", "-")

        namespace = namespace or changed_name

        return namespace

    def _parse_proxy_service(self, yamls_str) -> str:
        find = False
        proxy_name = None

        for each in yaml.load_all(yamls_str, Loader=yaml.Loader):
            if find:
                break

            if not isinstance(each, dict):
                continue

            kind = each.get("kind", "")
            if kind == "Service":
                port_list = each["spec"]["ports"]
                for port_spec in port_list:
                    if port_spec["port"] == 8088:
                        find = True
                        proxy_name = each["metadata"]["name"]

        return proxy_name

    def _send_delete(
        self,
        url,
        params: dict = None,
    ) -> bool:
        response = self._session.delete(self._admin_url + url, params=params)

        if response.ok:
            return self._response_to_object(response.json())
        else:
            message = response.json()["message"]
            print(f"[ERROR] reason : {message}")
            exit(1)

    def _send_get(self, url, params=None) -> CommonResponse:
        params = params or {}
        response = self._session.get(self._admin_url + url, params=params)

        if response.ok:
            return self._response_to_object(response.json())
        else:
            message = response.json()["message"]
            print(f"[ERROR] reason : {message}")
            exit(1)

    def _send_health_check_status_get(self, url, params=None) -> CommonResponse:
        params = params or {}
        response = self._session.get(self._admin_url + url, params=params)

        if response.ok:
            return self._response_to_object(response.json())
        else:
            return CommonResponse(
                status=None,
                message={"text": "cluster off"},
                data=None,
            )

    def _send_binary_post(self, url, file_path, form_data):
        files = {"file": open(file_path, "rb")}

        response = self._session.post(
            self._admin_url + url, data=form_data, files=files
        )
        if response.ok:
            return self._response_to_object(response.json())
        else:
            message = response.json()["message"]
            print(f"[ERROR] reason : {message}")
            exit(1)

    def _send_download(self, url, params=None):
        response = self._session.get(self._admin_url + url, params=params)
        if response.ok:
            return response.content
        else:
            message = response.json()["message"]
            print(f"[ERROR] reason : {message}")
            exit(1)

    def _send_post(
        self, url, json_data: dict = None, form_data: dict = None, params: dict = None
    ):
        json_data = json_data or {}
        response = self._session.post(
            self._admin_url + url, data=form_data, json=json_data, params=params
        )

        if response.ok:
            return self._response_to_object(response.json())
        else:
            print(response.status_code)
            print(response.json())
            message = response.json()["message"]
            print(f"[ERROR] reason : {message}")
            exit(1)

    def _send_put(
        self, url, json_data: dict = None, form_data: dict = None, params: dict = None
    ):
        json_data = json_data or {}
        response = self._session.put(
            self._admin_url + url, data=form_data, json=json_data, params=params
        )

        if response.ok:
            return self._response_to_object(response.json())
        else:
            message = response.json()["message"]
            print(f"[ERROR] reason : {message}")
            exit(1)

    def _yaml_load_all(self, filepath):
        yamls = []

        try:
            for each in yaml.load_all(open(filepath, "r"), Loader=yaml.Loader):
                yamls.append(each)
        except Exception:
            print(f"[ERROR] No such file or yaml : {filepath}")
            exit(1)

        return yamls

    def delete(self, name: str, model_id: int = None):
        """
        delete command to name or model_id
        """
        delete_response = None
        identifier = model_id or name
        return_value = None

        if model_id:
            delete_response = self._send_delete(f"{self._base_url}/{model_id}")
        elif name:
            response = self._send_get(f"{self._base_url}", params={"name": name})

            models = response.data
            if models:
                model = models[0]

                model_id = model["id"]

                delete_response = self._send_delete(f"{self._base_url}/{model_id}")

        if delete_response:
            return_value = f"identifier: {identifier} is successfully deleted!"
        else:
            return_value = f"identifier: {identifier} does not be successfully deleted!"

        return return_value

    def get(self, name):
        """
        get command to model name's info
        """
        response = self._send_get(f"{self._base_url}", {"name": name})
        for each in response.data:
            self._print(each)

    def list(self):
        """
        view command to group's list
        """
        response = self._send_get(self._base_url)
        self._print(response.data)

    def ls(self):
        """
        view command to group's list
        """
        return self.list()

    def _print(self, dictionary):
        dictionary = dictionary or {}
        if self._output == "json":
            print(json.dumps(dictionary, indent=self._indent))
        elif self._output == "yaml":
            print(yaml.dump(dictionary, indent=self._indent))

    def rm(self, name: str, model_id: int = None):
        """
        rm(delete) command to name or model_id
        """
        return self.delete(name, model_id)


class File(AdminClient):
    """
    File setting\n
    preparation file
        setting file yaml file
    usage:
        ex) tmctl <group> <command> <yaml file>
        ex) tmctl file <ls(list), rm(delete), submit get> <manual.yaml>
        ex) tmctl file ls
        ex) tmctl file submit test.yaml
    """

    def __init__(self, common_option: CommonOption):
        super(File, self).__init__(common_option, "/v1/files")

    def download(self, name, path=None):
        """
        file download command\n
        """
        path = path or "./"
        response = self._send_get(f"{self._base_url}", {"name": name})

        file = response.data[0]

        binary = self._send_download(f"{self._base_url}/{file['id']}/download")

        if binary:
            file_path = os.path.join(path, file["file_name"])
            with open(file_path, "wb") as _f:
                _f.write(binary)

            self._print("download success.")
        else:
            self._print("empty binary")

    def ls(self):
        """
        file list(ls) check\n
        """
        self.list()

    def rm(self, name: str, model_id: int = None):
        """
        file delete(rm) command\n
        """
        return self.delete(name, model_id)

    def submit(self, path):
        """
        file submit(add) command\n
        """
        yamls = self._yaml_load_all(path)

        for each in yamls:
            version = each.get("version", None)
            action_type = each.get("type", None)

            if version in ["v1/file"]:
                file_config = each.get("file", None) or {}
                name = file_config.get("name", None)
                file_path = file_config.get("file_path", None)
                target_path = file_config.get("target_path", None)

                if not name:
                    print("invalid name", name)
                    exit(1)

                if action_type == "create":
                    file_exists = os.path.exists(file_path)

                    if (not file_path) or (not file_exists):
                        print("invalid file_path", file_path)
                        exit(1)

                    response = self._send_binary_post(
                        "/v1/files",
                        file_path,
                        form_data={"name": name, "target_path": target_path},
                    )
                    self._print(response.data)

                elif action_type == "update":
                    file_id = file_config.get("id", None)

                    if file_id:
                        if file_path:
                            file_exists = os.path.exists(file_path)

                            if (not file_path) or (not file_exists):
                                print("invalid file_path", file_path)
                                exit(1)

                            response = self._send_binary_post(
                                f"/v1/files/{file_id}",
                                file_path,
                                form_data={"name": name, "target_path": target_path},
                            )
                        else:
                            response = self._send_post(
                                f"/v1/files/{file_id}",
                                form_data={"name": name, "target_path": target_path},
                            )

                        self._print(response.data)


class Catalog(AdminClient):
    """
    catalog setting\n
    preparation file
        setting catalog yaml file
    usage:
        ex) tmctl <group> <command> <yaml file>
        ex) tmctl catalog <ls(list), rm(delete), submit get> <manual.yaml>
        ex) tmctl catalog ls
        ex) tmctl catalog submit test.yaml
    """

    def __init__(self, common_option: CommonOption):
        super(Catalog, self).__init__(common_option, "/v1/catalogs")

    def ls(self):
        """
        catalog list(ls) check\n
        """
        self.list()

    def rm(self, name: str = None, catalog_id: int = None):
        """
        catalog delete(rm) command\n
        """
        return self.delete(name, catalog_id)

    def viewer_restart(self):
        viewer_enabled = self._send_get("/v1/catalogs/viewer/enabled")

        if viewer_enabled:
            self._send_post("/v1/catalogs/viewer/restart")

    def manually_cache(self):
        viewer_enabled = self._send_get("/v1/catalogs/viewer/enabled")

        if viewer_enabled:
            self._send_post("/v1/catalogs/viewer/manually_cache")

    def submit(self, path):
        """
        catalog submit(add)\n
        """
        yamls = self._yaml_load_all(path)

        for each in yamls:
            version = each.get("version", None)
            action_type = each.get("type", None)

            if version in ["v1/catalog"]:
                catalog_config = each.get("catalog", None) or {}
                name = catalog_config.get("name", None)
                catalog_type = catalog_config.get("catalog_type", None)
                properties = catalog_config.get("properties", None)

                if not name:
                    print("invalid name", name)
                    exit(1)

                if not catalog_type:
                    print("invalid chart name", catalog_type)
                    exit(1)

                if action_type == "create":
                    response = self._send_post(
                        "/v1/catalogs",
                        json_data={
                            "name": name,
                            "catalog_type": catalog_type,
                            "properties": properties,
                        },
                    )

                    self._print(response.data)
                    self.viewer_restart()
                elif action_type == "update":
                    catalog_id = catalog_config.get("id", None)

                    if catalog_id:
                        response = self._send_post(
                            f"/v1/catalogs/{catalog_id}",
                            json_data={
                                "name": name,
                                "catalog_type": catalog_type,
                                "properties": properties,
                            },
                        )
                        self._print(response.data)
                        self.viewer_restart()
                    else:
                        message = "catalog_id is None"
                        print(f"[ERROR] reason : {message}")
                        exit(1)
                else:
                    message = "invalid action type"
                    print(f"[ERROR] reason : {message}")
                    exit(1)


class VeriftyCatalog(Catalog):
    """
    catalog setting\n
    preparation file
        setting catalog yaml file
    usage:
        ex) tmctl <group> <command> <yaml file>
        ex) tmctl catalog <ls(list), rm(delete), submit get> <manual.yaml>
        ex) tmctl catalog ls
        ex) tmctl catalog submit test.yaml
    """

    def __init__(self, common_option: CommonOption):
        super(Catalog, self).__init__(common_option, "/v1/catalogs")

    def submit(self, path):
        def _verify_catalog(candidate_id, refresh, timeout):
            timeout_flag = False
            start_time = datetime.datetime.now(datetime.timezone.utc)

            candidate_id_response = self._send_get(
                f"/v1/catalogs/verify/{candidate_id}"
            )
            release = candidate_id_response.data[0]
            while release.get("status", "running") not in ["success", "failed"]:
                time.sleep(refresh)
                current_time = datetime.datetime.now(datetime.timezone.utc)

                if (current_time - start_time).seconds > timeout:
                    timeout_flag = True
                    exit(1)

                candidate_id_response = self._send_get(
                    f"/v1/catalogs/verify/{candidate_id}"
                )
                release = candidate_id_response.data[0]
                self._print(release)

            if timeout_flag:
                finished = False
            else:
                finished = True
            return finished

        yamls = self._yaml_load_all(path)

        for each in yamls:
            print(each)
            version = each.get("version", None)
            action_type = each.get("type", None)

            if version in ["v1/catalog"]:
                catalog_config = each.get("catalog", None) or {}
                name = catalog_config.get("name", None)
                catalog_type = catalog_config.get("catalog_type", None)
                properties = catalog_config.get("properties", None)

                if not name:
                    print("invalid name", name)
                    exit(1)

                if not catalog_type:
                    print("invalid chart name", catalog_type)
                    exit(1)

                if action_type == "create":
                    verify_response = self._send_post(
                        "/v1/catalogs/verify",
                        json_data={
                            "name": name,
                            "catalog_type": catalog_type,
                            "properties": properties,
                        },
                    )
                    self._print(verify_response.data)

                    if verify_response.data:
                        candidate_id = verify_response.data[0].get("candidate_id", None)
                        verify_result = _verify_catalog(
                            candidate_id, refresh=1, timeout=120
                        )

                        if verify_result:
                            response = self._send_post(
                                f"/v1/catalogs/verify/{candidate_id}"
                            )
                            self._print(response.data)
                            self._print("catalog create success.")
                            self.viewer_restart()

                        else:
                            message = "catalog verify is failed"
                            self._print(f"[ERROR] reason : {message}")
                            exit(1)
                    else:
                        message = "catalog verify is failed"
                        self._print(f"[ERROR] reason : {message}")
                        exit(1)

                elif action_type == "update":
                    catalog_id = catalog_config.get("id", None)

                    if catalog_id:
                        response = self._send_post(
                            f"/v1/catalogs/{catalog_id}",
                            json_data={
                                "name": name,
                                "catalog_type": catalog_type,
                                "properties": properties,
                            },
                        )
                        self._print(response.data)
                        self._print("catalog update success.")
                        self.viewer_restart()
                    else:
                        message = "catalog_id is None"
                        self._print(f"[ERROR] reason : {message}")
                        exit(1)
                else:
                    message = "invalid action type"
                    self._print(f"[ERROR] reason : {message}")
                    exit(1)


class Cluster(AdminClient):
    """
    cluster setting\n
    preparation file
        setting cluster yaml file
    usage:
        ex) tmctl <group> <command> <yaml file>
        ex) tmctl cluster <ls(list), rm(delete), submit get> <manual.yaml>
        ex) tmctl cluster ls
        ex) tmctl cluster submit test.yaml
    """

    def __init__(self, common_option: CommonOption):
        super(Cluster, self).__init__(common_option, "/v1/clusters")

    def add_catalog(self, cluster_name, catalog_name, direct_on=False):
        response = self._send_get("/v2/client/clusters", params={"name": cluster_name})
        cluster = response.data[0]

        response = self._send_get("/v1/catalogs", params={"name": catalog_name})
        catalog = response.data[0]

        cluster["catalog_list"].append(catalog["id"])

        response = self._send_put(
            "/v2/client/clusters",
            json_data=cluster,
            params={"name": cluster_name, "direct_on": direct_on},
        )
        self._print(response.data)

    def remove_catalog(self, cluster_name, catalog_name, direct_on=False):
        response = self._send_get("/v2/client/clusters", params={"name": cluster_name})
        cluster = response.data[0]

        response = self._send_get("/v1/catalogs", params={"name": catalog_name})
        catalog = response.data[0]

        if catalog["id"] in cluster["catalog_list"]:
            cluster["catalog_list"].remove(catalog["id"])

        response = self._send_put(
            "/v2/client/clusters",
            json_data=cluster,
            params={"name": cluster_name, "direct_on": direct_on},
        )
        self._print(response.data)

    def rm_catalog(self, cluster_name, catalog_name, direct_on=False):
        return self.remove_catalog(
            cluster_name=cluster_name, catalog_name=catalog_name, direct_on=direct_on
        )

    def create(self, name, **kwargs):
        """
        cluster create command\n
        e.g) tmctl cluster create cluster_name
        e.g) tmctl cluster create cluster_name -direct_on=False
        """
        parameters = {**{"name": name, "direct_on": True}, **kwargs}
        response = self._send_post("/v2/client/clusters", parameters)
        self._print(response.data)

    def delete(self, name, force=False):
        """
        cluster delete(rm) command\n
        """
        response = self._send_get("/v2/client/clusters", {"name": name})

        clusters = response.data

        if clusters:
            cluster = clusters[0]
            health_check = self._health_check_status(cluster["id"]).data

            if health_check:
                if force:
                    self._send_delete(
                        f"""/v2/client/clusters/{cluster["id"]}""",
                        params={"force_remove": True},
                    )
                else:
                    print("Cluster is on. please off the cluster first.")
                    logging.warning("Cluster is on. please off the cluster first.")
                    exit(1)

        response = self._send_delete(f"""/v2/client/clusters/{cluster["id"]}""")
        self._print(response.data)

    def _health_check_status(self, cluster_id):
        response = self._send_health_check_status_get(
            f"/v1/clusters/{cluster_id}/gateway/health"
        )
        return response

    def _waiting_release(self, release_id, refresh, timeout):
        start_time = datetime.datetime.now(datetime.timezone.utc)

        response = self._send_get(f"/v1/releases/{release_id}")
        finished = False
        timeout_flag = False
        release = response.data[0]

        while release.get("status", "QUEUED") not in ["FINISHED", "FAILED"]:
            time.sleep(refresh)

            current_time = datetime.datetime.now(datetime.timezone.utc)

            if (current_time - start_time).seconds > timeout:
                timeout_flag = True
                exit(1)

            response = self._send_get(f"/v1/releases/{release_id}")
            release = response.data[0]
            self._print(release)

        if timeout_flag:
            finished = False
        else:
            finished = True

        return finished

    def _waiting_and_get_release_log(self, release_id, refresh, timeout):
        start_time = datetime.datetime.now(datetime.timezone.utc)

        response = self._send_get(f"/v1/releases/{release_id}/log")
        celery_response = response.data[0]

        timeout_flag = False
        while celery_response.get("state", "PENDING") not in ["SUCCESS", "FAILURE"]:
            time.sleep(refresh)
            current_time = datetime.datetime.now(datetime.timezone.utc)

            if (current_time - start_time).seconds > timeout:
                timeout_flag = True
                exit(1)

            response = self._send_get(f"/v1/releases/{release_id}/log")
            celery_response = response.data[0]

            self._print(celery_response)

        if timeout_flag:
            response = None

        return celery_response

    def _execute_and_get_helm_release(self, url, refresh, timeout):
        response = self._send_post(url)
        release = response.data[0]

        release_id = release["id"]

        self._print(release)

        if not self._waiting_release(release_id, refresh, timeout):
            return None

        response = self._send_get(f"/v1/releases/{release_id}").data[0]

        return response

    def _execute_and_get_helm_release_log(self, url, refresh, timeout):
        response = self._send_post(url)
        release = response.data[0]

        release_id = release["id"]

        self._print(release)

        if not self._waiting_release(release_id, refresh, timeout):
            return None

        log_response = self._waiting_and_get_release_log(release_id, refresh, timeout)

        return log_response

    def _do_install(self, cluster_id, refresh, timeout):
        return self._execute_and_get_helm_release(
            f"/v1/clusters/{cluster_id}/install", refresh, timeout
        )

    def _do_upgrade(self, cluster_id, refresh, timeout):
        return self._execute_and_get_helm_release(
            f"/v1/clusters/{cluster_id}/upgrade", refresh, timeout
        )

    def list(self):
        """
        cluster list(ls) check\n
        """
        response = self._send_get("/v2/client/clusters")
        clusters = response.data

        self._print(clusters)

    def ls(self):
        """
        cluster list(ls) check\n
        """
        self.list()

    def get(self, name):
        """
        cluster info(ON/OFF) get\n
        """
        response = self._send_get("/v2/client/clusters", {"name": name})

        clusters = response.data

        if clusters:
            cluster = clusters[0]

            cluster["status"] = (
                "ON" if self._health_check_status(cluster["id"]).data else "OFF"
            )

            self._print(cluster)

    def status(self, name, refresh=1, timeout=120):
        """
        cluster status get\n
        """
        cluster = None

        response = self._send_get("/v2/client/clusters", params={"name": name})

        clusters = response.data

        if clusters:
            cluster = clusters[0]

        if not cluster:
            return

        cluster_status_response = self._execute_and_get_helm_release_log(
            f"/v1/clusters/{cluster['id']}/status", refresh, timeout
        )

        response_log = cluster_status_response.get("log", {}) or {}
        return_value = response_log.get("return", {}) or {}

        is_cluster_installed = len(return_value.get("stdout", "")) > 0

        proxy_status_response = self._execute_and_get_helm_release_log(
            f"/v1/clusters/{cluster['id']}/proxy/status", refresh, timeout
        )

        response_log = proxy_status_response.get("log", {}) or {}
        return_value = response_log.get("return", {}) or {}

        is_proxy_installed = len(return_value.get("stdout", "")) > 0

        status = {
            "cluster installed:": is_cluster_installed,
            "proxy installed:": is_proxy_installed,
            "cluster status (health check):": "ON"
            if self._health_check_status(cluster["id"]).data
            else "OFF",
        }

        self._print(status)

    def rm(self, name, force=False, refresh=1, timeout=120):
        """
        cluster delete(rm) command\n
        """
        return self.delete(name, force, refresh, timeout)

    def submit(self, path):
        """
        cluster submit(add)\n
        """
        yamls = self._yaml_load_all(path)

        for each in yamls:
            version = each.get("version", None)
            action_type = each.get("type", None)

            if version in ["v1/cluster"]:
                cluster_config = each.get("cluster", None) or {}
                name = cluster_config.get("name", None)
                direct_on = cluster_config.get("direct_on", True)
                chart_name = cluster_config.get("chart", None)
                cluster_view_data = cluster_config.get("cluster_view_data", None) or {}

                params = {"name": chart_name}

                response = self._send_get("/v1/charts", params=params)

                chart_id = None
                charts = response.data
                if charts:
                    chart_id = charts[0]["id"]

                if not chart_id:
                    raise Exception("invalid chart options")

                catalog_config = cluster_config.get("catalogs", None) or []

                catalog_list = []

                for catalog_name in catalog_config:
                    response = self._send_get(f"/v1/catalogs?name={catalog_name}")

                    catalogs = response.data

                    if catalogs:
                        catalog_list.append(catalogs[0]["id"])

                file_config = cluster_config.get("files", None) or []

                file_list = []

                for file_name in file_config:
                    response = self._send_get(f"/v1/files?name={file_name}")

                    files = response.data

                    if files:
                        file_list.append(files[0]["id"])

                settings = cluster_config.get("settings", None) or {}

                if not name:
                    print("invalid name", name)
                    exit(1)

                if not chart_id:
                    print("invalid chart id or chart_name", chart_id, chart_name)
                    exit(1)

                if action_type == "create":
                    response = self._send_post(
                        "/v2/client/clusters",
                        json_data={
                            "name": name,
                            "chart_id": chart_id,
                            "catalog_list": catalog_list,
                            "file_list": file_list,
                            "settings": settings,
                            "cluster_view_data": cluster_view_data,
                        },
                        params={"direct_on": direct_on},
                    )

                    clusters = response.data

                    if clusters:
                        self._print(clusters)

                elif action_type == "update":
                    cluster_id = cluster_config.get("id", None)

                    if cluster_id:
                        response = self._send_put(
                            f"/v2/client/clusters/{cluster_id}",
                            json_data={
                                "name": name,
                                "chart_id": chart_id,
                                "catalog_list": catalog_list,
                                "file_list": file_list,
                                "settings": settings,
                                "cluster_view_data": cluster_view_data,
                            },
                            params={"direct_on": direct_on},
                        )

                        clusters = response.data

                        if clusters:
                            self._print(clusters)
                    else:
                        message = "cluster_id is None"
                        # logging.warning("cluster id is unknown.")
                        print(f"[ERROR] reason : {message}")
                        exit(1)
                else:
                    message = "invalid action type"
                    print(f"[ERROR] reason : {message}")
                    exit(1)

    def on(self, name):
        """
        cluster on command
        """
        response = self._send_get("/v2/client/clusters", {"name": name})

        clusters = response.data

        if clusters:
            cluster = clusters[0]
            response = self._send_put(f"""/v2/client/clusters/{cluster["id"]}/on""")
            self._print(response.data)

            logging.info(response)
        else:
            logging.info(f"Cannot find cluster name: {name}")

    def off(self, name):
        """
        cluster off command(not delete)
        """
        response = self._send_get("/v2/client/clusters", {"name": name})

        clusters = response.data

        if clusters:
            cluster = clusters[0]
            response = self._send_put(f"""/v2/client/clusters/{cluster["id"]}/off""")
            self._print(response.data)

            logging.info(response)
        else:
            logging.info(f"Cannot find cluster name: {name}")


class HelmChart(AdminClient):
    """
    helm_chart setting\n
    preparation file
        setting helm_chart yaml file
    usage:
        ex) tmctl <group> <command> <yaml file>
        ex) tmctl helm_chart <ls(list), rm(delete), submit get> <manual.yaml>
        ex) tmctl helm_chart ls
        ex) tmctl helm_chart submit test.yaml
    """

    def __init__(self, common_option: CommonOption):
        super(HelmChart, self).__init__(common_option, "/v1/charts")

    def ls(self):
        """
        helm_chart list check\n
        """
        self.list()

    def rm(self, name: str = None, chart_id: int = None):
        """
        helm_chart remove\n
        """
        return self.delete(name, chart_id)

    def default(self, name: str = None, chart_id: int = None):
        """
        helm_chart default\n
        """
        default_response = None
        identifier = chart_id or name
        return_value = None

        if chart_id:
            default_response = self._send_post(
                f"{self._base_url}/{chart_id}/set_default"
            )
        elif name:
            response = self._send_get(f"{self._base_url}", params={"name": name})

            models = response.data
            if models:
                model = models[0]
                chart_id = model["id"]
                default_response = self._send_post(
                    f"{self._base_url}/{chart_id}/set_default"
                )

        if default_response:
            return_value = (
                f"identifier: {identifier} is successfully set default helm chart!"
            )
        else:
            return_value = f"identifier: {identifier} does not be successfully set default helm chart!"

        return return_value

    def submit(self, path):
        """
        helm_chart submit(add)\n
        """
        yamls = self._yaml_load_all(path)

        for each in yamls:
            version = each.get("version", None)
            action_type = each.get("type", None)

            if version in ["v1/chart"]:
                chart_config = each.get("chart", None) or {}
                name = chart_config.get("name", None)
                chart_name = chart_config.get("chart_name", None)
                chart_version = chart_config.get("version", None)
                registry = chart_config.get("registry", None)
                repository = chart_config.get("repository", None)
                values = chart_config.get("values", None)

                if not name:
                    print("invalid name", name)
                    exit(1)

                if not chart_name:
                    print("invalid chart name", chart_name)
                    exit(1)

                if action_type == "create":
                    response = self._send_post(
                        "/v1/charts",
                        json_data={
                            "name": name,
                            "chart_name": chart_name,
                            "version": chart_version,
                            "registry": registry,
                            "repository": repository,
                            "values": values,
                        },
                    )

                    self._print(response.data[0])
                elif action_type == "update":
                    chart_id = chart_config.get("id", None)

                    if chart_id:
                        response = self._send_post(
                            f"/v1/charts/{chart_id}",
                            json_data={
                                "name": name,
                                "chart_name": chart_name,
                                "version": chart_version,
                                "registry": registry,
                                "repository": repository,
                                "values": values,
                            },
                        )
                        self._print(response.data[0])
                    else:
                        message = "chart_id is None"
                        print(f"[ERROR] reason : {message}")
                        exit(1)
                else:
                    message = "invalid action type"
                    print(f"[ERROR] reason : {message}")
                    exit(1)


class MountFile(AdminClient):
    """
    Mount File setting\n
    preparation file
        setting mount yaml file
    usage:
        ex) tmctl <group> <command> <yaml file>
        ex) tmctl mount <ls(list), rm(delete), submit get> <manual.yaml>
        ex) tmctl mount ls
        ex) tmctl mount submit test.yaml
    """

    def __init__(self, common_option: CommonOption):
        super(MountFile, self).__init__(common_option, "/v1/mounts")

    def get(self, mount_path):
        """
        mount file info get\n
        """
        response = self._send_get(f"{self._base_url}", {"mount_path": mount_path})
        for each in response.data:
            self._print(each)

    def delete(self, mount_path: str, model_id: int = None):
        """
        mount file delete(rm) command\n
        """
        delete_response = None
        identifier = model_id or mount_path
        return_value = None

        if model_id:
            delete_response = self._send_delete(f"{self._base_url}/{model_id}")
        elif mount_path:
            response = self._send_get(
                f"{self._base_url}", params={"mount_path": mount_path}
            )

            models = response.data
            if models:
                model = models[0]

                model_id = model["id"]

                delete_response = self._send_delete(f"{self._base_url}/{model_id}")

        if delete_response:
            return_value = f"identifier: {identifier} is successfully deleted!"
        else:
            return_value = f"identifier: {identifier} does not be successfully deleted!"

        return return_value

    def download(self, mount_path, path=None):
        """
        mount file download command\n
        """
        path = path or "./"
        response = self._send_get(f"{self._base_url}", {"mount_path": mount_path})

        mount_file = response.data[0]

        binary = self._send_download(f"{self._base_url}/{mount_file['id']}/download")

        if binary:
            file_path = os.path.join(path, mount_file["file_name"])
            with open(file_path, "wb") as _f:
                _f.write(binary)

            self._print("download success.")
        else:
            self._print("empty binary")
            exit(1)

    def ls(self):
        """
        mount file list(ls) check\n
        """
        self.list()

    def rm(self, mount_path: str, model_id: int = None):
        """
        mount file delete(rm) command\n
        """
        return self.delete(mount_path, model_id)

    def submit(self, path):
        """
        mount file submit(add) command\n
        """
        yamls = self._yaml_load_all(path)

        for each in yamls:
            version = each.get("version", None)
            action_type = each.get("type", None)

            if version in ["v1/mount"]:
                file_config = each.get("mount", None) or {}
                source_path = file_config.get("source_path", None)
                mount_path = file_config.get("mount_path", None)
                target_path = file_config.get("target_path", None)
                refresh = file_config.get("refresh", None) or False

                if not refresh:
                    if not source_path:
                        print("invalid path", source_path)
                        exit(1)

                    file_exists = os.path.exists(source_path)

                    if not file_exists:
                        print("invalid currnet source fil path", source_path)
                        exit(1)

                    if not mount_path:
                        print("invalid mount_path", mount_path)
                        exit(1)

                if action_type == "create":
                    response = None
                    if refresh:
                        response = self._send_post(
                            "/v1/mounts",
                            form_data={
                                "mount_path": mount_path,
                                "target_path": target_path,
                                "refresh": True,
                            },
                        )
                    else:
                        response = self._send_binary_post(
                            "/v1/mounts",
                            source_path,
                            form_data={
                                "mount_path": mount_path,
                                "target_path": target_path,
                            },
                        )

                    self._print(response.data)
                elif action_type == "update":
                    mount_file_id = file_config.get("id", None)

                    if mount_file_id:
                        response = self._send_binary_post(
                            f"/v1/mounts/{mount_file_id}",
                            source_path,
                            form_data={
                                "mount_path": mount_path,
                                "target_path": target_path,
                            },
                        )

                        self._print(response.data)
