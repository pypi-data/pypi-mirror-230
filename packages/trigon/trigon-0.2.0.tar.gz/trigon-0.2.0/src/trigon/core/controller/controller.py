import inspect

from fastapi import APIRouter


class Controller:
    def as_view(self):
        entity = f"{self.__class__.__name__.replace('Controller', '')}s"

        self.router = APIRouter(prefix=f"/{entity.lower()}", tags=[entity.title()])

        for name, endpoint in inspect.getmembers(self, inspect.ismethod):
            if hasattr(endpoint, "_http_method"):
                method = endpoint._http_method
                prefix = endpoint._prefix
                status_code = endpoint._status_code
                responses = endpoint._responses

                setattr(
                    self,
                    name,
                    self.router.add_api_route(
                        prefix,
                        endpoint,
                        methods=[method],
                        status_code=status_code,
                        responses=responses,
                    ),
                )

        return self.router
