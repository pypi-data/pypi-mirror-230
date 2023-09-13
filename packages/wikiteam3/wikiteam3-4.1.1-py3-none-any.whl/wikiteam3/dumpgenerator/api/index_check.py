import re

import requests


def check_index(*, index: str, logged_in: bool, session: requests.Session):
    """ Checking index.php availability """
    r = session.post(url=index, data={"title": "Special:Version"}, timeout=30)
    if r.status_code >= 400:
        print(f"ERROR: The wiki returned status code HTTP {r.status_code}")
        return False
    raw = r.text
    print("Checking index.php...", index)
    # Workaround for
    # [Don't try to download private wikis unless --cookies is given]
    # (https://github.com/wikiTeam/wikiteam/issues/71)
    if (
        re.search(
            '(Special:Badtitle</a>|class="permissions-errors"|"wgCanonicalSpecialPageName":"Badtitle"|Login Required</h1>)',
            raw,
        )
        and not logged_in
    ):
        print("ERROR: This wiki requires login and we are not authenticated")
        return False
    if re.search(
        '(page-Index_php|"wgPageName":"Index.php"|"firstHeading"><span dir="auto">Index.php</span>)',
        raw,
    ):
        print("Looks like the page called Index.php, not index.php itself")
        return False
    if re.search(
        '(This wiki is powered by|<h2 id="mw-version-license">|meta name="generator" content="MediaWiki|class="mediawiki)',
        raw,
    ):
        return True
    return False
