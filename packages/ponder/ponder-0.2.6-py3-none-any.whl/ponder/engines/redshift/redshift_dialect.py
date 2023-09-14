import hashlib

from ponder.core.dataframequerytreehelper import DFCaseFold
from ponder.engines.postgres.postgres_dialect import postgres_dialect


class redshift_dialect(postgres_dialect):
    def generate_autoincrement_type(self):
        return "BIGINT IDENTITY(0,1)"

    def generate_sanitized_name_upper(self, col_name):
        return self._generate_sanitized_name(col_name, DFCaseFold.UPPER)

    def generate_sanitized_name_lower(self, col_name):
        return self._generate_sanitized_name(col_name, DFCaseFold.LOWER)

    def generate_sanitized_name_none(self, col_name):
        return self._generate_sanitized_name(col_name, DFCaseFold.NO_FOLD)

    def _generate_sanitized_name(self, col_name, fold):
        ret_val = hashlib.shake_256(str(col_name).encode("utf-8")).hexdigest(6)
        if fold is DFCaseFold.UPPER:
            return f"F{ret_val.upper()}"
        if fold is DFCaseFold.LOWER:
            return f"f{ret_val.lower()}"
        return f"f{ret_val}"

    def format_name_upper(self, name):
        return self._format_name(name, DFCaseFold.UPPER)

    def format_name_lower(self, name):
        return self._format_name(name, DFCaseFold.LOWER)

    def format_name_none(self, name):
        return self._format_name(name, DFCaseFold.NO_FOLD)

    def _format_name(self, name, fold):
        if not isinstance(name, str):
            name = str(name)
        if self._obfuscate:
            # just doing something random to obfuscate.
            name = (
                hashlib.sha256(self._salt.encode() + name.encode()).hexdigest()
                + ":"
                + self._salt
            )

        if fold is DFCaseFold.UPPER:
            return f"{name.upper()}"
        if fold is DFCaseFold.LOWER:
            return f"{name.lower()}"
        return f"f{name}"
