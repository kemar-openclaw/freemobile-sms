"""Typer CLI for the Free Mobile SMS client."""

from __future__ import annotations

import typer

from .client import FreeMobileClient, FreeMobileClientError
from .settings import FreeMobileSettings

app = typer.Typer(
    name="freemobile-sms",
    help="Send SMS notifications via the Free Mobile API.",
    no_args_is_help=True,
)


@app.callback()
def main() -> None:
    """Free Mobile SMS — send SMS notifications via the Free Mobile API."""


@app.command()
def send(
    message: str = typer.Argument(help="The text message to send (max 480 characters)."),
    user: str | None = typer.Option(
        None,
        "--user",
        "-u",
        envvar="FREE_MOBILE_USER",
        help="Free Mobile customer ID.",
    ),
    password: str | None = typer.Option(
        None,
        "--password",
        "-p",
        envvar="FREE_MOBILE_PASSWORD",
        help="Free Mobile API key.",
    ),
    api_url: str = typer.Option(
        "https://smsapi.free-mobile.fr/sendmsg",
        "--api-url",
        envvar="FREE_MOBILE_API_URL",
        help="Free Mobile SMS API URL.",
    ),
    method: str = typer.Option(
        "GET",
        "--method",
        "-m",
        help="HTTP method: GET or POST. POST avoids URL-encoding the message.",
    ),
) -> None:
    """Send an SMS notification via the Free Mobile API.

    Credentials can be provided via --user/--password options or the
    FREE_MOBILE_USER / FREE_MOBILE_PASSWORD environment variables.

    Examples:

        \b
        # Using environment variables
        $ export FREE_MOBILE_USER=12345678
        $ export FREE_MOBILE_PASSWORD=myApiKey
        $ freemobile-sms send "Hello from CLI!"

        \b
        # Using options
        $ freemobile-sms send "Hello!" --user 12345678 --password myApiKey

        \b
        # Using POST (no URL-encoding needed)
        $ freemobile-sms send "Hello!" --method POST -u 12345678 -p myApiKey
    """
    settings = FreeMobileSettings(
        user=user or "",
        password=password or "",
        api_url=api_url,
    )

    with FreeMobileClient(settings=settings) as client:
        try:
            result = client.send(message, method=method)
        except FreeMobileClientError as exc:
            typer.echo(f"Error: {exc}", err=True)
            raise typer.Exit(code=1) from exc

    if result.ok:
        typer.echo(f"✓ {result.message}")
    else:
        typer.echo(f"✗ {result.message}", err=True)
        raise typer.Exit(code=1)


if __name__ == "__main__":  # pragma: no cover
    app()
