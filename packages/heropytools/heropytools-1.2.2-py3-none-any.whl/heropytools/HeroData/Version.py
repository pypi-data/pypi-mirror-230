# *************************************************************** #
#               Copyright © Hero Imaging AB 2022. 				  #
#  					  All Rights Reserved.						  #
# *************************************************************** #

class Version:
    def __init__(self, major: int, minor: int, build: int = None, revision: int = None):
        if major is None or minor is None:
            raise ValueError("Major and minor version must always be provided.")
        self.major = major
        self.minor = minor
        self.build = build
        self.revision = revision

    def __lt__(self, other):
        return self._cmp(other, lambda x, y: x < y, False)

    def __le__(self, other):
        return self._cmp(other, lambda x, y: x <= y, True)

    def __gt__(self, other):
        return self._cmp(other, lambda x, y: x > y, False)

    def __ge__(self, other):
        return self._cmp(other, lambda x, y: x >= y, True)

    def _cmp(self, other, operator, allow_equality: bool):
        if operator(self.major, other.major):
            if allow_equality:
                if not self.major == other.major:
                    return True
            else:
                return True

        if operator(self.minor, other.minor):
            if allow_equality:
                if not self.major == other.major:
                    return True
            else:
                return True

        if operator(self._value_or_default(self.build), self._value_or_default(other.build)):
            if allow_equality:
                if not self._value_or_default(self.build) == self._value_or_default(other.build):
                    return True
            else:
                return True

        return operator(self._value_or_default(self.revision), self._value_or_default(other.revision))

    @staticmethod
    def _value_or_default(value) -> int:
        if value is None:
            return 0
        else:
            return value

    @staticmethod
    def from_string(s: str):
        v = s.split(sep='.')
        return Version(*v)

    def __str__(self) -> str:
        version_str = f"{self.major}.{self.minor}"
        if self.build is not None:
            version_str += f".{self.build}"
            if self.revision is not None:
                version_str += f".{self.revision}"
        return version_str
