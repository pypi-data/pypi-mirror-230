from trigon.contrib.plugins import Plugin


class PluginBuilder:
    def __init__(self) -> None:
        self.plugins: list[Plugin] = []

    def add(self, plugin: Plugin):
        self.plugins.append(plugin)

        return self

    def _build(self) -> list[Plugin]:
        return self.plugins
