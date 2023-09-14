from typing import List, Optional, Tuple, Union

from promptquality.constants.scorers import Scorers
from promptquality.types.custom_scorer import CustomScorer


def bifurcate_scorers(
    scorers: Optional[List[Union[Scorers, CustomScorer]]] = None
) -> Tuple[List[Scorers], List[CustomScorer]]:
    if scorers is None:
        return [], []
    galileo_scorers = []
    custom_scorers = []
    for scorer in scorers:
        if isinstance(scorer, Scorers):
            galileo_scorers.append(scorer)
        elif isinstance(scorer, CustomScorer):
            custom_scorers.append(scorer)
        else:
            raise ValueError(f"Unknown scorer type: {type(scorer)}.")
    return galileo_scorers, custom_scorers
