import ssl
import socket
import requests
from datetime import datetime, timezone, timedelta
from urllib3.exceptions import InsecureRequestWarning

# Désactive les avertissements SSL
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

def check_cert_expiry(hostname, port=443, alert_days=30, webhook_url=None):
    """
    Vérifie la date d'expiration du certificat SSL
    """
    try:
        context = ssl.create_default_context()
        
        with socket.create_connection((hostname, port), timeout=5) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()
                expiry_str = cert['notAfter']
                expiry_date = datetime.strptime(expiry_str, '%b %d %H:%M:%S %Y %Z').replace(tzinfo=timezone.utc)
                days_left = (expiry_date - datetime.now(timezone.utc)).days
                
                # Formatage de la date pour l'affichage
                formatted_date = expiry_date.strftime('%Y-%m-%d %H:%M:%S UTC')
                
                print(f"Vérification du certificat électronique sur le domaine : {hostname}")
                print(f"Le certificat pour {hostname} expire le {formatted_date} ({days_left} jours restants)")
                
                # Envoi systématique au webhook si configuré
                if webhook_url:
                    # Envoi de l'alerte standard
                    success = send_webhook_alert(
                        webhook_url, 
                        hostname, 
                        formatted_date, 
                        days_left,
                        is_critical=(days_left < alert_days)
                    )
                    
                    if success:
                        print("Alerte envoyée au webhook.")
                    else:
                        print("Échec de l'envoi au webhook")
                
                if days_left < alert_days:
                    print(f"ATTENTION : Certificat expire dans {days_left} jours !")
                else:
                    print("Le certificat est encore valide suffisamment longtemps.")
                
    except Exception as e:
        error_msg = f"Erreur lors de la vérification du certificat pour {hostname}: {e}"
        print(error_msg)
        if webhook_url:
            success = send_webhook_alert(webhook_url, hostname, error_message=error_msg)
            if success:
                print("Alerte d'erreur envoyée au webhook.")

def send_webhook_alert(webhook_url, hostname, expiry_date=None, days_left=None, error_message=None, is_critical=False):
    """
    Envoie une notification SSL au webhook
    Retourne True si réussi, False si échec
    """
    try:
        if error_message:
            message = {
                "content": f"❌ ERREUR - Vérification certificat SSL\n"
                          f"**Domaine**: {hostname}\n"
                          f"**Erreur**: {error_message}"
            }
        else:
            if is_critical:
                message = {
                    "content": f"ALERTE CRITIQUE, Le Certificat SSL expire bientôt"
                              f", Le domaine: {hostname}"
                              f", la date d'expiration: {expiry_date}"
                              f", Le nombre de jours restants: {days_left} (CRITIQUE)"
                              f", Action requise: Renouvellement urgent nécessaire!"
                }
            else:
                message = {
                    "content": f"ℹInformation - Certificat SSL"
                              f"**Domaine**: {hostname}"
                              f"**Expiration**: {expiry_date}"
                              f"**Jours restants**: {days_left}"
                }
        
        response = requests.post(
            webhook_url, 
            json=message, 
            verify=False, 
            timeout=10
        )
        
        # Vérifie que le statut HTTP est 2xx
        response.raise_for_status()
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"[ERREUR] Échec envoi webhook: {str(e)}")
        return False
    except Exception as e:
        print(f"[ERREUR] Problème inattendu: {str(e)}")
        return False