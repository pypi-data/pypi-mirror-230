"""Type hints (stub file) for the classes and functions exported from rust."""

from datetime import datetime
from enum import Enum
from typing import Any, Callable, List, Optional, Sequence, Union, Tuple

class SftpOpts:
    base_path: str
    host: str
    port: int
    username: str
    envelope_dir: Optional[str]
    filename: Optional[str]
    pkey: Optional[str]
    pkey_password: Optional[str]
    buf_size: Optional[int]

    def __init__(
        self,
        base_path: str,
        host: str,
        port: int,
        username: str,
        envelope_dir: Optional[str] = None,
        filename: Optional[str] = None,
        pkey: Optional[str] = None,
        pkey_password: Optional[str] = None,
        buf_size: Optional[int] = None,
    ) -> None: ...

class S3Opts:
    endpoint: str
    bucket: str
    region: str
    profile: Optional[str]
    access_key: Optional[str]
    secret_key: Optional[str]
    session_token: Optional[str]

    def __init__(
        self,
        endpoint: str,
        bucket: str,
        region: str = "",
        profile: Optional[str] = None,
        access_key: Optional[str] = None,
        secret_key: Optional[str] = None,
        session_token: Optional[str] = None,
    ) -> None: ...

class CompressionAlgorithm(Enum):
    Stored: None
    Gzip: None
    Zstandard: None

class LocalOpts:
    output: Optional[str]

    def __init__(self, output: Optional[str] = None) -> None: ...

class EncryptOpts:
    dry_run: bool
    files: Sequence[str]
    force: bool
    recipients: Sequence[bytes]
    compression_algorithm: Optional[CompressionAlgorithm]
    compression_level: Optional[int]
    max_cpu: Optional[int]
    password: Optional[str]
    purpose: Optional[str]
    signer: Optional[bytes]
    transfer_id: Optional[int]

    def __init__(
        self,
        dry_run: bool,
        files: Sequence[str],
        force: bool,
        recipients: Sequence[bytes],
        compression_algorithm: Optional[
            CompressionAlgorithm
        ] = CompressionAlgorithm.Zstandard,
        compression_level: Optional[int] = None,
        max_cpu: Optional[int] = None,
        password: Optional[str] = None,
        purpose: Optional[str] = None,
        signer: Optional[bytes] = None,
        transfer_id: Optional[int] = None,
    ) -> None: ...

class DecryptOpts:
    decrypt_only: bool
    dry_run: bool
    file: str
    recipients: Sequence[bytes]
    signer: bytes
    max_cpu: Optional[int]
    output: Optional[str]
    password: Optional[str]

    def __init__(
        self,
        decrypt_only: bool,
        dry_run: bool,
        file: str,
        recipients: Sequence[bytes],
        signer: bytes,
        max_cpu: Optional[int] = None,
        output: Optional[str] = None,
        password: Optional[str] = None,
    ) -> None: ...

def transfer(
    files: Sequence[str],
    destination: Union[S3Opts, SftpOpts],
    progress: Optional[Callable[[float], Any]] = None,
    two_factor_callback: Optional[Callable[[], str]] = None,
) -> None: ...
def encrypt(
    opts: EncryptOpts,
    destination: Union[SftpOpts, LocalOpts],
    progress: Optional[Callable[[float], Any]] = None,
    two_factor_callback: Optional[Callable[[], str]] = None,
) -> Optional[str]: ...
def decrypt(
    opts: DecryptOpts,
    progress: Optional[Callable[[float], Any]] = None,
) -> Optional[str]: ...

class KeyType(Enum):
    Public: Any
    Secret: Any

class CertType(Enum):
    Public: Any
    Secret: Any

class Validity(Enum):
    Condemned: Any
    Expired: Any
    Invalid: Any
    Revoked: Any
    Unknown: Any
    Valid: Any

class RevocationReason(Enum):
    Compromised: Any
    Superseded: Any
    Retired: Any
    Unspecified: Any

class UserID:
    value: bytes
    name: Optional[str]
    email: Optional[str]
    comment: Optional[str]

class Key:
    key_id: str
    key_type: KeyType
    fingerprint: str
    length: Optional[int]
    creation_date: datetime
    expiration_date: Optional[datetime]
    pub_key_algorithm: int
    validity: Validity
    revocation_reason: Optional[List[str]]

class CertInfo:
    email: str
    fingerprint: str
    key_id: str
    keys: List[Key]
    primary_key: Key
    subkeys: List[Key]
    uid: Optional[UserID]
    uids: List[UserID]
    validity: Validity

    @classmethod
    def from_bytes(cls, data: bytes, end_relax: Optional[int] = None) -> "CertInfo": ...

def create_revocation_signature(
    cert: bytes, reason: RevocationReason, message: bytes, password: bytes
) -> bytes: ...
def generate_cert(uid: str, password: bytes) -> Tuple[bytes, bytes]: ...

class CertStore:
    def import_cert(self, cert: bytes, cert_type: CertType) -> CertInfo: ...
    def export_cert(self, fingerprint: str, cert_type: CertType) -> bytes: ...
    def list_certs(self, cert_type: CertType) -> List[CertInfo]: ...
    def revoke(self, rev_sig: bytes) -> None: ...

class CertParsingError(Exception): ...

def gnupg_extract_cert(
    identifier: str, cert_type: CertType, gpg_home: Optional[str]
) -> bytes: ...
def gnupg_list_certs(cert_type: CertType, gpg_home: Optional[str]) -> List[str]: ...
def gnupg_list_certs_with_userid(
    cert_type: CertType, gpg_home: Optional[str]
) -> List[str]: ...
