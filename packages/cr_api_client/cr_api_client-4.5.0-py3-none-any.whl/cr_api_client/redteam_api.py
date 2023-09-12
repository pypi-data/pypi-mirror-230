# -*- coding: utf-8 -*-
#
# Copyright (c) 2016-2021 AMOSSYS
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
import json
import os
import pprint
import time
from typing import Any
from typing import Callable
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple
from urllib.parse import urlencode

import requests
from colorama import Fore
from loguru import logger

from cr_api_client.config import cr_api_client_config


# Module variables
attack_list = {}


# -------------------------------------------------------------------------- #
# Internal helpers
# -------------------------------------------------------------------------- #


def _get(route: str, **kwargs: str) -> requests.Response:
    return requests.get(
        f"{cr_api_client_config.redteam_api_url}{route}",
        verify=cr_api_client_config.cacert,
        cert=(cr_api_client_config.cert, cr_api_client_config.key),
        timeout=60,
        **kwargs,
    )


def _post(route: str, **kwargs: str) -> requests.Response:
    return requests.post(
        f"{cr_api_client_config.redteam_api_url}{route}",
        verify=cr_api_client_config.cacert,
        cert=(cr_api_client_config.cert, cr_api_client_config.key),
        timeout=30,
        **kwargs,
    )


def _put(route: str, **kwargs: str) -> requests.Response:
    return requests.put(
        f"{cr_api_client_config.redteam_api_url}{route}",
        verify=cr_api_client_config.cacert,
        cert=(cr_api_client_config.cert, cr_api_client_config.key),
        timeout=30,
        **kwargs,
    )


def _delete(route: str, **kwargs: str) -> requests.Response:
    return requests.delete(
        f"{cr_api_client_config.redteam_api_url}{route}",
        verify=cr_api_client_config.cacert,
        cert=(cr_api_client_config.cert, cr_api_client_config.key),
        timeout=30,
        **kwargs,
    )


def _handle_error(result: requests.Response, context_error_msg: str) -> None:
    if result.headers.get("content-type") == "application/json":
        error_msg = str(result.json())  # ["message"]
    else:
        error_msg = result.text

    raise Exception(
        f"{context_error_msg}. "
        f"Status code: '{result.status_code}'.\n"
        f"Error message: '{error_msg}'."
    )


# -------------------------------------------------------------------------- #
# Redteam API
# -------------------------------------------------------------------------- #


def get_version() -> str:
    """Return Redteam API version."""
    result = _get("/version")

    if result.status_code != 200:
        _handle_error(result, "Cannot retrieve Redteam API version")

    return result.json()


def reset_redteam() -> None:
    """Reset redteam platform (init knowledge_database and delete all workers).

    :return: None

    >>> from cr_api_client import redteam_api
    >>> redteam_api.reset_redteam()  # doctest: +SKIP

    """
    result = _delete("/platform")
    result.raise_for_status()


def logs() -> Dict:
    """Get redteam API logs.

    :return: str

    >>> from cr_api_client import redteam_api
    >>> redteam_api.reset_redteam()  # doctest: +SKIP
    >>> redteam_api.logs()  # doctest: +SKIP
    {}

    """
    url = "/logs"

    result = _get(url, headers={}, data={})

    if result.status_code != 200:
        _handle_error(result, "Cannot retrieve logs from redteam API")

    return result.json()


def list_tactics() -> List[dict]:
    """List all available tactics (based on MITRE ATT&CK).

    :return: Available tactics in JSON format.
    :rtype: :class:`List`

    >>> from cr_api_client import redteam_api
    >>> redteam_api.reset_redteam()  # doctest: +SKIP
    >>> redteam_api.list_tactics()  # doctest: +SKIP
    [{'id': 'TA0001', 'name': 'Initial Access'}, {'id': 'TA0002', 'name': 'Execution'}, {'id': 'TA0003', 'name': 'Persistence'}, {'id': 'TA0004', 'name': 'Privilege Escalation'}, {'id': 'TA0005', 'name': 'Defense Evasion'}, {'id': 'TA0006', 'name': 'Credential Access'}, {'id': 'TA0007', 'name': 'Discovery'}, {'id': 'TA0008', 'name': 'Lateral Movement'}, {'id': 'TA0009', 'name': 'Collection'}, {'id': 'TA0010', 'name': 'Exfiltration'}, {'id': 'TA0011', 'name': 'Command and Control'}, {'id': 'TA0040', 'name': 'Impact'}, {'id': 'TA0042', 'name': 'Resource Development'}, {'id': 'TA0043', 'name': 'Reconnaissance'}]

    """
    url = "/tactic"

    result = _get(url, headers={}, data={})

    if result.status_code != 200:
        _handle_error(result, "Cannot retrieve available tactics from redteam API")

    return result.json()


