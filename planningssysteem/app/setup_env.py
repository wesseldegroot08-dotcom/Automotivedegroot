"""Maak een .env-bestand als het er nog niet is, met een willekeurige geheime sleutel."""

import secrets

from app.config import BASIS_MAP


def main() -> None:
    env = BASIS_MAP / ".env"
    if env.exists():
        return
    tekst = (BASIS_MAP / ".env.example").read_text(encoding="utf-8")
    tekst = tekst.replace("GEHEIME_SLEUTEL=verander-mij", f"GEHEIME_SLEUTEL={secrets.token_urlsafe(32)}")
    env.write_text(tekst, encoding="utf-8")
    print(".env gemaakt (met een nieuwe geheime sleutel).")


if __name__ == "__main__":
    main()
