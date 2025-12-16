import json
from pathlib import Path

PROFILE_CACHE = {}

def load_profiles(base_path: str = "profiles"):
    """
    Load profiles/{partner}/{version}/profile.json into memory.
    """
    base = Path(base_path)

    for partner_dir in base.iterdir():
        if partner_dir.is_dir():
            partner = partner_dir.name

            for version_dir in partner_dir.iterdir():
                if version_dir.is_dir():
                    edi_version = version_dir.name
                    profile_file = version_dir / "profile.json"

                    if profile_file.exists():
                        key = (partner.upper(), edi_version)
                        PROFILE_CACHE[key] = json.loads(profile_file.read_text())

    print(f"Loaded {len(PROFILE_CACHE)} partner profiles.")

    if PROFILE_CACHE.get("global", 'default') is None:
        return False
    return True


def get_profile(partner: str, version: str):
    """
    Retrieve a loaded profile from memory.
    """
    profile =  PROFILE_CACHE.get((partner, version), None)
    if profile is None:
        profile = PROFILE_CACHE.get((partner, "default"), None)
        if profile is None:
            profile = PROFILE_CACHE.get(("global", "default"), None)
    if profile is None:
        raise ValueError(f"No profile found for partner '{partner}' with version '{version}'")
    return profile
