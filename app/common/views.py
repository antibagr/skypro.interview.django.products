from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.urls import Resolver404
from loguru import logger


def _log_request(request: HttpRequest, status_code: int) -> None:
    with logger.contextualize(path=request.path, method=request.method, meta=request.META):
        logger.error("HTTP {} {} '{}'", status_code, request.method, request.path)


def handler404(
    request: HttpRequest,
    exception: Resolver404,  # noqa: U100
    template_name: str = "errors/404.html",
) -> HttpResponse:
    _log_request(request, 404)
    return render(request, template_name)


def handler500(request: HttpRequest) -> HttpResponse:
    _log_request(request, 500)
    return render(request, "errors/50x.html")
