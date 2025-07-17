# Notifier module
# src/notifier.py

import smtplib                      # Module pour envoyer des emails via SMTP
from email.message import EmailMessage  # Classe pour créer des emails facilement
import requests

def send_email(subject, content, config):
    """
    Envoie un email d'alerte si l'option est activée dans la config.
    """
    email_cfg = config.get("alerts", {}).get("email", {})  # Récupère la config email
    if not email_cfg.get("enabled", False):                # Si l'alerte email n'est pas activée, on quitte
        return
    msg = EmailMessage()                                   # Crée un nouvel email
    msg["Subject"] = subject                              # Définit le sujet
    msg["From"] = email_cfg["username"]                   # Expéditeur
    msg["To"] = email_cfg["to"]                           # Destinataire
    msg.set_content(content)                              # Corps du message

    with smtplib.SMTP(email_cfg["smtp_server"], email_cfg["smtp_port"]) as server:  # Connexion au serveur SMTP
        server.starttls()                                 # Sécurise la connexion (TLS)
        server.login(email_cfg["username"], email_cfg["password"])  # Authentification
        server.send_message(msg)                          # Envoie l'email

def send_webhook(content, config):
    """
    Envoie une alerte via webhook si activé dans la config.
    """
    webhook_cfg = config.get("alerts", {}).get("webhook", {})  # Récupère la config webhook
    if not webhook_cfg.get("enabled", False):                  # Si l'alerte webhook n'est pas activée, on quitte
        return
    url = webhook_cfg.get("url")                               # Récupère l'URL du webhook
    if url:
        try:
            requests.post(url, json={"text": content}, timeout=5, verify=False)  # Envoie la requête POST au webhook
        except Exception as e:
            print(f"Erreur lors de l'envoi du webhook: {e}")       # Affiche l'erreur si l'envoi échoue

