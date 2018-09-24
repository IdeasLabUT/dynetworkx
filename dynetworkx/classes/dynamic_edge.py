from __future__ import division
"""
    Base class for dynamic edges
"""

class DynamicEdge(object):
    def __init__(self, start_time, end_time, **attrs):
        """
        Parameters
        ----------
        start_time: offset-based
        end_time: offset-based
        Returns
        -------
        """

        self.attributes = attrs
        self.start_time = start_time
        self.end_time   = end_time

    def within_snapshot_window(self, snapshot_start, snapshot_end):
        if self.end_time >= snapshot_start and self.end_time <= snapshot_end:
            return True
        if self.start_time <= snapshot_end and self.start_time >= snapshot_start:
            return True
        if self.start_time >= snapshot_start and self.end_time <= snapshot_end:
            return True
        if self.start_time < snapshot_start and self.end_time > snapshot_end:
            return True
        return False

    def weight_within_snapshot_window(self, snapshot_start, snapshot_end, duration):
        start_time = max(snapshot_start, self.start_time)
        end_time = min(snapshot_end, self.end_time)
        return  (end_time - start_time) / duration