def list_workers() -> List[dict]:
    """List all available workers.

    :return: Available workers in JSON format.
    :rtype: :class:`List`

    >>> from cr_api_client import redteam_api
    >>> redteam_api.reset_redteam()  # doctest: +SKIP
    >>> redteam_api.list_workers()  # doctest: +SKIP
    [{...}]

    """
    url = "/worker"

    result = _get(url, headers={}, data={})

    if result.status_code != 200:
        _handle_error(result, "Cannot retrieve available workers from redteam API")

    return result.json()


def worker_infos(id_worker: str) -> dict:
    """Retrieve worker info from its ID.

    :return: Worker info in JSON format.
    :rtype: :class:`List`

    >>> from cr_api_client import redteam_api
    >>> redteam_api.reset_redteam()  # doctest: +SKIP
    >>> redteam_api.worker_infos("1021_006_002")  # doctest: +SKIP
    {'id': '1021_006_002', 'name': 'winrm_session', ...}

    """
    url = f"/worker/{id_worker}"

    result = _get(url, headers={}, data={})

    if result.status_code != 200:
        _handle_error(result, "Cannot retrieve worker info from redteam API")

    return result.json()


def list_attacks(status: str = None) -> List[dict]:
    """List all attacks available and done.

    :param status: The status (success, failed, error, running, runnable) to filter.
    :type status: :class:`str`

    :return: List all attacks in JSON format.
    :rtype: :class:`List`

    >>> from cr_api_client import redteam_api
    >>> redteam_api.reset_redteam()  # doctest: +SKIP
    >>> redteam_api.list_attacks(status="success")  # doctest: +SKIP
    []

    """
    url = "/attack"

    if status:
        url = url + "?status=" + status
    result = _get(url, headers={}, data={})

    if result.status_code != 200:
        _handle_error(result, "Cannot retrieve available attacks from redteam API")

    return result.json()


def attack_infos(id_attack: str) -> Tuple[str, List[dict]]:
    """Return status and output for an attack.

    :param id_attack: The attack identifier.
    :type id_attack: :class:`int`

    :return: Status of attack and output data.
    :rtype: :class:`str`, :class:`Dict`

    >>> from cr_api_client import redteam_api
    >>> redteam_api.reset_redteam()  # doctest: +SKIP
    >>> redteam_api.attack_infos(id_attack=1)  # doctest: +SKIP
    ('runnable', None)

    """
    url = "/attack/" + str(id_attack)

    result = _get(url, headers={}, data={})
    if result.status_code != 200:
        _handle_error(result, "Cannot retrieve attack from redteam API")
    res_json = result.json()
    output = None
    if res_json["output"]:
        output = json.loads(res_json["output"])
    return res_json["status"], output


def __waiting_attack(
    id_attack: str, name: str, waiting_worker: bool = True, debug: bool = False
) -> str:
    """
    Waiting for attack status (waiting, success or failed).

    :param id_attack: The attack identifier.
    :type id_attack: :class:`int`
    :param attack_name: The worker name for this attack.
    :type attack_name: :class:`str`
    :param waiting_worker: Wait attack status become "success" or "failed".
    :type waiting_worker: :class:`bool`, optional

    :return: The ID of attack.
    :rtype: :class:`str`

    """
    url = "/attack/" + str(id_attack)

    result = _get(url, headers={}, data={})

    if result.status_code != 200:
        _handle_error(result, "Cannot retrieve attack information from redteam API")

    status = result.json().get("status", None)
    cpt_max = 150
    cpt = 0
    while status not in ["success", "failed", "error"]:  # not finished
        time.sleep(1)
        cpt = cpt + 1
        result = _get(url, headers={}, data={})

        if result.status_code != 200:
            _handle_error(result, "Cannot retrieve attack information from redteam API")

        status = result.json().get("status", None)
        if status == "waiting":
            logger.info(f"[+] ({id_attack}) Attack {name} is waiting.")
            if not waiting_worker:
                return id_attack
        if cpt == cpt_max:
            status = "error"
            _handle_error(result, f"Attack {name} error : TIMEOUT")
        time.sleep(1)

    if status == "success":
        color = Fore.GREEN
    elif status == "failed":
        color = Fore.YELLOW
    elif status == "error":
        color = Fore.RED
        _handle_error(result, f"Attack {name} error.")

    logger.info(
        f"[+] {Fore.BLUE}({id_attack}) Attack {name}{Fore.RESET} : {color}{status}{Fore.RESET}"
    )

    # Retrieve debug value from var env
    debug_env = os.getenv("CR_DEBUG", "0")

    # Debug value can either be set from var env or from function parameter
    if debug or debug_env == "1":
        # Show attack report
        scenario_report = scenario_result()

        pp = pprint.PrettyPrinter(width=160)

        if len(scenario_report) > 0:
            logger.info("[+] Attack report")

            for attack_report in scenario_report:
                if str(attack_report["id"]) == str(id_attack):
                    pp.pprint(attack_report)

        # Show worker logs
        logger.info("[+] Attack worker logs")

        redteam_logs = logs()

        if str(id_attack) in redteam_logs:
            for log in redteam_logs[str(id_attack)]:
                print(log)

    return id_attack


