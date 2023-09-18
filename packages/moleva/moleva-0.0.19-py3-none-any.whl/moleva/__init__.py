from typing import Dict, List, Optional, Union
import os

from .libs import Evaluator


class MolEva:
    def __init__(self, model_dir: Union[str, os.PathLike]):
        """
        :param model_dir: model dir, include LICENSE file
        :return:
        """
        self.evaluator = Evaluator(model_dir)

    def dili(self, smiles: List[str]):
        results = self.evaluator.evaluate(smiles, "dili")
        return results[0]

    def car(self, smiles: List[str]):
        results = self.evaluator.evaluate(smiles, "car")
        return results[0]
