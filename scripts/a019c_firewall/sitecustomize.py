"""Opt-in bootstrap for the A019C-R2 synthetic validation process tree."""
import os

if os.environ.get("MALECNS_A019C_R2_FIREWALL") == "1":
    try:
        from validation_firewall import install
        install()
    except BaseException:
        # Python otherwise prints and ignores sitecustomize failures.
        os._exit(78)
