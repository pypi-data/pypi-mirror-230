import dataclasses
import typing as t

import mantik.utils as utils


@dataclasses.dataclass
class Environment:
    """The required environment variables for tracking."""

    token: str

    def to_dict(self) -> t.Dict[str, str]:
        """Return as dict."""
        return {
            utils.mlflow.TRACKING_TOKEN_ENV_VAR: self.token,
        }

    def to_bash_statement(self, no_export: bool = False) -> str:
        """Return as a bash statement.

        Parameters
        ----------
        no_export : bool, default=False
            Whether to include the `export` command as a prefix.

        Returns
        -------
        str
            The environment variables as a bash statement.
            E.g. `export ENV_VAR=<value>`.

        """
        statement = f"{utils.mlflow.TRACKING_TOKEN_ENV_VAR}={self.token}"
        if no_export:
            return statement
        return f"export {statement}"
