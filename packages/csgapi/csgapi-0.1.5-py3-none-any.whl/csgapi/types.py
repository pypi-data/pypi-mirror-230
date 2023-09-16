from .mixin import GetMixin, CreateMixin, UpdateMixin, ListMixin, DeleteMixin

class ForeignKeyManager(GetMixin, CreateMixin, UpdateMixin, ListMixin):
    pass


class Manager(ForeignKeyManager, DeleteMixin):
    pass