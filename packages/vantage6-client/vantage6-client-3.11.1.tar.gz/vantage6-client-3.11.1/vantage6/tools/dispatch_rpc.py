import os
import importlib
import jwt
import traceback

from typing import Any

from vantage6.client import ContainerClient
from vantage6.client.algorithm_client import AlgorithmClient
from vantage6.tools.util import info, warn, error


def dispatch_rpc(data: Any, input_data: dict, module: str, token: str,
                 use_new_client: bool = False, log_traceback=False) -> Any:
    """
    Load the algorithm module and call the correct method to run an algorithm.

    Parameters
    ----------
    data : Any
        The data that is passed to the algorithm.
    input_data : dict
        The input data that is passed to the algorithm. This should at least
        contain the key 'method' which is the name of the method that should be
        called. Another often used key is 'master' which indicates that this
        container is a master container. Other keys depend on the algorithm.
    module : str
        The name of the module that contains the algorithm.
    token : str
        The JWT token that is used to authenticate from the algorithm container
        to the server.
    use_new_client : bool, optional
        Whether to use the new client or the old client, by default False
    log_traceback: bool, optional
        Whether to print the full error message from algorithms or not, by
        default False. Algorithm developers should only use this option if
        they are sure that the error message does not contain any sensitive
        information. By default False.

    Returns
    -------
    Any
        The result of the algorithm.
    """
    # import algorithm module
    try:
        lib = importlib.import_module(module)
        info(f"Module '{module}' imported!")
    except ModuleNotFoundError:
        error(f"Module '{module}' can not be imported! Exiting...")
        exit(1)

    # in case of a master container, we have to do a little extra
    master = input_data.get("master")
    if master:
        info("Running a master-container")
        # read env
        host = os.environ["HOST"]
        port = os.environ["PORT"]
        api_path = os.environ["API_PATH"]

        # init Docker Client
        # TODO In v4+ we should always use the new client, delete option then
        if use_new_client:
            client = AlgorithmClient(token=token, host=host, port=port,
                                     path=api_path)
        else:
            client = ContainerClient(token=token, host=host, port=port,
                                     path=api_path)

        # read JWT token, to log te collaboration id. The
        # AlgorithmClient automatically sets the collaboration_id
        claims = jwt.decode(token, options={"verify_signature": False})

        # Backwards comptability from < 3.3.0
        if 'identity' in claims:
            id_ = claims['identity']['collaboration_id']
        elif 'sub' in claims:
            id_ = claims['sub']['collaboration_id']

        info(f"Working with collaboration_id <{id_}>")

        method_name = input_data["method"]

    else:
        info("Running a regular container")
        method_name = f"RPC_{input_data['method']}"

    # attempt to load the method
    try:
        method = getattr(lib, method_name)
    except AttributeError:
        warn(f"method '{method_name}' not found!\n")
        exit(1)

    # get the args and kwargs input for this function.
    args = input_data.get("args", [])
    kwargs = input_data.get("kwargs", {})

    # try to run the method
    try:
        result = method(client, data, *args, **kwargs) if master else \
                 method(data, *args, **kwargs)
    except Exception as e:
        error(f"Error encountered while calling {method_name}: {e}")
        if log_traceback:
            error(traceback.print_exc())
        exit(1)

    return result
