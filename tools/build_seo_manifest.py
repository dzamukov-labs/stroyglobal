#!/usr/bin/env python3
import os
import re
import json
from html import unescape


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))


def read_file_safe(path):
    try:
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()
    except Exception:
        return ''


def extract_between(pattern, text, flags=re.IGNORECASE | re.DOTALL):
    m = re.search(pattern, text, flags)
    return m.group(1).strip() if m else ''


def strip_tags(html: str) -> str:
    # Remove scripts/styles first
    html = re.sub(r'<script[\s\S]*?</script>', '', html, flags=re.IGNORECASE)
    html = re.sub(r'<style[\s\S]*?</style>', '', html, flags=re.IGNORECASE)
    # Strip tags
    text = re.sub(r'<[^>]+>', ' ', html)
    # Collapse whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return unescape(text)


def extract_metas(html: str):
    metas = {}
    # charset
    m = re.search(r'<meta[^>]*charset\s*=\s*"?([^\s"/>]+)"?', html, re.IGNORECASE)
    if m:
        metas['charset'] = m.group(1).lower()
    # name/description
    for name in ('description', 'keywords', 'robots'):
        m = re.search(r'<meta[^>]*name\s*=\s*"?' + name + r'"?[^>]*content\s*=\s*"([^"]*)"', html, re.IGNORECASE)
        if m:
            metas[name] = m.group(1).strip()
    # canonical
    m = re.search(r'<link[^>]*rel\s*=\s*"?canonical"?[^>]*href\s*=\s*"([^"]+)"', html, re.IGNORECASE)
    if m:
        metas['canonical'] = m.group(1).strip()
    return metas


def extract_headings(html: str):
    headings = {}
    for level in range(1, 7):
        tag = f'h{level}'
        pattern = rf'<{tag}[^>]*>([\s\S]*?)</{tag}>'
        matches = re.findall(pattern, html, re.IGNORECASE)
        if matches:
            items = [strip_tags(m).strip() for m in matches if strip_tags(m).strip()]
            if items:
                headings[tag] = items
    return headings


def extract_links(html: str):
    links = []
    for m in re.finditer(r'<a[^>]*href\s*=\s*"([^"]+)"[^>]*>([\s\S]*?)</a>', html, re.IGNORECASE):
        href = m.group(1).strip()
        anchor = strip_tags(m.group(2))
        rel_m = re.search(r'rel\s*=\s*"([^"]+)"', m.group(0), re.IGNORECASE)
        rel = rel_m.group(1) if rel_m else ''
        target_m = re.search(r'target\s*=\s*"([^"]+)"', m.group(0), re.IGNORECASE)
        target = target_m.group(1) if target_m else ''
        links.append({'href': href, 'anchor': anchor, 'rel': rel, 'target': target})
    return links


def extract_images(html: str):
    images = []
    for m in re.finditer(r'<img[^>]*>', html, re.IGNORECASE):
        tag = m.group(0)
        def get_attr(attr):
            am = re.search(rf'{attr}\s*=\s*"([^"]*)"', tag, re.IGNORECASE)
            return am.group(1).strip() if am else ''
        images.append({
            'src': get_attr('src'),
            'alt': get_attr('alt'),
            'title': get_attr('title'),
            'width': get_attr('width'),
            'height': get_attr('height'),
        })
    return images


def make_page_object(root_dir: str, file_path: str, site_domain: str):
    rel_path = os.path.relpath(file_path, root_dir)
    html = read_file_safe(file_path)
    title = extract_between(r'<title>([\s\S]*?)</title>', html)
    metas = extract_metas(html)
    headings = extract_headings(html)
    links = extract_links(html)
    images = extract_images(html)
    # Classify links as internal/external with robust rules
    internal_links = []
    external_links = []
    for l in links:
        href = (l.get('href') or '').strip()
        lower_href = href.lower()
        # Skip empty and non-navigational schemes
        if not href or lower_href.startswith(('mailto:', 'tel:', 'javascript:')):
            external_links.append(l)
            continue
        # Absolute URLs
        if lower_href.startswith(('http://', 'https://', '//')):
            if site_domain in lower_href:
                internal_links.append(l)
            else:
                external_links.append(l)
            continue
        # Fragments and relative paths treated as internal
        if href.startswith(('#', '/', './', '../')) or not re.match(r'^[a-zA-Z]+:', href):
            internal_links.append(l)
            continue
        # Fallback
        external_links.append(l)

    return {
        'type': 'page',
        'path': '/' + rel_path.replace('\\', '/'),
        'status': 200,
        'title': strip_tags(title) if title else '',
        'meta': {
            'description': metas.get('description', ''),
            'keywords': metas.get('keywords', ''),
            'robots': metas.get('robots', 'index,follow'),
            'canonical': metas.get('canonical', ''),
            'charset': metas.get('charset', 'utf-8'),
        },
        'openGraph': {},
        'twitter': {},
        'headings': headings,
        'contentHtml': html,
        'internalLinks': internal_links,
        'externalLinks': external_links,
        'images': images,
        'breadcrumbs': [],
    }


def main():
    site_domain = 'stroyglobal.com'
    robots_path = os.path.join(ROOT, 'robots.txt')
    sitemap_path = os.path.join(ROOT, 'sitemap.xml')
    robots_txt = read_file_safe(robots_path)
    sitemap_xml = read_file_safe(sitemap_path)

    site_obj = {
        'type': 'site',
        'domain': site_domain,
        'wwwPolicy': 'no-www',
        'trailingSlash': 'preserve',
        'defaultLang': 'ru',
        'encoding': 'utf-8',
        'analytics': {
            'gtm': ['GTM-NDB4QN5'],
            'ga_ua': ['UA-118258068-1'],
            'yandex_metrika': ['21670957']
        }
    }

    print(json.dumps(site_obj, ensure_ascii=False))

    if robots_txt:
        print(json.dumps({'type': 'robotsTxt', 'path': '/robots.txt', 'content': robots_txt}, ensure_ascii=False))
    if sitemap_xml:
        print(json.dumps({'type': 'sitemapXml', 'path': '/sitemap.xml', 'content': sitemap_xml}, ensure_ascii=False))

    # walk and collect .htm files
    for dirpath, dirnames, filenames in os.walk(ROOT):
        for name in filenames:
            if name.lower().endswith('.htm'):
                full_path = os.path.join(dirpath, name)
                page_obj = make_page_object(ROOT, full_path, site_domain)
                print(json.dumps(page_obj, ensure_ascii=False))


if __name__ == '__main__':
    main()


