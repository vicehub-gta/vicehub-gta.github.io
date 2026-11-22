"""Encrypt the Premium vault for the members page.

Usage: python3 tools/seal.py <plaintext.json> <passphrase-file>
Writes content/premium/vault.json (AES-256-GCM, key from PBKDF2-SHA256).
The plaintext and the passphrase never go into this repository.
"""
import base64, json, os, sys
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

ITER = 250_000
src, pwfile = sys.argv[1], sys.argv[2]
data = json.dumps(json.load(open(src, encoding="utf-8")), ensure_ascii=False, separators=(",", ":")).encode()
pw = open(pwfile, encoding="utf-8").read().strip().encode()
salt, iv = os.urandom(16), os.urandom(12)
key = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=ITER).derive(pw)
ct = AESGCM(key).encrypt(iv, data, None)
b = lambda x: base64.b64encode(x).decode()
out = os.path.join(os.path.dirname(__file__), "..", "content", "premium", "vault.json")
json.dump({"v": 1, "iter": ITER, "salt": b(salt), "iv": b(iv), "ct": b(ct)}, open(out, "w"))
print(f"sealed {len(data)} bytes -> {os.path.normpath(out)}")
