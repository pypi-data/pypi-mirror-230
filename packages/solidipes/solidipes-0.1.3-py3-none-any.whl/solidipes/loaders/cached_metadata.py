from operator import attrgetter

from ..utils import get_cached_metadata, set_cached_metadata
from .data_container import DataContainer


class CachedMetadata(DataContainer):
    # Format is { key in metadata.yaml : attribute path }
    cached_metadata_fields = {}
    _cached_metadata = None

    def __init__(self):
        DataContainer.__init__(self)
        self.load_cached_metadata()

    def get_cached_metadata(self):
        if CachedMetadata._cached_metadata is None:
            CachedMetadata._cached_metadata = get_cached_metadata()
        if self.unique_identifier not in CachedMetadata._cached_metadata:
            CachedMetadata._cached_metadata[self.unique_identifier] = {}
        return CachedMetadata._cached_metadata[self.unique_identifier]

    def write_cached_metadata(self):
        set_cached_metadata(CachedMetadata._cached_metadata)

    @property
    def _modified_time(self):
        raise NotImplementedError

    def load_cached_metadata(self):
        """Load cached metadata and put in _data_collection (as attributes)"""

        cached_metadata = self.get_cached_metadata()
        # print("cached_metadata:", cached_metadata)
        # Check if update is necessary
        cache_modified_time = cached_metadata.get("modified_time", 0)
        if cache_modified_time < self._modified_time:
            cached_metadata = self.update_cached_metadata()

        # Update _data_collection
        for key, value in cached_metadata.items():
            self.add(key, value)

        return cached_metadata

    def update_cached_metadata(self):
        cached_metadata = self.get_cached_metadata()
        # Update cache with cached_metadata_fields
        for key, attribute_path in self.cached_metadata_fields.items():
            cached_metadata[key] = attrgetter(attribute_path)(self)

        self.write_cached_metadata()
        return cached_metadata

    def set_cached_metadata_entry(self, key, value):
        cached_metadata = self.get_cached_metadata()
        cached_metadata[key] = value
        self.add(key, value)
        self.write_cached_metadata()

    def save_field_to_cache(self, key):
        cached_metadata = self.get_cached_metadata()
        cached_metadata[key] = getattr(self, key)
        self.write_cached_metadata()