def execute_attack(
    id_attack: int,
    name: str,
    waiting_worker: bool = True,
    options: Dict = {},
    debug: bool = False,
) -> Optional[str]:
    """
    Start attack by id_attack.

    :param id_attack: The attack identifier.
    :type id_attack: :class:`int`
    :param attack_name: The worker name for this attack.
    :type attack_name: :class:`str`
    :param waiting_worker: Wait attack status become "success" or "failed".
    :type waiting_worker: :class:`bool`, optional

    :return: The ID of attack.
    :rtype: :class:`str`

    """
    url = "/attack/" + str(id_attack) + "/play"
    if options:
        url = url + "?" + urlencode(options)
    payload = {}
    headers = {}
    result = _get(url, headers=headers, data=payload)

    if result.status_code != 200:
        _handle_error(result, "Cannot start attack from redteam API")

    result = result.json()
    idAttack = result.get("idAttack", None)
    logger.info(f"[+] {Fore.BLUE}({idAttack}) Attack {name}{Fore.RESET} : started")
    logger.info(f"[+]     Values : {Fore.YELLOW}{result['values']}{Fore.RESET}")
    if idAttack is not None:
        return __waiting_attack(idAttack, name, waiting_worker, debug=debug)


def execute_attack_name(
    attack_name: str, waiting_worker: bool = True, debug: bool = False
) -> Optional[str]:
    """
    Select attack by worker name (first occurence) and execute it.

    :param attack_name: The worker name for this attack.
    :type attack_name: :class:`str`
    :param waiting_worker: Wait attack status become "success" or "failed".
    :type waiting_worker: :class:`bool`, optional

    :return: The ID of attack.
    :rtype: :class:`str`

    """
    url = "/attack"
    result = _get(url, headers={}, data={})

    if result.status_code != 200:
        _handle_error(result, "Cannot retrieve available attacks from redteam API")

    attack = next(
        (x for x in result.json() if x["worker"]["name"] == attack_name), None
    )

    if attack:
        return execute_attack(
            attack["idAttack"], attack_name, waiting_worker, debug=debug
        )
    else:
        logger.warning(f"[-] Attack {attack_name} not avalaible")


def execute_attack_name_by_values(
    attack_name: str,
    retries: int = 3,
    attack_session_identifier: Optional[str] = None,
    attack_values_dict: Optional[Dict[str, Any]] = None,
    attack_values_callback: Optional[Callable[[Dict[str, Any]], bool]] = None,
    waiting_worker: bool = True,
    options: Dict = {},
) -> Optional[str]:
    attack = None
    for _ in range(retries):
        attack = get_attack_by_values(
            attack_name,
            attack_session_identifier=attack_session_identifier,
            attack_values_dict=attack_values_dict,
            attack_values_callback=attack_values_callback,
        )
        if attack:
            break
        else:
            time.sleep(1)

    if not attack:
        message = f"Attack '{attack_name}' was not found after {retries} retries"

        if attack_session_identifier:
            message += f", for attack session id {attack_session_identifier}."

        if attack_values_dict and not attack_values_callback:
            message += f", for attack values {attack_values_dict}."
        elif not attack_values_dict and attack_values_callback:
            message += ", for attack values selected by a callback."
        elif attack_values_dict and attack_values_callback:
            message += f", for attack values {attack_values_dict} and further selected by a callback."

        raise Exception(message)

    return execute_attack(
        attack["idAttack"],
        attack["worker"]["name"],
        waiting_worker=waiting_worker,
        options=options,
    )


