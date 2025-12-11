#!/usr/bin/env python3
import json
import os
import re


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
MANIFEST = os.path.join(ROOT, 'seo-manifest.ndjson')


def iter_ndjson(path):
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        for line_num, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                yield line_num, json.loads(line)
            except json.JSONDecodeError as e:
                yield line_num, {'__error__': f'JSON parse error at line {line_num}: {e}'}


def is_abs_url(href: str) -> bool:
    return href.lower().startswith(('http://', 'https://', '//'))


def main():
    issues = []
    seen_paths = set()
    page_count = 0
    for ln, obj in iter_ndjson(MANIFEST):
        if '__error__' in obj:
            issues.append(obj['__error__'])
            continue
        typ = obj.get('type')
        if typ == 'site':
            # Minimal checks
            if not obj.get('domain'):
                issues.append(f'Line {ln}: site.domain missing')
            continue
        if typ in ('robotsTxt', 'sitemapXml'):
            if not obj.get('content'):
                issues.append(f'Line {ln}: {typ}.content empty')
            continue
        if typ == 'page':
            page_count += 1
            path = obj.get('path', '')
            if not path.startswith('/'):
                issues.append(f'Line {ln}: page.path must start with "/" -> {path}')
            if path in seen_paths:
                issues.append(f'Line {ln}: duplicate page.path {path}')
            seen_paths.add(path)
            meta = obj.get('meta', {})
            if meta.get('charset', '').lower() not in ('utf-8', 'utf8'):
                issues.append(f'Line {ln}: non-utf8 charset for {path}')
            # Links
            for link in obj.get('internalLinks', []):
                href = (link.get('href') or '').strip()
                if not href:
                    issues.append(f'Line {ln}: empty internal href at {path}')
                # internal should not be external absolute to other domains
                if is_abs_url(href) and obj.get('path', '').split('/')[1] not in href:
                    # not a strict check, but flag suspicious
                    pass
            for link in obj.get('externalLinks', []):
                href = (link.get('href') or '').strip()
                if not href:
                    issues.append(f'Line {ln}: empty external href at {path}')
            # Images
            for img in obj.get('images', []):
                src = (img.get('src') or '').strip()
                if not src:
                    issues.append(f'Line {ln}: empty image src at {path}')
                alt = (img.get('alt') or '').strip()
                # recommend alt for SEO
                if not alt:
                    issues.append(f'Line {ln}: missing alt for image {src} at {path}')
            continue
        issues.append(f'Line {ln}: unknown type {typ}')

    summary = {
        'pages': page_count,
        'uniquePaths': len(seen_paths),
        'issuesCount': len(issues),
    }
    print(json.dumps({'summary': summary, 'issues': issues[:200]}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()




