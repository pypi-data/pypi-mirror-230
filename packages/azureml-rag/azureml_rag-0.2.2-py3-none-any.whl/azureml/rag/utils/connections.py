# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""MLIndex auth connection utilities."""
import json
import re
from typing import Optional, Union

from azureml.rag.utils.logging import get_logger
from azureml.rag.utils.requests import create_session_with_retry, send_post_request

try:
    from azure.ai.generative import AIClient
    from azure.ai.generative.entities import Connection
except Exception:
    AIClient = None
    Connection = None
try:
    from azure.ai.ml import MLClient
    from azure.ai.ml.entities import WorkspaceConnection
except Exception:
    MLClient = None
    WorkspaceConnection = None
try:
    from azure.core.credentials import TokenCredential
except Exception:
    TokenCredential = object

logger = get_logger("connections")


def get_connection_credential(config):
    """Get a credential for a connection."""
    try:
        from azure.core.credentials import AzureKeyCredential
    except ImportError as e:
        raise ValueError(
            "Could not import azure-core python package. "
            "Please install it with `pip install azure-core`."
        ) from e
    try:
        from azure.identity import DefaultAzureCredential
    except ImportError as e:
        raise ValueError(
            "Could not import azure-identity python package. "
            "Please install it with `pip install azure-identity`."
        ) from e
    if config.get("connection_type", None) == "workspace_keyvault":
        from azureml.core import Run, Workspace
        run = Run.get_context()
        if hasattr(run, "experiment"):
            ws = run.experiment.workspace
        else:
            try:
                ws = Workspace(
                    subscription_id=config.get("connection", {}).get("subscription"),
                    resource_group=config.get("connection", {}).get("resource_group"),
                    workspace_name=config.get("connection", {}).get("workspace")
                )
            except Exception as e:
                logger.warning(f"Could not get workspace '{config.get('connection', {}).get('workspace')}': {e}")
                # Fall back to looking for key in environment.
                import os
                key = os.environ.get(config.get("connection", {}).get("key"))
                if key is None:
                    raise ValueError(f"Could not get workspace '{config.get('connection', {}).get('workspace')}' and no key named '{config.get('connection', {}).get('key')}' in environment")
                return AzureKeyCredential(key)

        keyvault = ws.get_default_keyvault()
        credential = AzureKeyCredential(keyvault.get_secret(config.get("connection", {}).get("key")))
    elif config.get("connection_type", None) == "workspace_connection":
        connection_id = config.get("connection", {}).get("id")
        connection = get_connection_by_id_v2(connection_id)
        credential = connection_to_credential(connection)
    elif config.get("connection_type", None) == "environment":
        import os
        key = os.environ.get(config.get("connection", {}).get("key", "OPENAI_API_KEY"))
        credential = DefaultAzureCredential() if key is None else AzureKeyCredential(key)
    else:
        credential = DefaultAzureCredential()
    return credential


