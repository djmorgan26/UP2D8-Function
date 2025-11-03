import logging
import structlog

def configure_logger():
    # Configure standard logging to capture warnings and errors
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    structlog.configure(
        processors=[
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    # Optionally, configure the root logger to use structlog
    # This ensures that any log messages from libraries also get processed by structlog
    # handler = logging.StreamHandler()
    # formatter = structlog.stdlib.ProcessorFormatter(
    #     processor=structlog.dev.ConsoleRenderer(),
    #     foreign_pre_chain=[
    #         structlog.stdlib.add_logger_name,
    #         structlog.stdlib.add_log_level,
    #         structlog.processors.TimeStamper(fmt="iso"),
    #     ],
    # )
    # handler.setFormatter(formatter)
    # root_logger = logging.getLogger()
    # root_logger.addHandler(handler)
    # root_logger.setLevel(logging.INFO)

# Call this function at the start of your application or function app
