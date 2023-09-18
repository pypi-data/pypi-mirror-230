import logging
from rich.style import Style
from textual import RenderableType
from textual.widget import Widget
from rich.text import Text
from textual.widgets import Static

logger = logging.getLogger(__name__)


class Span(Widget):

    def __init__(self, s_width, s_text, s_color, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.s_text = s_text
        self.s_color = s_color

    def on_mount(self) -> None:
        self.styles.background = self.s_color

        # TODO tooptip render
        self.tooltip = self.s_text

    def render(self) -> RenderableType:
        # actuall, just display self.s_text will still work
        dispaly_text = self.s_text
        t = Text(dispaly_text, style=Style(bgcolor=self.s_color))

        return t
