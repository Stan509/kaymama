import urllib.request
import json
import urllib.parse
import sys
import xml.etree.ElementTree as ET
import os
from dotenv import load_dotenv

# Load local environment variables from .env
load_dotenv()

# Configuration
DO_TOKEN = os.getenv('DO_TOKEN')
NC_API_KEY = os.getenv('NC_API_KEY')
NC_USERNAME = 'Stan509'  # Expected Namecheap username matching the Stan509 GitHub context
NC_TLD = 'online'
NC_SLD = 'kaymama'
CLIENT_IP = '148.255.216.98'

if not DO_TOKEN or not NC_API_KEY:
    print("Error: DO_TOKEN and NC_API_KEY must be set in your .env file.")
    sys.exit(1)

SPEC = {
    "name": "kaymama",
    "region": "nyc",
    "services": [
        {
            "name": "web",
            "git": {
                "repo_clone_url": "https://github.com/Stan509/kaymama.git",
                "branch": "main"
            },
            "dockerfile_path": "Dockerfile",
            "envs": [
                {
                    "key": "DATABASE_URL",
                    "value": "${db.DATABASE_URL}",
                    "scope": "RUN_AND_BUILD_TIME"
                },
                {
                    "key": "DEBUG",
                    "value": "False",
                    "scope": "RUN_TIME"
                },
                {
                    "key": "ALLOWED_HOSTS",
                    "value": "kaymama.online,www.kaymama.online,localhost,127.0.0.1",
                    "scope": "RUN_TIME"
                },
                {
                    "key": "SECRET_KEY",
                    "value": "django-secure-production-secret-key-kaymama-2026",
                    "scope": "RUN_AND_BUILD_TIME"
                }
            ],
            "instance_size_slug": "apps-s-1vcpu-0.5gb",
            "instance_count": 1,
            "http_port": 8000
        }
    ],
    "jobs": [
        {
            "name": "migrate",
            "git": {
                "repo_clone_url": "https://github.com/Stan509/kaymama.git",
                "branch": "main"
            },
            "dockerfile_path": "Dockerfile",
            "run_command": "python manage.py migrate --noinput && python manage.py seed_restaurant && python manage.py collectstatic --noinput",
            "envs": [
                {
                    "key": "DATABASE_URL",
                    "value": "${db.DATABASE_URL}",
                    "scope": "RUN_AND_BUILD_TIME"
                },
                {
                    "key": "SECRET_KEY",
                    "value": "django-secure-production-secret-key-kaymama-2026",
                    "scope": "RUN_AND_BUILD_TIME"
                }
            ],
            "instance_size_slug": "apps-s-1vcpu-0.5gb",
            "instance_count": 1,
            "kind": "PRE_DEPLOY"
        }
    ],
    "databases": [
        {
            "name": "db",
            "engine": "PG",
            "version": "15"
        }
    ],
    "domains": [
        {
            "domain": "kaymama.online",
            "type": "PRIMARY"
        },
        {
            "domain": "www.kaymama.online",
            "type": "ALIAS"
        }
    ]
}

def do_api_request(url, method='GET', body=None):
    headers = {
        'Authorization': f'Bearer {DO_TOKEN}',
        'Content-Type': 'application/json'
    }
    data = json.dumps(body).encode('utf-8') if body else None
    req = urllib.request.Request(url, headers=headers, data=data, method=method)
    try:
        with urllib.request.urlopen(req) as res:
            return json.loads(res.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        print(f"DO API Error ({e.code}): {e.read().decode('utf-8')}")
        sys.exit(1)
    except Exception as e:
        print(f"Request failed: {e}")
        sys.exit(1)

def get_existing_app():
    print("Checking for existing DigitalOcean App...")
    data = do_api_request("https://api.digitalocean.com/v2/apps")
    for app in data.get('apps', []):
        if app.get('spec', {}).get('name') == 'kaymama':
            return app
    return None

def deploy_app():
    existing = get_existing_app()
    if existing:
        app_id = existing['id']
        print(f"App found (ID: {app_id}). Updating spec...")
        url = f"https://api.digitalocean.com/v2/apps/{app_id}"
        result = do_api_request(url, method='PUT', body={"spec": SPEC})
        print("App spec updated successfully!")
    else:
        print("No existing app found. Creating new App on DigitalOcean App Platform...")
        url = "https://api.digitalocean.com/v2/apps"
        result = do_api_request(url, method='POST', body={"spec": SPEC})
        print("App creation initiated successfully!")
        
    app_info = result.get('app', {})
    default_ingress = app_info.get('default_ingress', '')
    
    # Strip protocol if present
    if default_ingress.startswith('https://'):
        default_ingress = default_ingress.replace('https://', '')
    if default_ingress.startswith('http://'):
        default_ingress = default_ingress.replace('http://', '')
    if default_ingress.endswith('/'):
        default_ingress = default_ingress[:-1]
        
    print(f"Default App URL: {default_ingress}")
    return default_ingress

def update_namecheap_dns(ingress_domain):
    if not ingress_domain:
        print("Ingress domain empty, skipping Namecheap DNS setup.")
        return
        
    print(f"Connecting to Namecheap API to configure domains for '{ingress_domain}'...")
    
    # URL encoded parameters
    params = {
        'ApiUser': NC_USERNAME,
        'ApiKey': NC_API_KEY,
        'UserName': NC_USERNAME,
        'Command': 'namecheap.domains.dns.setHosts',
        'ClientIP': CLIENT_IP,
        'SLD': NC_SLD,
        'TLD': NC_TLD,
        'HostName1': '@',
        'RecordType1': 'ALIAS',
        'Address1': ingress_domain,
        'TTL1': '1800',
        'HostName2': 'www',
        'RecordType2': 'CNAME',
        'Address2': ingress_domain,
        'TTL2': '1800'
    }
    
    query_string = urllib.parse.urlencode(params)
    url = f"https://api.namecheap.com/xml.response?{query_string}"
    
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as res:
            response_xml = res.read().decode('utf-8')
            root = ET.fromstring(response_xml)
            errors = root.findall('.//{http://api.namecheap.com/xml.response}Error')
            
            if errors:
                err_msg = ", ".join([e.text for e in errors])
                print(f"\n[WARNING] Namecheap API returned errors: {err_msg}")
                print("\nThis usually means:")
                print("1. Your Namecheap username does not match 'Stan509'.")
                print(f"2. Your current IP address ({CLIENT_IP}) is not whitelisted in Namecheap.")
                print("\n[ACTION REQUIRED]: Please configure DNS manually in your Namecheap Console:")
                print(f"  - Add ALIAS record for '@' pointing to '{ingress_domain}'")
                print(f"  - Add CNAME record for 'www' pointing to '{ingress_domain}'")
            else:
                print("\n[SUCCESS] Namecheap DNS records successfully configured via API!")
                print(f"  - ALIAS record @ -> {ingress_domain}")
                print(f"  - CNAME record www -> {ingress_domain}")
    except Exception as e:
        print(f"Error calling Namecheap API: {e}")

if __name__ == "__main__":
    ingress = deploy_app()
    update_namecheap_dns(ingress)
    print("\nDeployment execution completed. Please check your DigitalOcean Console to monitor progress.")
