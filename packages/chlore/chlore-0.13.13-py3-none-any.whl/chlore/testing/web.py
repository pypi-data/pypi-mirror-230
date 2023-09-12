from contextlib import contextmanager
from typing import cast

from fastapi.testclient import TestClient
import requests

from .dependencies import override_dependency


@contextmanager
def capture_jinja_context(app, jinja_mixin):
    capture_context = {}
    original_render = jinja_mixin.render

    def render(self, template: str, context: dict, **kwargs) -> dict:
        capture_context.update(context)
        return original_render(self, template, context=context, **kwargs)

    try:
        jinja_mixin.render = render
        yield capture_context
    finally:
        jinja_mixin = original_render


class WebTestResponse(requests.Response):
    def __init__(self, req: requests.Response, jinja_context: dict):
        super().__init__()
        for k, v in req.__dict__.items():
            self.__dict__[k] = v
        self.jinja_context = jinja_context


class WebTestClient(TestClient):
    """
    A TestClient subclass specialized to test web applications
    """

    def __init__(self, *args, jinja_mixin, **kwargs):
        super().__init__(*args, **kwargs)
        self.jinja_mixin = jinja_mixin

    @staticmethod
    def _add_default_kwargs(kw):
        kw.setdefault("follow_redirects", False)
        return kw

    def request(self, *args, **kwargs) -> WebTestResponse:
        kwargs = self._add_default_kwargs(kwargs)
        with capture_jinja_context(self.app, self.jinja_mixin) as context:
            resp = super().request(*args, **kwargs)
            return WebTestResponse(resp, context)

    def get(self, *args, **kwargs) -> WebTestResponse:
        kwargs = self._add_default_kwargs(kwargs)
        return cast(WebTestResponse, super().get(*args, **kwargs))

    def post(self, *args, **kwargs) -> WebTestResponse:
        kwargs = self._add_default_kwargs(kwargs)
        return cast(WebTestResponse, super().post(*args, **kwargs))

    def put(self, *args, **kwargs) -> WebTestResponse:
        kwargs = self._add_default_kwargs(kwargs)
        return cast(WebTestResponse, super().put(*args, **kwargs))

    def delete(self, *args, **kwargs) -> WebTestResponse:
        kwargs = self._add_default_kwargs(kwargs)
        return cast(WebTestResponse, super().put(*args, **kwargs))
