import base64
import json
from datetime import datetime, timedelta

from cryptography.fernet import Fernet, InvalidSignature, InvalidToken, MultiFernet

from pyauthorizer.encryptor.base import BaseEncryptor, License, LicenseStatus
from pyauthorizer.encryptor.utils import generate_key


class MultiEncryptor(BaseEncryptor):
    def __init__(self):
        super().__init__()

    def generate_license(self, data: dict):
        """
        Generate a license based on given data.

        Args:
            data (dict): The data to be included in the license.

        Returns:
            License: The generated license object.
        """
        key_nums = int(data["key_nums"])
        secret_keys = [generate_key() for _ in range(key_nums)]
        license_data = {
            "user_data": data,
            "expiry_date": str(datetime.now() + timedelta(days=30)),
        }
        base64_data = base64.urlsafe_b64encode(json.dumps(license_data).encode("utf-8"))
        token = MultiFernet([Fernet(k) for k in secret_keys]).encrypt(base64_data)
        return License(
            secret_key=" ".join([k.decode("utf-8") for k in secret_keys]),
            token=token.decode("utf-8"),
        )

    def validate_license(self, license: License, data: dict):
        """
        Validate a given license.

        Args:
            license (License): The license to be validated.
            data (dict): The data to generate the license from.

        Returns:
            LicenseStatus: The status of the license (ACTIVE, EXPIRED, or INVALID).
        """
        try:
            cipher = MultiFernet([Fernet(k) for k in license.secret_key.split()])
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
