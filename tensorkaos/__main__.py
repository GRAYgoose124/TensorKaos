from .window import TensorKaos
from .utilities.misc import setup_logging


def main():
    setup_logging()

    app = TensorKaos()
    app.run()


if __name__ == "__main__":
    main()
