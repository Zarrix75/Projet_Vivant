# Checker module
# src/checker.py

import requests
from logger import log_event
from notifier import send_email, send_webhook

def check_sites(sites, config):
    """
    Vérifie la disponibilité des sites
    """
    for site in sites:
        try:
            response = requests.get(
                site["url"], 
                timeout=10, 
                verify=False,
                headers={'User-Agent': 'Mozilla/5.0'}
            )
            
            if response.status_code not in config.get("error_codes", []):
                log_event(f"{site['url']} est disponible (code: {response.status_code}).")
            else:
                msg = f"{site['url']} est indisponible (code: {response.status_code})."
                log_event(msg)
                trigger_alert(site['name'], msg, config)
                
        except requests.RequestException as e:
            error_msg = "est hors ligne."
            if "Failed to resolve" in str(e):
                error_msg = "est hors ligne."
            elif "timed out" in str(e):
                error_msg = "est hors ligne (timeout)."
    
            msg = f"{site['url']} {error_msg}"
            log_event(msg)
            trigger_alert(site['name'], msg, config)

def trigger_alert(site_name, message, config):
    """
    Déclenche les alertes
    """
    send_email(
        subject=f"Alerte indisponibilité : {site_name}",
        content=message,
        config=config
    )
    send_webhook(message, config)