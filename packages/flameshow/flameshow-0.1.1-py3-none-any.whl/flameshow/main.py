import json
import logging
import os
import time

from rich.traceback import Stack

from flameshow.parser import debug_root, parse_goroutine, parse_sample
from flameshow.render import render_stack


logger = logging.getLogger(__name__)


def setup_log(enabled, level, loglocation):
    if enabled:
        logging.basicConfig(
            filename=os.path.expanduser(loglocation),
            filemode="a",
            format="%(asctime)s %(levelname)5s (%(module)s) %(message)s",
            level=level,
        )
    else:
        logging.disable(logging.CRITICAL)
    logger.info("------ mactop ------")


def main():
    setup_log(True, logging.DEBUG, "luckyme.log")

    with open("goroutine.json") as f:
        pprof_data = json.load(f)

    t1 = time.time()
    root = parse_goroutine(pprof_data)
    t2 = time.time()
    logger.info("parse json files cost %s s", t2 - t1)

    render_stack(root)


if __name__ == "__main__":
    main()
