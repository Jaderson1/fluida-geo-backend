import logging


def setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    # Quiet the very chatty per-request access log; problem responses are
    # logged explicitly instead (see main.py's log_problem_responses).
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
