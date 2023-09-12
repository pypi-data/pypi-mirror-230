# Internal tool

## Dependencies:

- Helm
- yq

## Info

If the DOCKER_HOST environment variable is set, it will use that Docker Engine to perform the pull/push requests.

## Sample Usage:

```
otimages push -v 23.4.0 --repository random.containerhub.tld --langpacks --include otxecm-init --exclude otxecm-init-lang-es

**SOURCEREPO**/released/otxecm-init-lang-ar:23.4.0
**SOURCEREPO**/released/otxecm-init-lang-cs-cz:23.4.0
**SOURCEREPO**/released/otxecm-init-lang-da-dk:23.4.0
**SOURCEREPO**/released/otxecm-init-lang-de:23.4.0
**SOURCEREPO**/released/otxecm-init-lang-fi-fi:23.4.0
**SOURCEREPO**/released/otxecm-init-lang-fr:23.4.0
**SOURCEREPO**/released/otxecm-init-lang-he:23.4.0
**SOURCEREPO**/released/otxecm-init-lang-it:23.4.0
**SOURCEREPO**/released/otxecm-init-lang-iw:23.4.0
**SOURCEREPO**/released/otxecm-init-lang-ja:23.4.0
**SOURCEREPO**/released/otxecm-init-lang-kk-kz:23.4.0
**SOURCEREPO**/released/otxecm-init-lang-ko-kr:23.4.0
**SOURCEREPO**/released/otxecm-init-lang-nb-no:23.4.0
**SOURCEREPO**/released/otxecm-init-lang-nl:23.4.0
**SOURCEREPO**/released/otxecm-init-lang-pl-pl:23.4.0
**SOURCEREPO**/released/otxecm-init-lang-pt:23.4.0
**SOURCEREPO**/released/otxecm-init-lang-ru-ru:23.4.0
**SOURCEREPO**/released/otxecm-init-lang-sv:23.4.0
**SOURCEREPO**/released/otxecm-init-lang-tr-tr:23.4.0
**SOURCEREPO**/released/otxecm-init-lang-uk-ua:23.4.0
**SOURCEREPO**/released/otxecm-init-lang-zh-cn:23.4.0
**SOURCEREPO**/released/otxecm-init-lang-zh-tw:23.4.0

Push Images to repository:
random.containerhub.tld/otxecm-init-lang-ar:23.4.0
random.containerhub.tld/otxecm-init-lang-cs-cz:23.4.0
random.containerhub.tld/otxecm-init-lang-da-dk:23.4.0
random.containerhub.tld/otxecm-init-lang-de:23.4.0
random.containerhub.tld/otxecm-init-lang-fi-fi:23.4.0
random.containerhub.tld/otxecm-init-lang-fr:23.4.0
random.containerhub.tld/otxecm-init-lang-he:23.4.0
random.containerhub.tld/otxecm-init-lang-it:23.4.0
random.containerhub.tld/otxecm-init-lang-iw:23.4.0
random.containerhub.tld/otxecm-init-lang-ja:23.4.0
random.containerhub.tld/otxecm-init-lang-kk-kz:23.4.0
random.containerhub.tld/otxecm-init-lang-ko-kr:23.4.0
random.containerhub.tld/otxecm-init-lang-nb-no:23.4.0
random.containerhub.tld/otxecm-init-lang-nl:23.4.0
random.containerhub.tld/otxecm-init-lang-pl-pl:23.4.0
random.containerhub.tld/otxecm-init-lang-pt:23.4.0
random.containerhub.tld/otxecm-init-lang-ru-ru:23.4.0
random.containerhub.tld/otxecm-init-lang-sv:23.4.0
random.containerhub.tld/otxecm-init-lang-tr-tr:23.4.0
random.containerhub.tld/otxecm-init-lang-uk-ua:23.4.0
random.containerhub.tld/otxecm-init-lang-zh-cn:23.4.0
random.containerhub.tld/otxecm-init-lang-zh-tw:23.4.0
Are you sure you want to push to random.containerhub.tld/? [y/N]:

```

# Help:

```sh
otimages --help
Usage: otimages [OPTIONS] COMMAND [ARGS]...

╭─ Options ───────────────────────────────────────────────────────────────────────────────────────╮
│ --install-completion          Install completion for the current shell.                         │
│ --show-completion             Show completion for the current shell, to copy it or customize    │
│                               the installation.                                                 │
│ --help                        Show this message and exit.                                       │
╰─────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Commands ──────────────────────────────────────────────────────────────────────────────────────╮
│ list                                                                                            │
│ pull                                                                                            │
│ push                                                                                            │
╰─────────────────────────────────────────────────────────────────────────────────────────────────╯

```

```bash
otimages list --help
otimages pull --help
otimages push --help
```
