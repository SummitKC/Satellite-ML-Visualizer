"""End-to-end training: load -> clean -> features -> split -> fit -> evaluate -> save.

    python -m ml.train --model gbm
"""

import argparse
import logging

logger = logging.getLogger(__name__)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", choices=["baseline", "gbm"], default="gbm")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    # 1. ml.data.loader.load_joined()
    # 2. ml.data.cleaning.clean()
    # 3. ml.features.build.build_training_set()
    # 4. ml.data.splits.time_split()
    # 5. fit baseline and args.model; ml.evaluate.evaluate() both on test
    # 6. save model + metrics JSON to ml.config.ARTIFACT_DIR
    raise NotImplementedError


if __name__ == "__main__":
    main()
