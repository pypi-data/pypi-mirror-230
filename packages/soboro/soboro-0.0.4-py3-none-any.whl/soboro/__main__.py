def main():
    from mousse import get_logger
    from .cli import cli

    package_name, *_ = __name__.split(".")
    logger = get_logger(package_name)
    logger.include_extra = False
    logger.add_handler("RotatingFileHandler", path=f"logs/{package_name}.out")

    cli()


if __name__ == "__main__":
    main()
