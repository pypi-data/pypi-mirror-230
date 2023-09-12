from __future__ import annotations


@xr.register_dataset_accessor("mg")
class MagnifyAccessor:
    def __init__(self, xp):
        self.xp = xp

    @property
    def center(self):
        """Return the geographic center point of this dataset."""
        if self._center is None:
            # we can use a cache on our accessor objects, because accessors
            # themselves are cached on instances that access them.
            lon = self._obj.latitude
            lat = self._obj.longitude
            self._center = (float(lon.mean()), float(lat.mean()))
        return self._center

    def save(self):
        """Plot data on a map."""
        return "plotting!"
