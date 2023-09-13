class SessionMetaData(dict):
    """
    SessionMetaData is a subclass of Python's built-in dictionary that can be used to store miscellaneous session data.
    This data persists across requests and can be useful for storing session-specific information.

    Attributes:
        Inherits all attributes and methods of the dict class.

    Methods:
        - __getattr__(self, name): Custom method to access values using attribute-like syntax.
            If 'name' exists as a key in the dictionary, it returns the corresponding value.
            If 'name' is not a valid key, it raises an AttributeError.

        - __setattr__(self, name, value): Custom method to set values using attribute-like syntax.
            Sets 'name' as a key in the dictionary with 'value' as the corresponding value.

    Example:
        ```
        session_data = SessionMetaData()
        session_data.user_id = 123
        session_data.username = "john_doe"
        print(session_data.user_id)  # Accessing a stored value using attribute-like syntax.
        print(session_data['username'])  # Accessing a stored value using dictionary-like syntax.
        ```

    Note:
        This class allows you to work with session-specific data using a more intuitive attribute-style syntax
        while internally storing the data as a dictionary.
    """
    def __getattr__(self, name):
        if name in self:
            return self[name]
        else:
            raise AttributeError(f"'SessionMetaData' object has no attribute '{name}'")

    def __setattr__(self, name, value):
        self[name] = value