def get_attack_by_values(
    attack_name: str,
    attack_session_identifier: Optional[str] = None,
    attack_values_dict: Optional[Dict[str, Any]] = None,
    attack_values_callback: Optional[Callable[[Dict[str, Any]], bool]] = None,
) -> Dict[str, Any]:
    """
    Helper function to find an attack for a specific attack session or for specific attack values

    Allows to search for an available an attack based on its name, and several optional criteria.
    The selection can be done based one:

    * the ID of the attack session to use
    * specific, exact keys/values in the attack values
    * a custom callback, for more complex selection

    The three selection methods can be combined. If two or all three parameters are used
    (`attack_session_identifier`, `attack_values_dict`, `attack_values_callback`), an attack is
    searched that matches all three parameters.

    Example:
    >>> from cr_api_client import redteam_api
    >>> attack_session_id = "d5f7a6a3-54c7-4666-9e9d-31cbc404c21b"
    >>> attack_values_dict = {"target_ip": "1.2.3.4", "param1": 42}
    >>> attack_values_callback = lambda values: "param2" in values and "substring" in values["param2"]
    >>> redteam_api.get_attack_by_values("my_worker_name", attack_session_id, attack_values_dict, attack_values_callback)  # doctest: +SKIP
    {'idAttack': 23, 'worker': {'id': '1487_000_001', 'name': 'my_worker_name', 'description':
    'XXX', 'cve': [],'stability': 'CRASH_SAFE', 'reliability': 'UNIQUE', 'side_effect':
    'NETWORK_CONNECTION', 'killchain_step': 'EXECUTION', 'repeatable': False, 'mitre_data':
    {'technique': {'id': 'T1487', 'name': 'Techname'}, 'subtechnique': {}, 'tactics': [{'id':
    'TA0002', 'name': 'Execution'}]}}, 'status': 'runnable', 'created_date':
    '2023-03-09T17:12:00+01:00', 'started_date': '', 'last_update': '', 'commands': None, 'values':
    '{"target_ip": "1.2.3.4", "param3": "value3", "param2: "this string contains a substring, it
    does, "param1": 42, attack_session_id": "d5f7a6a3-54c7-4666-9e9d-31cbc404c21b"}', 'output': None, 'source': None, 'infrastructure': '{"ip_api_public":
    "91.160.8.7", "domain_name_public": "dpcbwesnmecppni.co.uk", "ip_api_private": "192.168.66.2",
    "type": "C&C_HTTP", "webserver": "91.160.8.8"}', 'docker_id': "f44a56c89e"}

    :param attack_name: The worker name for this attack.
    :type attack_name: :class:`str`
    :param attack_session_identifier: (Optional) The ID of the attack session to use for this attack
    :type attack_session_identifier: class:`str`
    :param attack_values_dict: (Optional) Other key/values searched in the attack values
    :type attack_values_dict: class:`Dict[str, Any]`
    :param attack_values_callback: (Optional) Callback to select an attack, based on its attack
        values, in a custom way
    :type attack_values_callback: class:`Callable[[Dict[str, Any]], bool]`

    :return: The dict of the attack (with keys idAttack, worker, status, values, etc.)
    :rtype: :class:`Dict[str, Any]`
    """

    # The constraint on attack session id is actually a constraint expressed by the dict
    # attack_values_dict
    if attack_session_identifier:
        if attack_values_dict is None:
            attack_values_dict = {}
        attack_values_dict["attack_session_id"] = attack_session_identifier

    for attack in list_attacks():
        if (
            attack
            and attack["values"] != '"None"'
            and attack["worker"]["name"] == attack_name
        ):
            attack_values = json.loads(attack["values"])
            attack_values_match = True

            # Check constraints on the value
            # By dict (exact values)
            if attack_values_dict:
                for k, v in attack_values_dict.items():
                    if k not in attack_values or attack_values[k] != v:
                        attack_values_match = False

            # By callback
            if attack_values_callback:
                attack_values_match = attack_values_match and attack_values_callback(
                    attack_values
                )

            # If all constraints are respected, the attack is the right one
            if attack_values_match:
                return attack


