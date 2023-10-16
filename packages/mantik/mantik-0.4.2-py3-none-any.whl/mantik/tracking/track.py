import logging

import mantik.authentication.auth as auth
import mantik.tracking.environment as _environment
import mantik.utils as utils

logger = logging.getLogger(__name__)


def init_tracking() -> _environment.Environment:
    """Authenticate to the MLflow Tracking Server.

    Returns
    -------
    Environment
        Holds the environment variables required for tracking.

    Notes
    -----
    MLflow prioritizes the username and password environment variables over
    the token variable, causing an `Unauthorized` error. As a consequence,
    these have to be unset before setting the token variable.

    The tokens will be stored in a file `~/.mantik/tokens.json` to reuse
    tokens and refresh them only if they have expired.

    """
    logger.debug("Authenticating at the Mantik platform")
    token = auth.get_valid_access_token()
    environment = _environment.Environment(token=token)
    utils.mlflow.unset_conflicting_env_vars()
    utils.env.set_env_vars(environment.to_dict())
    logger.debug("Authentication successful")
    return environment
