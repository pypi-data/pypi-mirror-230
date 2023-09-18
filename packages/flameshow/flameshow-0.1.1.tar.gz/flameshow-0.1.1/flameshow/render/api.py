import logging
from .span import Span
from .flame_graph_widget import FlameGraphWidget

from textual.app import App, ComposeResult
from textual.widgets import Header, Footer

logger = logging.getLogger(__name__)


class FlameGraphApp(App):
    BINDINGS = [("d", "toggle_dark", "Toggle dark mode")]

    DEFAULT_CSS = """
    Span {
        width: 100%;
        height: 1;
    }

    Span:hover {
        text-style: reverse bold;
    }
    """

    def __init__(self, root_stack, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.root_stack = root_stack

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        yield FlameGraphWidget(self.root_stack, "100%")
        yield Footer()


def render_stack(root):
    app = FlameGraphApp(root)
    app.run()
