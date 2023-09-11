class ChainInstruction:
    def __init__(
        self,
        instruction_type,
        content=None,
        coordinate=None,
        priority=0,
        func=None,
        metadata=None,
    ):
        self.instruction_type = instruction_type
        self.content = content
        self.coordinate = coordinate
        self.priority = priority
        self.func = func
        self.metadata = metadata or {}

    def validate(self):
        """
        Validate the chain instruction to ensure all required fields are present and valid.
        """
        if not self.instruction_type:
            raise ValueError("The instruction_type field is required.")

        if not isinstance(self.instruction_type, str):
            raise TypeError("The instruction_type field must be a string.")

        if self.instruction_type == "custom":
            if not callable(self.func):
                raise ValueError(
                    "The 'func' field must be a callable function for custom instructions."
                )

        if self.content is not None and not isinstance(self.content, str):
            raise TypeError("The content field must be a string or None.")

        if self.coordinate is not None and not isinstance(self.coordinate):
            raise TypeError(
                "The coordinate field must be an instance of the Coordinate class or None."
            )

        if not isinstance(self.priority, int):
            raise TypeError("The priority field must be an integer.")

        if self.priority < 0:
            raise ValueError("The priority field must be a non-negative integer.")

        if not isinstance(self.metadata, dict):
            raise TypeError("The metadata field must be a dictionary.")

    def to_dict(self):
        """
        Convert the chain instruction to a dictionary representation.
        """
        instruction_dict = {
            "instruction_type": self.instruction_type,
            "content": self.content,
            "coordinate": self.coordinate.dict() if self.coordinate else None,
            "priority": self.priority,
            "func": self.func,
            "metadata": self.metadata,
        }
        return instruction_dict

    @classmethod
    def from_dict(cls, instruction_dict):
        """
        Create a ChainInstruction instance from a dictionary representation.
        """
        if not isinstance(instruction_dict, dict):
            raise TypeError("The instruction_dict must be a dictionary.")

        instruction_type = instruction_dict.get("instruction_type")
        content = instruction_dict.get("content")
        coordinate = instruction_dict.get("coordinate")
        priority = instruction_dict.get("priority", 0)
        func = instruction_dict.get("func")
        metadata = instruction_dict.get("metadata")

        return cls(instruction_type, content, coordinate, priority, func, metadata)

    def __repr__(self):
        """
        Return a string representation of the ChainInstruction object.
        """
        return (
            f"ChainInstruction(instruction_type={self.instruction_type}, content={self.content}, "
            f"coordinate={self.coordinate}, priority={self.priority}, func={self.func}, metadata={self.metadata})"
        )

    def __eq__(self, other):
        """
        Check if two ChainInstruction objects are equal.
        """
        if isinstance(other, ChainInstruction):
            return (
                self.instruction_type == other.instruction_type
                and self.content == other.content
                and self.coordinate == other.coordinate
                and self.priority == other.priority
                and self.func == other.func
                and self.metadata == other.metadata
            )
        return False

    def add_metadata(self, key, value):
        """
        Add a metadata entry to the ChainInstruction.
        """
        self.metadata[key] = value

    def remove_metadata(self, key):
        """
        Remove a metadata entry from the ChainInstruction based on the given key.
        """
        if key in self.metadata:
            del self.metadata[key]

    def get_metadata(self, key, default=None):
        """
        Get the value of a metadata entry from the ChainInstruction based on the given key.
        If the key is not found, return the default value.
        """
        return self.metadata.get(key, default)

    def has_metadata(self, key):
        """
        Check if the ChainInstruction has a metadata entry with the given key.
        """
        return key in self.metadata

    def clear_metadata(self):
        """
        Clear all metadata entries from the ChainInstruction.
        """
        self.metadata = {}
