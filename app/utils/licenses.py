ALLOWED = {"cc-by", "cc-by-sa", "mit", "apache-2.0"}

def allowed(lic: str) -> bool:
    if not lic: return False
    s = lic.strip().lower()
    return any(s.startswith(x) for x in ALLOWED)
