from collections import defaultdict


class Id:
    @staticmethod
    def with_id(klass):
        class Wrapped(klass):
            _id_counts = defaultdict(int)

            def __init__(self, *args, id=None, **kwargs):
                self._id = id
                if not isinstance(self, tuple):
                    super().__init__(*args, **kwargs)

            @classmethod
            def _new_id(_, klass):
                name = klass.__class__.__name__
                idx = Wrapped._id_counts[name]
                Wrapped._id_counts[name] += 1
                id = f"{name}_{idx}"
                return id

            @property
            def id(self):
                if self._id is None:
                    self._id = Wrapped._new_id(self)
                return self._id

        Wrapped.__qualname__ = klass.__qualname__
        Wrapped.__name__ = klass.__name__

        return Wrapped
