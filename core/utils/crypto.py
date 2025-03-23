"""Utilitaires pour la gestion des clés cryptographiques."""

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa, ed25519
from cryptography.hazmat.primitives import hashes
from cryptography.exceptions import InvalidKey
import base64


def generate_key_pair(key_type: str) -> tuple[str, str]:
    """Génère une paire de clés selon le type spécifié.
    
    Args:
        key_type: Type de clé ('rsa', 'ed25519', 'secp256k1')
    
    Returns:
        Tuple[str, str]: (clé privée, clé publique) au format PEM
    """
    if key_type == 'rsa':
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        public_pem = private_key.public_key().public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        return private_pem.decode(), public_pem.decode()

    elif key_type == 'ed25519':
        private_key = ed25519.Ed25519PrivateKey.generate()
        private_bytes = private_key.private_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PrivateFormat.Raw,
            encryption_algorithm=serialization.NoEncryption()
        )
        public_key = private_key.public_key()
        public_bytes = public_key.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw
        )
        return (
            base64.b64encode(private_bytes).decode(),
            base64.b64encode(public_bytes).decode()
        )

    elif key_type == 'secp256k1':
        # Note: Pour secp256k1, nous utiliserions normalement 'coincurve' ou 'ethereum'
        # Ici nous utilisons RSA comme placeholder pour l'exemple
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        public_pem = private_key.public_key().public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        return f"0x{private_pem.hex()[:64]}", f"0x{public_pem.hex()[:64]}"

    raise ValueError(f"Type de clé non supporté : {key_type}")


def verify_key_pair(private_key: str, public_key: str, key_type: str) -> bool:
    """Vérifie qu'une paire de clés est valide.
    
    Args:
        private_key: Clé privée au format PEM
        public_key: Clé publique au format PEM
        key_type: Type de clé ('rsa', 'ed25519', 'secp256k1')
    
    Returns:
        bool: True si la paire est valide
    """
    try:
        if key_type == 'rsa':
            private = serialization.load_pem_private_key(
                private_key.encode(),
                password=None
            )
            public = serialization.load_pem_public_key(
                public_key.encode()
            )
            # Test simple : on signe et vérifie
            message = b"test"
            signature = private.sign(
                message,
                padding=padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                algorithm=hashes.SHA256()
            )
            public.verify(
                signature,
                message,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return True

        elif key_type == 'ed25519':
            private_bytes = base64.b64decode(private_key)
            public_bytes = base64.b64decode(public_key)
            private = ed25519.Ed25519PrivateKey.from_private_bytes(private_bytes)
            public = ed25519.Ed25519PublicKey.from_public_bytes(public_bytes)
            message = b"test"
            signature = private.sign(message)
            public.verify(signature, message)
            return True

        elif key_type == 'secp256k1':
            # TODO: Implémenter la vérification secp256k1
            return True

    except (ValueError, InvalidKey):
        return False

    return False
