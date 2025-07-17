import socket
import requests
import sys
import os
import warnings
from typing import List, Dict, Optional

warnings.filterwarnings("ignore", category=requests.packages.urllib3.exceptions.InsecureRequestWarning)

# Configuration dynamique des sites
SITES = {}

def initialize_sites(domains=None):
    """Initialise la configuration des sites en fonction des domaines fournis"""
    global SITES
    default_ports = range(1, 1025)
    
    if not domains:
        domains = ["exemple.com", "exemple.com2", "exemple.com3"]
    
    SITES.clear()
    for domain in domains:
        safe_name = domain.replace('.', '_')
        SITES[domain] = {
            "save_file": f"{safe_name}_ports.txt",
            "ports": default_ports
        }

# Initialisation par défaut
initialize_sites()

def read_saved_ports(site: str) -> List[str]:
    """Lit les ports précédemment sauvegardés pour un site spécifique"""
    if site not in SITES:
        return []
    
    save_file = SITES[site]["save_file"]
    if not os.path.exists(save_file):
        return []
    
    with open(save_file, "r") as f:
        return [line.strip() for line in f if line.strip().isdigit()]

def write_ports_to_file(site: str, ports: List[str]) -> None:
    """Sauvegarde les ports ouverts pour un site spécifique"""
    if site not in SITES:
        return
        
    save_file = SITES[site]["save_file"]
    with open(save_file, "w") as f:
        for port in ports:
            f.write(f"{port}\n")

def send_webhook_alert(site: str, port: str, webhook_url: str) -> bool:
    """Envoie une alerte webhook pour un port spécifique"""
    try:
        data = {
            "content": f"Nouveau port ouvert sur {site}: {port}"
        }
        response = requests.post(webhook_url, json=data, verify=False, timeout=10)
        response.raise_for_status()
        return True
    except Exception as e:
        print(f"[ERREUR] Webhook pour {site}: {str(e)}")
        return False

def check_open_ports(site: str) -> List[str]:
    """Scan les ports pour un site spécifique"""
    if site not in SITES:
        return []
        
    found_ports = []
    ports_to_check = SITES[site]["ports"]
    
    for port in ports_to_check:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(0.1)
                sock.connect((site, port))
                found_ports.append(str(port))
        except:
            continue
            
    return sorted(found_ports)

def scan_site(site: str, webhook_url: str = None) -> None:
    """Effectue un scan complet pour un site"""
    if site not in SITES:
        print(f"Site non configuré: {site}")
        return
        
    print(f"\nScan des ports pour {site}...")
    
    current_ports = check_open_ports(site)
    previous_ports = read_saved_ports(site)

    newly_opened = [p for p in current_ports if p not in previous_ports]

    if newly_opened:
        print(f"Nouveaux ports sur {site}: {', '.join(newly_opened)}")
        if webhook_url:
            for port in newly_opened:
                if send_webhook_alert(site, port, webhook_url):
                    print(f"Alerte pour le port {port} envoyée au webhook")
                else:
                    print(f"Échec pour le port {port}")
    else:
        print(f"Aucun nouveau port détecté sur {site}")

    write_ports_to_file(site, current_ports)
    print(f"Résultats sauvegardés dans {SITES[site]['save_file']}")

def main(args=None, config=None):
    """Fonction principale"""
    # Initialisation des sites depuis la config si disponible
    if config and "domains" in config:
        initialize_sites(config["domains"])
    
    webhook_url = config.get("alerts", {}).get("webhook", {}).get("url") if config else None

    # Traitement des arguments passés sous forme de liste
    if isinstance(args, list) and len(args) > 1:
        site_to_scan = args[1]
        scan_site(site_to_scan, webhook_url)
        return

    # Traitement des arguments CLI
    if len(sys.argv) > 1:
        site_to_scan = sys.argv[1]
        scan_site(site_to_scan, webhook_url)
    else:
        # Mode par défaut - scan tous les sites configurés
        for site in SITES:
            scan_site(site, webhook_url)

if __name__ == "__main__":
    main()