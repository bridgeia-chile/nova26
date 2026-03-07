import urllib.request
import json
import os
import zipfile
import shutil

url = "https://api.github.com/repos/steipete/gogcli/releases/latest"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req) as response:
    data = json.loads(response.read().decode())
    dl_url = None
    for asset in data['assets']:
        if 'windows_amd64.zip' in asset['name'].lower():
            dl_url = asset['browser_download_url']
            break

if dl_url:
    print(f"Downloading from {dl_url}")
    urllib.request.urlretrieve(dl_url, "gogcli.zip")
    with zipfile.ZipFile("gogcli.zip", "r") as zip_ref:
        zip_ref.extractall("gogcli_extracted")
    
    target_dir = os.path.expanduser("~/.local/bin")
    os.makedirs(target_dir, exist_ok=True)
    
    gog_path = None
    for root, dirs, files in os.walk("gogcli_extracted"):
        for file in files:
            if file == "gog.exe":
                gog_path = os.path.join(root, file)
                break
                
    if gog_path:
        shutil.copy(gog_path, os.path.join(target_dir, "gog.exe"))
        print("Success! Copied to", os.path.join(target_dir, "gog.exe"))
    else:
        print("gog.exe not found after extract. Found:", os.listdir('gogcli_extracted'))
else:
    print("Could not find release")