def __execute_attack_with_value(
    attack_name: str,
    waiting_worker: bool = True,
    values: Optional[Dict] = None,
    debug: bool = False,
) -> Optional[str]:
    url = "/attack"
    result = _get(url, headers={}, data={})

    if result.status_code != 200:
        _handle_error(result, "Cannot retrieve available attacks from redteam API")

    for attack in result.json():
        if attack["worker"]["name"] == attack_name:
            if values is not None:
                v_dict = json.loads(attack["values"])
                if set(values.items()).issubset(v_dict.items()):
                    target_attack = attack
                    break
            else:
                target_attack = attack
                break

    if target_attack:
        return execute_attack(
            id_attack=target_attack["idAttack"],
            name=attack_name,
            waiting_worker=waiting_worker,
            debug=debug,
        )
    else:
        logger.warning(f"[-] {Fore.RED} Attack {attack_name} not found.{Fore.RESET}")


def init_knowledge(data: List[dict]) -> bool:
    """
    Insert data in knowledge database.

    :return: boolean

    >>> from cr_api_client import redteam_api
    >>> redteam_api.reset_redteam()  # doctest: +SKIP
    >>> redteam_api.init_knowledge([{"host": {"host_ip": "x.x.x.x", "host": {"netbios_name": "WIN"}, "roles": []}}])  # doctest: +SKIP
    True

    """
    output = {}

    for elt in data:
        key = list(elt)[0]
        output[key] = elt[key]

    url = "/knowledge"
    headers = {"Content-type": "application/json"}
    result = _post(url, headers=headers, data=json.dumps(output))

    if result.status_code != 200:
        _handle_error(result, "Cannot initialize knowledge database from redteam API")
    else:
        return True


def scenario_result() -> str:
    """
    Generate json report about all attack actions.

    :return: List all attacks done and runnning.

    >>> from cr_api_client import redteam_api
    >>> redteam_api.reset_redteam()  # doctest: +SKIP
    >>> redteam_api.scenario_result()  # doctest: +SKIP
    []

    """

    url = "/report"

    result = _get(url, headers={}, data={})

    if result.status_code != 200:
        _handle_error(result, "Cannot get scenario result from redteam API")

    return result.json()


def attack_knowledge() -> str:
    """
    Get the attack knowledge (attack hosts and sessions).

    :return: Attack hosts and sessions.

    >>> from cr_api_client import redteam_api
    >>> redteam_api.reset_redteam()  # doctest: +SKIP
    >>> redteam_api.attack_knowledge()  # doctest: +SKIP
    {'hosts': [], 'network_interfaces': [], 'services': [], 'softwares': [], 'credentials': [], 'payloads': [], 'files': [], 'ad_groups': []}

    """

    url = "/attack_knowledge"

    result = _get(url, headers={}, data={})
    if result.status_code != 200:
        _handle_error(result, "Cannot get attack knowledge result from redteam API")

    try:
        return result.json()
    except Exception:
        raise Exception(
            "Cannot get attack knowledge result from redteam API: invalid JSON received from /attack_knowledge endpoint"
        )


def attack_sessions() -> str:
    """
    Show available redteam attack sessions.

    :return: Attack sessions.

    >>> from cr_api_client import redteam_api
    >>> redteam_api.reset_redteam()  # doctest: +SKIP
    >>> redteam_api.attack_sessions()  # doctest: +SKIP
    []

    """

    url = "/attack_sessions"

    result = _get(url, headers={}, data={})

    if result.status_code != 200:
        _handle_error(result, "Cannot get attack knowledge result from redteam API")

    try:
        knowledge = result.json()
    except Exception:
        raise Exception(
            "Cannot get attack knowledge result from redteam API: invalid JSON received from /attack_session endpoint"
        )

    if "attack_sessions" in knowledge:
        attack_sessions = knowledge["attack_sessions"]
    else:
        raise Exception(
            "Cannot get attack knowledge result from redteam API: invalid JSON received from /attack_session endpoint"
        )

    return attack_sessions


def infrastructures() -> str:
    """
    Show redteam attack infrastructures.

    :return: Attack infractructures.

    >>> from cr_api_client import redteam_api
    >>> redteam_api.reset_redteam()  # doctest: +SKIP
    >>> redteam_api.infrastructures()  # doctest: +SKIP
    []

    """

    url = "/attack_infrastructures"

    result = _get(url, headers={}, data={})

    if result.status_code != 200:
        _handle_error(result, "Cannot get attack knowledge result from redteam API")

    try:
        knowledge = result.json()
    except Exception:
        raise Exception(
            "Cannot get attack infrastructure result from redteam API: invalid JSON received from /attack_infrastructures endpoint"
        )

    if "attack_infrastructures" in knowledge:
        infrastructures = knowledge["attack_infrastructures"]
    else:
        raise Exception(
            "Cannot get attack infrastructure result from redteam API: invalid JSON received from /attack_infrastructures endpoint"
        )

    return infrastructures