def connection_to_credential(connection: Union[dict, Connection, WorkspaceConnection]):
    """Get a credential for a workspace connection."""
    if isinstance(connection, dict):
        props = connection["properties"]
        auth_type = props.get("authType", props.get("AuthType"))
        if auth_type == "ApiKey":
            from azure.core.credentials import AzureKeyCredential
            return AzureKeyCredential(props["credentials"]["key"])
        elif auth_type == "PAT":
            from azure.core.credentials import AccessToken
            return AccessToken(props["credentials"]["pat"], props.get("expiresOn", None))
        elif auth_type == "CustomKeys":
            # OpenAI connections are made with CustomKeys auth, so we can try to access the key using known structure
            from azure.core.credentials import AzureKeyCredential
            if connection.get("metadata", {}).get("azureml.flow.connection_type", None) == "OpenAI":
                # Try to get the the key with api_key, if fail, default to regular CustomKeys handling
                try:
                    key = props["credentials"]["keys"]["api_key"]
                    return AzureKeyCredential(key)
                except Exception as e:
                    logger.warning(f"Could not get key using api_key, using default handling: {e}")
            key_dict = props["credentials"]["keys"]
            if len(key_dict.keys()) != 1:
                raise ValueError(f"Only connections with a single key can be used. Number of keys present: {len(key_dict.keys())}")
            return AzureKeyCredential(props["credentials"]["keys"][list(key_dict.keys())[0]])
        else:
            raise ValueError(f"Unknown auth type '{auth_type}'")
    elif isinstance(connection, WorkspaceConnection):
        if connection.credentials.type.lower() == "api_key":
            from azure.core.credentials import AzureKeyCredential
            return AzureKeyCredential(connection.credentials.key)
        elif connection.credentials.type.lower() == "pat":
            from azure.core.credentials import AccessToken
            return AccessToken(connection.credentials.pat, connection.credentials.expires_on)
        elif connection.credentials.type.lower() == "custom_keys":
            if connection._metadata.get("azureml.flow.connection_type", "").lower() == "openai":
                from azure.core.credentials import AzureKeyCredential
                try:
                    key = connection.credentials.keys.api_key
                    return AzureKeyCredential(key)
                except Exception as e:
                    logger.warning(f"Could not get key using api_key, using default handling: {e}")
            key_dict = connection.credentials.keys
            if len(key_dict.keys()) != 1:
                raise ValueError(f"Only connections with a single key can be used. Number of keys present: {len(key_dict.keys())}")
            return AzureKeyCredential(connection.credentials.keys[list(key_dict.keys())[0]])
        else:
            raise ValueError(f"Unknown auth type '{connection.credentials.type}' for connection '{connection.name}'")
    else:
        if connection.credentials.type.lower() == "api_key":
            from azure.core.credentials import AzureKeyCredential
            return AzureKeyCredential(connection.credentials.key)
        else:
            raise ValueError(f"Unknown auth type '{connection.credentials.type}' for connection '{connection.name}'")


def get_connection_by_id_v2(connection_id: str, credential: TokenCredential = None, client: str = "sdk") -> Union[dict, WorkspaceConnection, Connection]:
    """
    Get a connection by id using azure.ai.ml or azure.ai.generative.

    If azure.ai.ml is installed, use that, otherwise use azure.ai.generative.
    """
    uri_match = re.match(r"/subscriptions/(.*)/resourceGroups/(.*)/providers/Microsoft.MachineLearningServices/workspaces/(.*)/connections/(.*)", connection_id, flags=re.IGNORECASE)

    if uri_match is None:
        logger.error(f"Invalid connection_id {connection_id}, expecting Azure Machine Learning resource ID")
        raise ValueError(f"Invalid connection id {connection_id}")

    logger.info(f"Getting workspace connection: {uri_match.group(4)}")

    if credential is None:
        from azure.identity import DefaultAzureCredential
        from azureml.rag.utils.azureml import AzureMLRunCredential

        credential = AzureMLRunCredential() if AzureMLRunCredential.in_run() else DefaultAzureCredential()

    logger.info(f"Using auth: {type(credential)}")

    if AzureMLRunCredential.in_run():
        # Until we have a way to get the region specific azureml endpoint
        client = "rest"

    if client == "sdk" and MLClient is not None:
        logger.info("Getting workspace connection via MLClient")
        ml_client = MLClient(
            credential=credential,
            subscription_id=uri_match.group(1),
            resource_group_name=uri_match.group(2),
            workspace_name=uri_match.group(3)
        )
        if not AzureMLRunCredential.in_run():
            logger.info("Not in run, getting Connection from MFE")
            connection = ml_client.connections.get(uri_match.group(4))
        else:
            # TODO: When in Run need to get region specific azureml endpoint
            # Can maybe copy this: `endpoint = workspace.service_context._get_endpoint("api")``
            raise NotImplementedError("Using MLClient in Run is not implemented yet.")
            # logger.info("In run, getting Connection via list_secrets")
            # connection = None

        if connection is None or connection.credentials.key is None:
            from azure.ai.ml._azure_environments import _get_aml_resource_id_from_metadata
            old_base_url = ml_client.connections._operation._client._base_url
            if connection is None:
                ml_client.connections._operation._client._base_url = f"{_get_aml_resource_id_from_metadata()}/rp/workspaces"

                list_secrets_response = ml_client.connections._operation.list_secrets(
                    connection_name=uri_match.group(4),
                    resource_group_name=ml_client.resource_group_name,
                    workspace_name=ml_client.workspace_name,
                )

                connection = WorkspaceConnection(
                    target=list_secrets_response.properties.target,
                    type=list_secrets_response.properties.category,
                    credentials=list_secrets_response.properties.credentials,
                    metadata=list_secrets_response.metadata,
                )
                logger.info(f"Manually constructed Connection: {connection}")
            else:
                list_secrets_response = ml_client.connections._operation.list_secrets(
                    connection_name=uri_match.group(4),
                    resource_group_name=ml_client.resource_group_name,
                    workspace_name=ml_client.workspace_name,
                )
                connection.credentials.key = list_secrets_response.properties.credentials.key

            ml_client.connections._operation._client._base_url = old_base_url

    elif client == "sdk" and AIClient is not None:
        logger.info("Getting workspace connection via AIClient")
        ai_client = AIClient(
            credential=credential,
            subscription_id=uri_match.group(1),
            resource_group_name=uri_match.group(2),
            project_name=uri_match.group(3)
        )
        connection = ai_client.connections.get(uri_match.group(4))
    else:
        logger.info("Getting workspace connection via REST as fallback")
        return get_connection_by_id_v1(connection_id, credential)

    return connection


