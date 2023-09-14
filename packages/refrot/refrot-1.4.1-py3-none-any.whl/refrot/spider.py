from timeit import default_timer as timer

import requests

from . import inspect
from . import hparser

TIMEOUT_SECONDS = 5


def get_links(url, args, checked=[], errors={}):
    """Recursively check links found at url."""
    if url in checked:
        return
    if args.ignore_external_links and not url.startswith(args.url):
        return
    checked.append(url)
    # Don't spider static files: CSS, JS, etc.
    if inspect.static_url(url):
        return
    try:
        if args.user_agent:
            headers = {'user-agent': args.user_agent}
            r = requests.get(
                url,
                headers=headers,
                timeout=float(TIMEOUT_SECONDS))
        else:
            r = requests.get(url, timeout=float(TIMEOUT_SECONDS))
        if r.history:
            status_code = r.history[0].status_code
            reason = r.history[0].reason
            print(status_code, url)
            # Ignore temporary redirects.
            if status_code != 302:
                errors[url] = f'{status_code} {reason}'
        else:
            print(r.status_code, url)
        if r.status_code != 200:
            errors[url] = f'{r.status_code} {r.reason}'
    except requests.exceptions.SSLError:
        print('SSL Cert Fail', url)
        errors[url] = 'SSL Cert Fail'
        return checked, errors
    except requests.exceptions.InvalidSchema:
        print('Invalid Schema', url)
        errors[url] = 'Invalid Schema'
        return checked, errors
    except requests.exceptions.ConnectionError:
        print('Connection Error', url)
        errors[url] = 'Connection Error'
        return checked, errors
    except requests.exceptions.ReadTimeout:
        print('Read Timeout Error', url)
        errors[url] = 'Read Timeout Error'
        return checked, errors

    # Don't spider external links. They can check their own pages!
    if not url.startswith(args.url):
        return
    parser = hparser.LinkParser()
    parser.feed(r.text)
    parser.make_links_absolute(url)
    for link in parser.links:
        get_links(link, args, checked, errors)
    return checked, errors


def main(args):
    start = timer()
    checked, errors = get_links(args.url, args)
    print(f'\nLinks checked: {len(checked)}. Errors found: {len(errors)}.')
    keys = sorted(errors.keys())
    for key in keys:
        print(errors[key], key)
    end = timer()
    print(f'Run time: {end - start:.2f} seconds')

