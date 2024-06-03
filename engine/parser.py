import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re

def fetch(url):
    response = requests.get(url)
    return response.text

def parse_emails(html):
    emails = re.findall(r'[\w\.-]+@[\w\.-]+', html)
    return emails

def parse_phone_numbers(html):
    phone_numbers = re.findall(r'\+48\s?\d{3}\s?\d{3}\s?\d{3}', html)
    return phone_numbers

def parse_images(html, base_url):
    soup = BeautifulSoup(html, 'html.parser')
    images = [urljoin(base_url, img['src']) for img in soup.find_all('img', src=True)]
    return images

def parse_videos(html, base_url):
    soup = BeautifulSoup(html, 'html.parser')
    videos = []

    for video in soup.find_all('video'):
        src = video.get('src')
        if src:
            videos.append(urljoin(base_url, src))
        else:
            for source in video.find_all('source'):
                src = source.get('src')
                if src:
                    videos.append(urljoin(base_url, src))

    iframe_pattern = re.compile(r'<iframe[^>]*src="([^"]+\.(mp4|avi|mov|wmv|flv|webm|mkv))"[^>]*>')
    iframes = re.findall(iframe_pattern, html)
    for iframe_src in iframes:
        videos.append(urljoin(base_url, iframe_src))
    return videos

def verify_nip(nip):
    nip = ''.join(filter(str.isdigit, nip))

    if len(nip) != 10:
        return False

    if all(digit == '0' for digit in nip):
        return False

    weights = [6, 5, 7, 2, 3, 4, 5, 6, 7]
    suma = sum(int(nip[i]) * weights[i] for i in range(9))
    checksum = suma % 11

    if checksum == 10:
        checksum = 0

    return checksum == int(nip[9])

def parse_nip(html):
    nip_pattern = re.compile(r'<[a-zA-Z\s\d="\':/._-]*>(\d{10})<[a-zA-Z\s\d="\':/._-]*>')
    nips = re.findall(nip_pattern, html)
    valid_nips = [nip for nip in nips if verify_nip(nip)]
    return valid_nips

def fetch_and_parse(url, data_type):
    html = fetch(url)
    base_url = '/'.join(url.split('/')[:3])
    parsed_data = {'url': url}
    
    if 'emails' in data_type or 'all' in data_type:
        parsed_data['emails'] = parse_emails(html)
    if 'phone_numbers' in data_type or 'all' in data_type:
        parsed_data['phone_numbers'] = parse_phone_numbers(html)
    if 'images' in data_type or 'all' in data_type:
        parsed_data['images'] = parse_images(html, base_url)
    if 'videos' in data_type or 'all' in data_type:
        parsed_data['videos'] = parse_videos(html, base_url)
    if 'nips' in data_type or 'all' in data_type:
        parsed_data['nips'] = parse_nip(html)

    return parsed_data
    
def fetch_subpages(url, num_subpages):
    html = fetch(url)
    soup = BeautifulSoup(html, 'html.parser')
    links = [a['href'] for a in soup.find_all('a', href=True)]
    full_links = [urljoin(url, link) for link in links if link.startswith('http://') or link.startswith('https://')]
    return full_links[:num_subpages]
