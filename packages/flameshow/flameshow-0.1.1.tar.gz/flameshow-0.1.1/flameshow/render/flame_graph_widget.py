import logging
from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.widgets import Static

from .span import Span
from random import randbytes

logger = logging.getLogger(__name__)


def random_color():
    return f"#{randbytes(3).hex()}"


class FlameGraphWidget(Static):
    DEFAULT_CSS = """
    FlameGraphWidget {
      layout: vertical;
    }
    """

    def __init__(self, root_stack, my_width, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.root_stack = root_stack
        self.my_width = my_width

    def compose(self) -> ComposeResult:
        yield self.render_current()
        yield self.render_children()

    def on_mount(self) -> None:
        self.styles.width = self.my_width

    def render_current(self):
        return Span(self.my_width, self.root_stack.name, random_color())

    def render_children(self):
        total = sum([c.value for c in self.root_stack.children])

        widgets = []
        for child in self.root_stack.children:
            w = round(child.value / total * 100)
            style_w = f"{w:.2f}%"
            widgets.append(FlameGraphWidget(child, style_w))

        return Horizontal(*widgets)
