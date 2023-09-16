

class cached_property(object):

    class unset(object):
        pass

    UNSET = unset()

    def __init__(self, func):
        self.func = func
        self.value = self.UNSET

    def __get__(self, instance, cls=None):

        if instance is None:
            return self

        if isinstance(self.value, self.unset):
            self.value = self.func(instance)

        return self.value
