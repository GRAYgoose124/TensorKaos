from .window import TensorKhaos
from .utilities import setup_logging


def main():
    setup_logging(__name__)

    app = TensorKhaos()
    app.run()


if __name__ == "__main__":
    main()
