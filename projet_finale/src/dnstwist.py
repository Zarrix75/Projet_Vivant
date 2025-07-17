#!/usr/bin/env python3
import json
import logging
import subprocess
import sys
import os
import urllib.request
from argparse import ArgumentParser
import requests
from typing import List, Dict, Any, Optional

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

WEBHOOK_URL = 'your_webhook_url_here'  # Remplacez par votre URL de webhook
DEFAULT_DNS = '8.8.8.8'  # DNS Google public

class TyposquatAnalyzer:
    def __init__(self, domain: str):
        self.domain = domain
        self.results: List[Dict[str, Any]] = []
        self._check_dependencies()

    def _check_dependencies(self):
        """Vérifie que dnstwist est installé et accessible"""
        try:
            subprocess.run(['dnstwist', '--version'],
                         capture_output=True,
                         check=True,
                         text=True)
        except Exception as e:
            logging.error("dnstwist n'est pas installé ou accessible")
            logging.error("Installez avec: pip install dnstwist")
            sys.exit(1)

    def _check_connectivity(self) -> bool:
        """Vérifie la connectivité Internet en utilisant le DNS Google"""
        try:
            urllib.request.urlopen('https://google.com', timeout=5)
            return True
        except Exception as e:
            logging.warning(f"Aucune connectivité Internet détectée: {str(e)}")
            return False

    def run_analysis(self, nameserver: Optional[str] = None, 
                    delay: Optional[float] = None,
                    timeout: int = 60) -> bool:
        """
        Exécute l'analyse dnstwist avec des paramètres configurables
        Args:
            nameserver: Serveur DNS alternatif (par défaut: 8.8.8.8)
            delay: Délai entre les requêtes en secondes (non utilisé)
            timeout: Timeout global en secondes
        """
        
        if not self._check_connectivity():
            return False

        cmd = [
            'dnstwist',
            '--registered',
            '--format', 'json',
            '--nameserver', nameserver if nameserver else DEFAULT_DNS
        ]

        if delay:
            logging.warning("Le paramètre delay n'est pas supporté par dnstwist et sera ignoré")

        cmd.append(self.domain)

        try:
            logging.info(f"Analyse de typosquatting pour {self.domain} en cours...")
            
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=True,
                timeout=timeout
            )
            
            self.results = json.loads(result.stdout)
            
            registered_count = len([r for r in self.results if r.get('dns-a')])
            logging.info(f"Analyse terminée. {len(self.results)} variations trouvées, {registered_count} enregistrées")
            
            return True
            
        except subprocess.CalledProcessError as e:
            logging.error(f"Erreur dnstwist (code {e.returncode}): {e.stderr.strip()}")
        except json.JSONDecodeError as e:
            logging.error(f"Erreur de décodage JSON: {str(e)}")
        except subprocess.TimeoutExpired:
            logging.error(f"Timeout après {timeout} secondes")
        except Exception as e:
            logging.error(f"Erreur inattendue: {str(e)}")
            
        return False

    def save_results(self, filename: str = None) -> None:
        """Sauvegarde les résultats en JSON avec nom de fichier automatique si non spécifié"""
        if filename is None:
            filename = f"typosquat_results_{self.domain}.json"
            
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.results, f, indent=2, ensure_ascii=False)
            logging.info(f"Résultats sauvegardés dans {filename}")
        except Exception as e:
            logging.error(f"Erreur lors de la sauvegarde: {str(e)}")

def send_typosquat_alert(domain: str, results: List[Dict[str, Any]]) -> None:
    """Envoie une alerte via webhook (silencieuse dans les logs)"""
    registered_domains = [r for r in results if r.get('dns-a')]
    if not registered_domains:
        return  # Ne rien logger

    try:
        message = {
            "title": f"🚨 Alerte Typosquatting - {domain}",
            "content": "\n".join(f"• {dom['domain']}" for dom in registered_domains[:10]),
            "stats": {
                "total_variations": len(results),
                "registered_domains": len(registered_domains)
            }
        }
        requests.post(WEBHOOK_URL, json=message, timeout=10)
    except Exception:
        pass  # Ne pas logger les erreurs de webhook

def main():
    parser = ArgumentParser()
    parser.add_argument('domain', help="Domaine cible à analyser")
    parser.add_argument('--output', help="Fichier de sortie personnalisé")
    parser.add_argument('--nameserver', help="Serveur DNS alternatif")
    parser.add_argument('--timeout', type=int, default=60, help="Timeout en secondes")
    parser.add_argument('--proxy', help="URL de proxy")
    
    args = parser.parse_args()

    # Configuration proxy silencieuse
    if args.proxy:
        os.environ['http_proxy'] = args.proxy
        os.environ['https_proxy'] = args.proxy

    analyzer = TyposquatAnalyzer(args.domain)
    if analyzer.run_analysis(
        nameserver=args.nameserver,
        timeout=args.timeout
    ):
        analyzer.save_results(args.output)
        send_typosquat_alert(args.domain, analyzer.results)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
    except Exception:
        sys.exit(1)