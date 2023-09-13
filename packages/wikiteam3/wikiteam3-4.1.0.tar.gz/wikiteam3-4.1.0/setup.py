# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['wikiteam3',
 'wikiteam3.dumpgenerator',
 'wikiteam3.dumpgenerator.api',
 'wikiteam3.dumpgenerator.cli',
 'wikiteam3.dumpgenerator.dump',
 'wikiteam3.dumpgenerator.dump.image',
 'wikiteam3.dumpgenerator.dump.misc',
 'wikiteam3.dumpgenerator.dump.page',
 'wikiteam3.dumpgenerator.dump.page.xmlexport',
 'wikiteam3.dumpgenerator.dump.page.xmlrev',
 'wikiteam3.dumpgenerator.dump.xmldump',
 'wikiteam3.dumpgenerator.log',
 'wikiteam3.uploader',
 'wikiteam3.utils',
 'wikiteam3.utils.login']

package_data = \
{'': ['*']}

install_requires = \
['file_read_backwards>=3.0.0,<4.0.0',
 'httpx>=0.24.1,<0.25.0',
 'internetarchive>=3.5.0,<4.0.0',
 'lxml>=4.9.2,<5.0.0',
 'mwclient>=0.10.1,<0.11.0',
 'python-slugify>=8.0.1,<9.0.0',
 'requests>=2.31.0,<3.0.0']

entry_points = \
{'console_scripts': ['dumpgenerator = wikiteam3.dumpgenerator:main_deprecated',
                     'wikiteam3dumpgenerator = wikiteam3.dumpgenerator:main',
                     'wikiteam3uploader = wikiteam3.uploader:main']}

setup_kwargs = {
    'name': 'wikiteam3',
    'version': '4.1.0',
    'description': 'Tools for downloading and preserving MediaWikis. We archive MediaWikis, from Wikipedia to tiniest wikis.',
    'long_description': '# `wikiteam3`\n\n<!-- !["MediaWikiArchive.png"](./MediaWikiArchive.png) -->\n<div align=center><img width = \'150\' height =\'150\' src ="./MediaWikiArchive.png"/></div>\n\n> Countless MediaWikis are still waiting to be archived.\n>\n> _Image by [@gledos](https://github.com/gledos/)_\n\n`wikiteam3` is a fork of `mediawiki-scraper`.\n\n## Why we fork mediawiki-scraper\n\nOriginally, mediawiki-scraper was named wikiteam3, but wikiteam upstream (py2 version) suggested that the name should be changed to avoid confusion with the original wikiteam.  \nHalf a year later, we didn\'t see any py3 porting progress in the original wikiteam, and mediawiki-scraper lacks "code" reviewers.  \nSo, we decided to break that suggestion, fork and named it back to wikiteam3, put the code here, and release it to pypi wildly.\n\nEverything still under GPLv3 license.\n\n## Installation\n\n```shell\npip install wikiteam3 --upgrade\n```\n\n## Usage\n\n### Downloading a wiki with complete XML history and images\n\n```bash\nwikiteam3dumpgenerator http://wiki.domain.org --xml --images\n```\n\n### Manually specifying `api.php` and/or `index.php`\n\nIf the script can\'t find itself the `api.php` and/or `index.php` paths, then you can provide them:\n\n```bash\nwikiteam3dumpgenerator --api http://wiki.domain.org/w/api.php --xml --images\n```\n\n```bash\nwikiteam3dumpgenerator --api http://wiki.domain.org/w/api.php --index http://wiki.domain.org/w/index.php \\\n    --xml --images\n```\n\nIf you only want the XML histories, just use `--xml`. For only the images, just `--images`. For only the current version of every page, `--xml --curonly`.\n\n### Resuming an incomplete dump\n\n```bash\nwikiteam3dumpgenerator \\\n    --api http://wiki.domain.org/w/api.php --xml --images --resume --path /path/to/incomplete-dump\n```\n\nIn the above example, `--path` is only necessary if the download path is not the default.\n\n`wikiteam3dumpgenerator` will also ask you if you want to resume if it finds an incomplete dump in the path where it is downloading.\n\n## Using `wikiteam3uploader`\n\nTODO: ...\n\n### Requirements\n\n- unbinded port 62954\n- 3GB+ RAM (~2.56GB for commpressing)\n- 64-bit OS (required by 2G wlog size)\n\n- 7z (`7z-full` with lzma2)\n- zstd 1.5.5+ (recommended), v1.5.0-v1.5.4(DO NOT USE), 1.4.8 (minimum)\n\n## Checking dump integrity\n\nTODO: xml2titles.py\n\nIf you want to check the XML dump integrity, type this into your command line to count title, page and revision XML tags:\n\n```bash\ngrep -E \'<title(.*?)>\' *.xml -c;grep -E \'<page(.*?)>\' *.xml -c;grep \\\n    "</page>" *.xml -c;grep -E \'<revision(.*?)>\' *.xml -c;grep "</revision>" *.xml -c\n```\n  \nYou should see something similar to this (not the actual numbers) - the first three numbers should be the same and the last two should be the same as each other:\n\n```bash\n580\n580\n580\n5677\n5677\n```\n\nIf your first three numbers or your last two numbers are different, then, your XML dump is corrupt (it contains one or more unfinished ```</page>``` or ```</revision>```). This is not common in small wikis, but large or very large wikis may fail at this due to truncated XML pages while exporting and merging. The solution is to remove the XML dump and re-download, a bit boring, and it can fail again.\n\n## Contributors\n\n**WikiTeam** is the [Archive Team](http://www.archiveteam.org) [[GitHub](https://github.com/ArchiveTeam)] subcommittee on wikis.\nIt was founded and originally developed by [Emilio J. Rodríguez-Posada](https://github.com/emijrp), a Wikipedia veteran editor and amateur archivist. Thanks to people who have helped, especially to: [Federico Leva](https://github.com/nemobis), [Alex Buie](https://github.com/ab2525), [Scott Boyd](http://www.sdboyd56.com), [Hydriz](https://github.com/Hydriz), Platonides, Ian McEwen, [Mike Dupont](https://github.com/h4ck3rm1k3), [balr0g](https://github.com/balr0g) and [PiRSquared17](https://github.com/PiRSquared17).\n\n**Mediawiki-Scraper** The Python 3 initiative is currently being led by [Elsie Hupp](https://github.com/elsiehupp), with contributions from [Victor Gambier](https://github.com/vgambier), [Thomas Karcher](https://github.com/t-karcher), [Janet Cobb](https://github.com/randomnetcat), [yzqzss](https://github.com/yzqzss), [NyaMisty](https://github.com/NyaMisty) and [Rob Kam](https://github.com/robkam)\n\n**WikiTeam3** None yet.\n',
    'author': 'yzqzss',
    'author_email': 'yzqzss@yandex.com',
    'maintainer': 'yzqzss',
    'maintainer_email': 'yzqzss@yandex.com',
    'url': 'https://github.com/saveweb/wikiteam3',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
