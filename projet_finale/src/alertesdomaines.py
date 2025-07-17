import requests
import time
import warnings
import urllib3
from datetime import datetime, timedelta

warnings.filterwarnings("ignore", category=urllib3.exceptions.InsecureRequestWarning)

WEBHOOK_URL = 'your_webhook_url_here'  # Remplacez par votre URL de webhook

def send_webhook_alert(message):
    """
    Envoie une alerte au webhook
    Args:
        message (str): Message à envoyer
    """
    payload = {"content": message}
    try:
        response = requests.post(WEBHOOK_URL, json=payload, verify=False)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Erreur webhook domaine : {e}")

def get_whois_data(domain):
    """
    Récupère les données WHOIS d'un domaine
    Args:
        domain (str): Domaine à analyser
    Returns:
        dict: Données WHOIS ou None en cas d'erreur
    """
    api_key = 'Your_API_Key_Here'  # Remplacez par votre clé API
    url = f'https://www.whoisxmlapi.com/whoisserver/WhoisService?apiKey={api_key}&domainName={domain}&outputFormat=JSON'

    try:
        response = requests.get(url, verify=False)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Erreur WHOIS domaine {domain}: {e}")
        return None

def check_expiry_alert(expiry_date, domain, registrar_name):
    """
    Vérifie si l'expiration est dans moins de 30 jours et envoie une alerte si nécessaire
    Args:
        expiry_date (datetime): Date d'expiration du domaine
        domain (str): Domaine analysé
        registrar_name (str): Nom du registrar
    """
    today = datetime.now()
    time_remaining = expiry_date - today
    
    if time_remaining < timedelta(days=30):
        days_remaining = time_remaining.days
        formatted_date = expiry_date.strftime('%Y-%m-%dT%H:%MZ')
        
        message = (f"ALERTE CRITIQUE - Expiration imminente : "
                  f"Le domaine {domain} expire dans {days_remaining} jours ({formatted_date}). "
                  f"Registrar: {registrar_name}")
        send_webhook_alert(message)

def extract_domain_info(whois_data, domain):
    """
    Extrait et envoie les informations d'expiration du domaine
    Args:
        whois_data (dict): Données WHOIS
        domain (str): Domaine analysé
    """
    if whois_data:
        registry_data = whois_data.get('WhoisRecord', {}).get('registryData', {})
        expires_date = registry_data.get('expiresDate')
        registrar_name = registry_data.get('registrarName')

        if expires_date:
            # Formatage de la date (JJ-MM-AAAA HH:MMZ)
            expiry_date = datetime.strptime(expires_date, '%Y-%m-%dT%H:%M:%SZ')
            formatted_date = expiry_date.strftime('%Y-%m-%dT%H:%MZ')
            
            # Envoi de l'alerte standard
            message = (f"Alerte Expiration Domaine : "
                      f"Le domaine {domain} expire le {formatted_date} et le "
                      f"Registrar est {registrar_name}")
            send_webhook_alert(message)
            
            # Vérification de l'expiration imminente (<30 jours)
            check_expiry_alert(expiry_date, domain, registrar_name)

def check_domain_expiry(domain):
    """
    Vérifie et affiche la date d'expiration d'un domaine
    Args:
        domain (str): Domaine à vérifier
    """
    print(f"Analyse du nom de domaine {domain}")
    whois_data = get_whois_data(domain)
    
    if whois_data:
        registry_data = whois_data.get('WhoisRecord', {}).get('registryData', {})
        expires_date = registry_data.get('expiresDate')
        registrar_name = registry_data.get('registrarName')

        if expires_date and registrar_name:
            # Formatage de la date (JJ-MM-AAAA HH:MMZ)
            expiry_date = datetime.strptime(expires_date, '%Y-%m-%dT%H:%M:%SZ')
            formatted_date = expiry_date.strftime('%Y-%m-%dT%H:%MZ')
            
            print(f"Date d'expiration du nom de domaine : {formatted_date}")
            print(f"Registrar du nom de domaine : {registrar_name}")
            
            # Envoi des données au webhook
            extract_domain_info(whois_data, domain)
            print("Alerte envoyée au webhook.\n")
            
            # Vérification de l'expiration imminente
            check_expiry_alert(expiry_date, domain, registrar_name)
        else:
            print("Informations d'expiration incomplètes dans les données WHOIS\n")
    else:
        print("Aucune donnée WHOIS disponible pour ce domaine\n")
    
    time.sleep(1)  # Pause pour éviter le rate limiting