def get_id_from_connection(connection: Union[dict, WorkspaceConnection, Connection]) -> str:
    """Get a connection id from a connection."""
    if isinstance(connection, dict):
        return connection["id"]
    elif isinstance(connection, WorkspaceConnection):
        return connection.id
    elif isinstance(connection, Connection):
        return connection.id
    else:
        raise ValueError(f"Unknown connection type: {type(connection)}")


def get_connection_by_name_v2(workspace, name: str) -> dict:
    """Get a connection from a workspace."""
    if hasattr(workspace._auth, "get_token"):
        bearer_token = workspace._auth.get_token("https://management.azure.com/.default").token
    else:
        bearer_token = workspace._auth.token

    endpoint = workspace.service_context._get_endpoint("api")
    url = f"{endpoint}/rp/workspaces/subscriptions/{workspace.subscription_id}/resourcegroups/{workspace.resource_group}/providers/Microsoft.MachineLearningServices/workspaces/{workspace.name}/connections/{name}/listsecrets?api-version=2023-02-01-preview"
    resp = send_post_request(url, {
        "Authorization": f"Bearer {bearer_token}",
        "content-type": "application/json"
    }, {})

    return resp.json()


def get_connection_by_id_v1(connection_id: str, credential: Optional[TokenCredential] = None) -> dict:
    """Get a connection from a workspace."""
    uri_match = re.match(r"/subscriptions/(.*)/resourceGroups/(.*)/providers/Microsoft.MachineLearningServices/workspaces/(.*)/connections/(.*)", connection_id)

    if uri_match is None:
        logger.error(f"Invalid connection_id {connection_id}, expecting Azure Machine Learning resource ID")
        raise ValueError(f"Invalid connection id {connection_id}")

    from azureml.core import Run, Workspace
    run = Run.get_context()
    if hasattr(run, "experiment"):
        ws = run.experiment.workspace
    else:
        try:
            ws = Workspace(
                subscription_id=uri_match.group(1),
                resource_group=uri_match.group(2),
                workspace_name=uri_match.group(3)
            )
        except Exception as e:
            logger.warning(f"Could not get workspace '{uri_match.group(3)}': {e}")
            raise ValueError(f"Could not get workspace '{uri_match.group(3)}'") from e

    return get_connection_by_name_v2(ws, uri_match.group(4))


def send_put_request(url, headers, payload):
    """Send a PUT request."""
    with create_session_with_retry() as session:
        response = session.put(url, data=json.dumps(payload), headers=headers)
        # Raise an exception if the response contains an HTTP error status code
        response.raise_for_status()

    return response.json()


def create_connection_v2(workspace, name, category: str, target: str, auth_type: str, credentials: dict, metadata: str):
    """Create a connection in a workspace."""
    url = f"https://management.azure.com/subscriptions/{workspace.subscription_id}/resourcegroups/{workspace.resource_group}/providers/Microsoft.MachineLearningServices/workspaces/{workspace.name}/connections/{name}?api-version=2023-04-01-preview"

    resp = send_put_request(url, {
        "Authorization": f"Bearer {workspace._auth.get_token('https://management.azure.com/.default').token}",
        "content-type": "application/json"
    }, {
        "properties": {
            "category": category,
            "target": target,
            "authType": auth_type,
            "credentials": credentials,
            "metadata": metadata
        }
    })

    return resp
