# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Functions for interacting with AzureML."""
import datetime
import os
from typing import Any, Dict, List, Optional

from azure.core.credentials import AccessToken
from azureml.rag.utils.logging import get_logger

logger = get_logger("utils.azureml")


class AzureMLRunCredential:
    """Credential for AzureML Run."""

    def __init__(self):
        """Initialize the credential."""
        pass

    def get_token(
        self, *scopes: str, claims: Optional[str] = None, tenant_id: Optional[str] = None, **kwargs: Any
    ) -> AccessToken:
        """Get an AzureML RunToken from the environment."""
        import os
        token = os.environ.get("AZUREML_RUN_TOKEN")
        token_expiry_time = os.environ.get(
            "AZUREML_RUN_TOKEN_EXPIRY",
            AzureMLRunCredential._parse_expiry_time_from_token(token)
        )
        # TODO: Handle encryption of RunToken, see `AzureMLTokenAuthentication._token_encryption_enabled` in `azureml.core.authentication`
        # TODO: Handle refresh if expiring soon. Main usage for now is at Run startup so _should_ be fine.
        return AccessToken(token, token_expiry_time)

    @staticmethod
    def _parse_expiry_time_from_token(token):
        import jwt
        # We set verify=False, as we don't have keys to verify signature, and we also don't need to
        # verify signature, we just need the expiry time.
        decode_json = jwt.decode(token, options={"verify_signature": False, "verify_aud": False})
        return AzureMLRunCredential._convert_to_datetime(decode_json["exp"])

    @staticmethod
    def _convert_to_datetime(expiry_time):
        if isinstance(expiry_time, datetime.datetime):
            return expiry_time

        return datetime.datetime.fromtimestamp(int(expiry_time))

    @staticmethod
    def in_run():
        """Check if we are running in AzureML."""

        return os.environ.get("AZUREML_RUN_TOKEN") is not None

    def close(self) -> None:
        """Close the credential."""
        pass


def get_workspace_from_environment():
    """Get the workspace from the run context if running in Azure, otherwise return None."""
    from azureml.core import Run

    run = Run.get_context()
    if hasattr(run, "experiment"):
        # We are running in Azure
        return run.experiment.workspace
    else:
        return None


def get_secret_from_workspace(name: str, workspace=None) -> str:
    """Get a secret from the workspace if running in Azure, otherwise get it from the environment."""
    secrets = get_secrets_from_workspace([name], workspace)
    return secrets[name]


def get_secrets_from_workspace(names: List[str], workspace=None) -> Dict[str, str]:
    """Get a secret from the workspace if running in Azure, otherwise get it from the environment."""
    import os

    ws = get_workspace_from_environment() if workspace is None else workspace
    if ws:
        keyvault = ws.get_default_keyvault()
        secrets = keyvault.get_secrets(names)
        logger.info("Run context and secrets retrieved", extra={"print": True})
    else:
        secrets = {}
        for name in names:
            secrets[name] = os.environ.get(name, os.environ.get(name.replace("-", "_")))

    return secrets
