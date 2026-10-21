"""Prepared one-pair helper; no automatic controller construction or execution."""

from stage_3 import _motion_cycle


def open_close_pair(record, serial, controller, stage_3_review, *, open_seconds):
    """One initial Close, Open, approved added hold, Close and guarded cleanup.

    Requires separate launch authority and reviewed Stage-3 physical evidence.
    Added hold begins after Open feedback; it is not a maximum exposure bound.
    No prompt, retry or automatic advancement occurs while Open.
    """
    return _motion_cycle(
        record, serial, controller, stage_3_review, stage=4, open_seconds=open_seconds
    )
