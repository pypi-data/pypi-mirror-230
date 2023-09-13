import base64
import json
from datetime import datetime, timedelta

from cryptography.fernet import Fernet, InvalidSignature, InvalidToken

from pyauthorizer.encryptor.base import BaseEncryptor, License, LicenseStatus
from pyauthorizer.encryptor.utils import generate_key


class SimpleEncryptor(BaseEncryptor):
    def __init__(self):
        super().__init__()

    def generate_license(self, data: dict):
        """
        Generate a license with the given data.

        Args:
            data (dict): The data to include in the license.

        Returns:
            License: The generated license.
        """
        secret_key = generate_key()
        license_data = {
            "user_data": data,
            "expiry_date": str(datetime.now() + timedelta(days=30)),
        }
        base64_data = base64.urlsafe_b64encode(json.dumps(license_data).encode("utf-8"))
        token = Fernet(secret_key).encrypt(base64_data)
        return License(
            secret_key=secret_key.decode("utf-8"),
            token=token.decode("utf-8"),
        )

    def validate_license(self, license: License, data: dict):
        """
        Validate the given license.

        Args:
            license (License): The license to validate.
            data (dict): The data to generate the license from.

        Returns:
            LicenseStatus: The status of the license (ACTIVE, EXPIRED, or INVALID).
        """
        try:
            cipher = Fernet(license.secret_key.encode("utf-8"))
            decrypted_token = cipher.decrypt(license.token.encode("utf-8"))
            decoded_data = base64.urlsafe_b64decode(decrypted_token)
            license_data: dict = json.loads(decoded_data)
            user_data: dict = license_data["user_data"]
            for key, value in user_data.items():
                if key not in data or value != data[key]:
                    return LicenseStatus.INVALID
        except (InvalidToken, InvalidSignature):
            return LicenseStatus.INVALID
        if "expiry_date" not in license_data:
            return LicenseStatus.INVALID
        expiry_date = datetime.fromisoformat(license_data["expiry_date"])
        current_date = datetime.now()
        if expiry_date > current_date:
            return LicenseStatus.ACTIVE
        return LicenseStatus.EXPIRED
