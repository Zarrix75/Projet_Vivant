import os
import yaml
import time
import sys
from pathlib import Path

from checker import check_sites
from logger import setup_logging
from alertesdomaines import check_domain_expiry as check_domain
from certificatelec import check_cert_expiry as check_certificat
from scanport import main as scan_ports
from dnstwist import TyposquatAnalyzer, send_typosquat_alert

def load_config():
    config_path = Path(__file__).parent.parent / "config" / "config.yaml"
    with open(config_path, "r") as file:
        return yaml.safe_load(file)

def run_all_checks(config, domain):
    setup_logging()
    full_analysis_sites = [f"https://{domain}"]

    print(f"\n=== Vérification de l'expiration du nom de domaine {domain} ===\n")
    check_domain(domain)

    print(f"\n=== Analyse du certificat électronique {domain} ===\n")
    check_certificat(
        domain,
        webhook_url=config.get("alerts", {}).get("webhook", {}).get("url")  
    )
    
    print(f"\n=== Analyse typosquatting de {domain} ===\n")
    analyzer = TyposquatAnalyzer(domain)
    if analyzer.run_analysis():
        analyzer.save_results(f"typosquat_results_{domain.replace('.', '_')}.json")
        send_typosquat_alert(domain, analyzer.results)

    print(f"\n=== Analyse des ports ouverts sur {domain} ===\n")
    scan_ports(
        args=["scanport.py", domain],
        config=config
    )

def main():
    setup_logging()
    config = load_config()
    
    # Récupération de la liste des domaines
    domains = config.get("domains", ["exemple.com"])
        
    # Boucle de monitoring
    while True:
        for current_domain in domains:
            print(f"\n=== Début du monitoring pour {current_domain} ===\n")
            run_all_checks(config, current_domain)
            
            # Monitoring basique
            print("\n=== Monitoring des sites web ===\n")
            monitoring_sites = [
                {"url": f"https://{current_domain}", "name": current_domain},
                {"url": "https://www.google.com", "name": "Google"},
                {"url": "https://www.thisdomaindoesnotexist123456.com", "name": "Fake Site"}
            ]
            check_sites(monitoring_sites, config)
            
            time.sleep(config.get("interval_between_domains", 5))
        
        print(f"\n=== Cycle complet terminé. Attente de {config.get('interval', 60)} secondes ===\n")
        time.sleep(config.get("interval", 60))

if __name__ == "__main__":
    main()