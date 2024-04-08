from .title import TitleView
from .pause import PauseView
from .gridgame import GridGameView

# re-export all views
__all__ = [v for v in locals() if v.endswith("View")]
