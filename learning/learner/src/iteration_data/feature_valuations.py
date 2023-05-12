from typing import List
from dataclasses import dataclass


@dataclass
class FeatureValuation:
    s_idx: int
    boolean_feature_valuations: List[bool]
    numerical_feature_valuations: List[int]

    def __hash__(self):
        return hash(tuple(self.boolean_feature_valuations + self.numerical_feature_valuations))

    def __eq__(self, other):
        return self.boolean_feature_valuations == other.boolean_feature_valuations and \
               self.numerical_feature_valuations == other.numerical_feature_valuations

    def __str__(self):
        return str(self.s_idx) + ": " + str(self.boolean_feature_valuations) + " " + str(self.numerical_feature_valuations)
