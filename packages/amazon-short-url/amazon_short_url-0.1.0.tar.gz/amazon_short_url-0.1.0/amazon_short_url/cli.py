import re
from urllib.parse import urlsplit, urlunsplit

import click


@click.command()
@click.argument('url')
def main(url: str):
    clean_url = clean(url)
    print(clean_url)


def clean(url: str) -> str:
    parsed = urlsplit(url)

    if not is_valid_scheme(parsed.scheme):
        raise ValueError(f'Invalid scheme: {parsed.scheme}')
    if not is_valid_netloc(parsed.netloc):
        raise ValueError(f'Invalid netloc: {parsed.netloc}')

    cleaned_path = clean_path(parsed.path)
    if cleaned_path is None:
        raise ValueError(f'Unsupported path: {parsed.path}')

    return urlunsplit((parsed.scheme, parsed.netloc, cleaned_path, '', ''))


def is_valid_scheme(scheme: str) -> bool:
    return scheme == 'https'


def is_valid_netloc(netloc: str) -> bool:
    return re.match(r'www\.amazon\.co(m|m?\.[a-z]+)', netloc) != None


def clean_path(raw_path: str) -> str | None:
    match = re.search(r'/dp/[A-Z0-9]+', raw_path)
    if match is None:
        return None

    return match.group(0)
