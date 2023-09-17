# auto-gpg

A tool that switches gpg home on different working directory

## Installation

```shell
pip install auto-gpg
```

## Usage

**Configuration**

Write configuration file `~/.auto-gpg`

```
~/Developer/src/github.com:~/.gnupgs/hi@guoyk.xyz
~/Developer/src/gitlab.mycompany.com:~/.gnupgs/guoyk@mycompany.com
```

**Execute `auto-gpg`**

`auto-gpg` invokes `gpg` command with `GNUPGHOME` environment variable, and the value of `GNUPGHOME` is determined by the configuration file above.

```shell
auto-gpg -k
auto-gpg -abs
# ...
```

**Configure `git`**

```shell
git config --global gpg.program auto-gpg
git config --global commit.gpgsign true
git config --global tag.gpgsign true
```

## Credits

GUO YANKE, MIT License
