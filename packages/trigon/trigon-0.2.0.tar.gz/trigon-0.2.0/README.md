<h1 align="center">Trigon</h1>

<p align="center"><em>A batteries-included python web framework</em></p>

<p align="center">
  <!-- <a href="https://www.python.org/">
    <img
      src="https://img.shields.io/pypi/pyversions/trigon"
      alt="PyPI - Python Version"
    />
  </a>
  <a href="https://pypi.org/project/trigon/">
    <img
      src="https://img.shields.io/pypi/v/trigon"
      alt="PyPI"
    />
  </a>
  <a href="https://github.com/billsioros/trigon/actions/workflows/ci.yml">
    <img
      src="https://github.com/billsioros/trigon/actions/workflows/ci.yml/badge.svg"
      alt="CI"
    />
  </a> -->
  <a href="https://github.com/billsioros/trigon/actions/workflows/cd.yml">
    <img
      src="https://github.com/billsioros/trigon/actions/workflows/cd.yml/badge.svg"
      alt="CD"
    />
  </a>
  <a href="https://results.pre-commit.ci/latest/github/billsioros/trigon/master">
    <img
      src="https://results.pre-commit.ci/badge/github/billsioros/trigon/master.svg"
      alt="pre-commit.ci status"
    />
  </a>
  <!-- <a href="https://codecov.io/gh/billsioros/trigon">
    <img
      src="https://codecov.io/gh/billsioros/trigon/branch/master/graph/badge.svg?token=coLOL0j6Ap"
      alt="Test Coverage"/>
  </a> -->
  <!-- <a href="https://opensource.org/licenses/MIT">
    <img
      src="https://img.shields.io/pypi/l/trigon"
      alt="PyPI - License"
    />
  </a> -->
  <a href="https://vscode.dev/redirect?url=vscode://ms-vscode-remote.remote-containers/cloneInVolume?url=https://github.com/billsioros/trigon">
    <img
      src="https://img.shields.io/static/v1?label=Dev%20Containers&message=Open&color=blue&logo=visualstudiocode"
      alt="Open in GitHub Codespaces"
    />
  </a>
  <a href="https://app.renovatebot.com/dashboard#github/billsioros/trigon">
    <img
      src="https://img.shields.io/badge/renovate-enabled-brightgreen.svg?style=flat&logo=renovatebot"
      alt="Renovate - Enabled">
  </a>
  <a href="https://github.com/billsioros/trigon/actions/workflows/dependency_review.yml">
    <img
      src="https://github.com/billsioros/trigon/actions/workflows/dependency_review.yml/badge.svg"
      alt="Dependency Review"
    />
  </a>
  <a href="https://github.com/billsioros/cookiecutter-pypackage">
    <img
      src="https://img.shields.io/badge/cookiecutter-template-D4AA00.svg?style=flat&logo=cookiecutter"
      alt="Cookiecutter Template">
  </a>
  <a href="https://www.buymeacoffee.com/billsioros">
    <img
      src="https://img.shields.io/badge/Buy%20me%20a-coffee-FFDD00.svg?style=flat&logo=buymeacoffee"
      alt="Buy me a coffee">
  </a>
</p>

## :rocket: Getting started

> **Attention**: The project is a work in progress and should not be used in production :construction:

Installing [`trigon`](https://pypi.org/project/trigon/) can be done as such:

```shell
pip install trigon
```

The project's documentation can be found [here](https://billsioros.github.io/trigon/).

```python
from typing import Any, Dict

import uvicorn
from trigon.core.controller import Controller, http, route
from trigon.core.controller.result import Ok, Result
from trigon.trigon import trigon


class ItemService:
    def get_items(self) -> list[Dict[str, Any]]:
        return [
            {
                "id": 1,
                "name": "Product 1",
                "description": "This is the description for Product 1.",
                "price": 19.99,
                "category": "Electronics",
                "stock": 50,
            },
            {
                "id": 2,
                "name": "Product 2",
                "description": "A sample description for Product 2.",
                "price": 29.99,
                "category": "Clothing",
                "stock": 100,
            },
            {
                "id": 3,
                "name": "Product 3",
                "description": "Description for Product 3 goes here.",
                "price": 9.99,
                "category": "Books",
                "stock": 25,
            },
        ]


class ItemController(Controller):
    def __init__(self, service: ItemService) -> None:
        self.service = service

    @route.get("/")
    @http.status(Ok)
    async def get_items(self) -> Result[list[Dict[str, Any]]]:
        return Ok(self.service.get_items())


if __name__ == "__main__":
    app = (
        trigon()
        .build_container(lambda builder: builder.singleton(ItemService))
        .register_controllers(ItemController)
        .configure_logging(
            lambda builder: builder.override("uvicorn")
            .register_middleware()
            .add_console_handler()
            .add_file_handler("logs/{time}.log"),
        )
        .build()
    )

    uvicorn.run(app, host="0.0.0.0", port=8000)
```

> For a more elaborate example (controller discovery, database configuration, Repository-Service Pattern, etc.) check out [Example 02](./examples/example_02/).

## :sparkles: Contributing

If you would like to contribute to the project, please go through the [Contributing Guidelines](https://billsioros.github.io/trigon/latest/CONTRIBUTING/) first. In order to locally set up the project please follow the instructions below:

```shell
# Set up the GitHub repository
git clone https://github.com/billsioros/trigon.git

# Create a virtual environment using poetry and install the required dependencies
poetry shell
poetry install

# Install pre-commit hooks
pre-commit install --install-hooks
```

Alternatively, you can support the project by [**Buying me a ☕**](https://www.buymeacoffee.com/billsioros).
