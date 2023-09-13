import abc
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict


class LicenseStatus(Enum):
    """
    Enum representing the status of a license.
    """

    ACTIVE = 1
    EXPIRED = 2
    INVALID = 3


@dataclass
class License:
    """
    Class representing a license.
    """

    secret_key: str
    token: str
    reversed: Dict[str, Any] = field(default_factory=dict)


class BaseEncryptor(abc.ABC):
    """
    Abstract base class for encryptors.
    """

    @abc.abstractmethod
    def generate_license(self, data: dict) -> License:
        """
        Generate a license based on the provided data.

        Args:
            data (dict): The data to generate the license from.

        Returns:
            License: The generated license.
        """

    @abc.abstractmethod
    def validate_license(self, license: License, data: dict) -> LicenseStatus:
        """
        Validate the provided license.

        Args:
            license (License): The license to validate.
            data (dict): The data to generate the license from.

        Returns:
            LicenseStatus: The status of the license.
        """
