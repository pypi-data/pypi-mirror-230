class SessionMetaData(dict):
    def __getattr__(self, name):
        if name in self:
            return self[name]
        else:
            raise AttributeError(f"'SessionMetaData' object has no attribute '{name}'")

    def __setattr__(self, name, value):
        self[name] = value