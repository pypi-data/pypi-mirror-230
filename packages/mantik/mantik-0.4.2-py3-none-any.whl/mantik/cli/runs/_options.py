import pathlib
import uuid

import click


class NotRequiredIf(click.Option):
    def __init__(self, *args, **kwargs):
        self.not_required_if = kwargs.pop("not_required_if")
        assert self.not_required_if, "'not_required_if' parameter required"
        kwargs["help"] = (
            f"{kwargs.get('help', '')} "
            f"NOTE: This argument is mutually "
            f"exclusive with {self.not_required_if}"
        )
        super().__init__(*args, **kwargs)

    def handle_parse_result(self, ctx, opts, args):
        we_are_present = self.name in opts
        other_present = self.not_required_if in opts

        if other_present:
            if we_are_present:
                raise click.UsageError(
                    f"Illegal usage: `{self.name}` is mutually "
                    f"exclusive with `{self.not_required_if}`"
                )
            else:
                self.prompt = None

        return super().handle_parse_result(ctx, opts, args)


class UuidParamType(click.ParamType):
    name = "uuid_type"

    def convert(self, value, param, ctx):
        try:
            return uuid.UUID(value)
        except ValueError:
            self.fail(
                f"{value!r} is not a valid hexadecimal UUID string", param, ctx
            )


API_URL = click.option(
    "--api-url",
    type=str,
    required=False,
    default=None,
    help="UNICORE API URL.",
)
BACKEND_CONFIG_ABSOLUTE = click.option(
    "--backend-config",
    type=click.Path(dir_okay=False, resolve_path=True, path_type=pathlib.Path),
    required=False,
    default=None,
    prompt=True,
    cls=NotRequiredIf,
    not_required_if="api_url",
    help="Absolute path to the backend config to read the API URL from.",
)
UNICORE_CONNECTION_ID = click.option(
    "--connection-id",
    required=False,
    default=None,
    type=UuidParamType(),
    help="Connection ID of your UNICORE Connection stored on Mantik. "
    "This is preferred over using env vars.",
)
