
import os
import logging
from datetime import datetime, timezone
from flask import Flask, request, render_template_string, redirect, url_for

app = Flask(__name__)

# --- Logging setup ---
LOG_DIR = os.environ.get("LOG_DIR", "logs")
os.makedirs(LOG_DIR, exist_ok=True)
log_path = os.path.join(LOG_DIR, "form.log")

logger = logging.getLogger("form_logger")
logger.setLevel(logging.INFO)
if not logger.handlers:
    fh = logging.FileHandler(log_path)
    fmt = logging.Formatter('%(message)s')
    fh.setFormatter(fmt)
    logger.addHandler(fh)

FORM_HTML = """
<!doctype html>
<html lang="fr">
<head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Formulaire simple</title>
    <style>
        body { font-family: system-ui, -apple-system, Segoe UI, Roboto, sans-serif; margin: 2rem; }
        form { max-width: 420px; display: grid; gap: 0.75rem; }
        label { font-weight: 600; }
        input { padding: 0.6rem 0.75rem; border: 1px solid #ddd; border-radius: 8px; }
        button { padding: 0.7rem 0.9rem; border: 0; border-radius: 10px; cursor: pointer; }
        .primary { background: #111; color: white; }
        .card { padding: 1.25rem; border: 1px solid #eee; border-radius: 12px; }
        .muted { color: #555; font-size: 0.9rem; }
        .notice { background:#fff7cc; border:1px solid #f2e397; padding:0.75rem 1rem; border-radius:10px; }
    </style>
</head>
<body>
    <h1>Formulaire</h1>
    <div class="card notice">
        ⚠️ Par sécurité, ce service <strong>ne journalise pas</strong> les mots de passe en clair par défaut.
        Vous pouvez activer ce comportement (déconseillé) en définissant <code>LOG_PASSWORDS=true</code>.
    </div>
    <form method="post" action="/">
        <div>
            <label for="username">Utilisateur</label><br>
            <input id="username" name="username" type="text" required autocomplete="username" />
        </div>
        <div>
            <label for="password">Mot de passe</label><br>
            <input id="password" name="password" type="password" required autocomplete="current-password" />
        </div>
        <div>
            <button class="primary" type="submit">Envoyer</button>
        </div>
        <p class="muted">Les soumissions sont journalisées dans <code>%(log_path)s</code> à l'intérieur du conteneur.</p>
    </form>
</body>
</html>
""" % {"log_path": log_path}

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        username = (request.form.get("username") or "").replace("\n", " ").strip()
        password = request.form.get("password") or ""

        # Decide whether to log the password (not recommended)
        log_passwords = os.getenv("LOG_PASSWORDS", "false").lower() == "true"

        client_ip = request.headers.get("X-Forwarded-For", request.remote_addr) or ""
        user_agent = request.headers.get("User-Agent", "")[:300]

        entry = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "username": username,
            "client_ip": client_ip,
            "user_agent": user_agent,
            "password_length": len(password)
        }
        if log_passwords:
            entry["password"] = password  # ⚠️ Not recommended!

        logger.info(entry)

        return redirect(url_for("thanks"))
    return render_template_string(FORM_HTML)

@app.route("/merci")
def thanks():
    return "<p>Merci ! Les informations ont été enregistrées dans le journal.</p>"

if __name__ == "__main__":
    # For local testing only (inside Docker we use gunicorn)
    app.run(host="0.0.0.0", port=8000)
