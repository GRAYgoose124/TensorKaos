from ..guiview import GuiView


class PrimaryView(GuiView):
    def __init__(self, window=None):
        super().__init__(window, "primary", "Primary View")
