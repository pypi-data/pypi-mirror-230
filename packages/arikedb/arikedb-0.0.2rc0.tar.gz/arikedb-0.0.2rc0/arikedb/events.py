from enum import Enum


class TagEvent(Enum):
    """Define all possible tag events"""

    ON_SET = "on_set"
    ON_CHANGE = "on_change"
    ON_RISING_EDGE = "on_rising_edge"
    ON_FALLING_EDGE = "on_falling_edge"
    ON_CROSS_LOW_THRESHOLD = "on_cross_low_threshold"
    ON_CROSS_HIGH_THRESHOLD = "on_cross_high_threshold"
    ON_RANGE_OUT = "on_range_out"
    ON_RANGE_IN = "on_range_in"
    ON_HIGH_POS_RATE = "on_high_pos_rate"
    ON_HIGH_NEG_RATE = "on_high_neg_rate"
