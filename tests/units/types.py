from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any, Protocol

    from django.contrib.auth.models import AbstractUser
    from django.http import HttpResponse

    class Response(HttpResponse):
        context: dict[str, Any]
        url: str

    class Client(Protocol):  # noqa: F811
        """
        Typed version of django.test.client.Client
        """

        def get(self, path: str, **extra: Any) -> Response:  # noqa: U100
            ...

        def force_login(self, user: AbstractUser, backend: Any = None) -> None:  # noqa: U100
            ...

else:
    from django.test.client import Client


__all__ = [
    "Client",
]
