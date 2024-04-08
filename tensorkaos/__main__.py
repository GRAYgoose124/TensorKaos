from .window import TensorKaos
from .core.utilities import setup_logging


def main():
    setup_logging()

    app = TensorKaos()
    app.run()


if __name__ == "__main__":
    main()
