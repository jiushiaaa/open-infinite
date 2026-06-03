"""v0.4 read-only worldline browser."""

__all__ = ["start_browser_server"]


def __getattr__(name: str):
    if name == "start_browser_server":
        from living_novel_engine.browser.server import start_browser_server

        return start_browser_server
    raise AttributeError(name)
