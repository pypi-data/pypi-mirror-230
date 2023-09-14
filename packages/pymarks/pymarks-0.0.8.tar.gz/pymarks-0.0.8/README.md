<div align="center">

![Python](https://img.shields.io/badge/python-3670A0?style=Flat&logo=python&logoColor=ffdd54)
![SQLite](https://img.shields.io/badge/sqlite-%2307405e.svg?style=Flat&logo=sqlite&logoColor=white)
[![Hatch project](https://img.shields.io/badge/%F0%9F%A5%9A-Hatch-4051b5.svg)](https://github.com/pypa/hatch)
[![linting - Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/charliermarsh/ruff/main/assets/badge/v0.json)](https://github.com/charliermarsh/ruff)
[![code style - Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![types - Mypy](https://img.shields.io/badge/types-Mypy-blue.svg)](https://github.com/python/mypy)
[![License - MIT](https://img.shields.io/badge/license-MIT-9400d3.svg)](https://spdx.org/licenses/)

</div>

## PyMarks (WIP)

### 🌟 About

`PyMarks` is a Python program designed to help you manage your bookmarks in a
more efficient way. Uses `SQLite3` as a database to store your bookmarks,
allowing you to `add`, `delete` and `update` them as needed.

To make it easier to access your bookmarks, the program provides a menu system
that can be accessed using tools such as `Dmenu`, `Rofi` or `fzf` in terminal.
With this menu system, you can search and `fuzzy` find the bookmark you're
looking for, and then open it in your preferred web browser. `PyMarks` is a
great tool for anyone who wants to keep their bookmarks organized and
accessible.

### ⚡️ Requirements

- [Rofi](https://github.com/davatorium/rofi) _(You have more options)_
- [dmenu](https://tools.suckless.org/dmenu/) _(Optional)_
- [fzf](https://github.com/junegunn/fzf) _(Optional)_
- xclip _(clipboard)_

### 📦 Installation

You can install this tool using `pipx` _(recommended)_, `pip` or by `cloning`
the repository

#### ⭐ Using pipx _(recommended)_

```bash
pipx install pymarks
```

#### Using pip

```bash
pip install pymarks
```

#### Clone repository

```bash
# clone repository
$ git clone "https://github.com/haaag/PyMarks"
$ cd PyMarks

# create virtual environment & source
$ python -m venv .venv && source .venv/bin/activate

# install dependencies
$ pip install -r requirements.txt

# run
$ pymarks
```

### 🚀 Usage

```bash
$ pymarks --help
PyMarks is a simple tool to assist you in efficiently
organizing and managing your bookmarks.

The tool simplifies the process of accessing, adding, updating,
and removing bookmarks.

options:
    -m, --menu                  Select menu (default: rofi)
    -V, --version               Show version
    -h, --help                  Show help
    -v, --verbose               Verbose mode

supported menus:
   ['dmenu', 'rofi', 'fzf']

optional environment variables:
    PYMARKS_HOME                Overrides default PyMarks location
    PYMARKS_BACKUP_MAX_AGE      Overrides backup age check interval
    PYMARKS_BACKUP_MAX_AMOUNT   Overrides backup max amount
```

#### ⌨️ Keybinds (rofi exclusive)

If using `rofi`, you can use some `keybinds`.

| Keybind   | Description       |
| --------- | ----------------- |
| **Alt+a** | Add new bookmark  |
| **Alt+c** | Change `database` |
| **Alt+d** | Record detail     |
| **Alt+e** | Record options    |
| **Alt+i** | App information   |
| **Alt+t** | Filter by `tag`   |

### 📁 Folder structure

Directory structure _(`$XDG_CONFIG_HOME/pymarks`)_

```bash
$ ~/.config/pymarks (main*) tree
├── backup
│   ├── YYYY-MM-DD_bookmarks.db
│   └── YYYY-MM-DD_bookmarks.db
└── databases
    ├── bookmarks.db <-- Default
    ├── trash.db     <-- Deleted records
    ├── private.db
    └── work.db
```

### 🔥 Similar projects and inspiration

- [Buku](https://github.com/jarun/buku) 🌟 Thank You 🤘

<details>
<summary>Done</summary>

### TODO

#### Priority

| Description                                | Progress                                                           |
| ------------------------------------------ | ------------------------------------------------------------------ |
| Use `XDG_DIRS`                             | ![100%](https://progress-bar.dev/100/?title=done&color=555555)     |
| Add `encrypt/decrypt` option to `database` | ![Planned](https://progress-bar.dev/0/?title=planned&color=b8860b) |
| Create `deleted/removed` table             | ![Planned](https://progress-bar.dev/0/?title=planned&color=b8860b) |
| Get `keybinds` in `dmenu/fzf` to work      | ![Planned](https://progress-bar.dev/0/?title=planned&color=b8860b) |

#### Environment variables

| Description               | Progress                                                       |
| ------------------------- | -------------------------------------------------------------- |
| PYMARKS_HOME              | ![100%](https://progress-bar.dev/100/?title=done&color=555555) |
| ~~PYMARKS_BACKUP_WATCH~~  | ![100%](https://progress-bar.dev/100/?title=done&color=555555) |
| PYMARKS_BACKUP_MAX_AGE    | ![100%](https://progress-bar.dev/100/?title=done&color=555555) |
| PYMARKS_BACKUP_MAX_AMOUNT | ![100%](https://progress-bar.dev/100/?title=done&color=555555) |

#### Actions

| Description                                                 | Progress                                                           |
| ----------------------------------------------------------- | ------------------------------------------------------------------ |
| Update record _(tags, URL)_                                 | ![100%](https://progress-bar.dev/100/?title=done&color=555555)     |
| Delete record _(tags, URL)_                                 | ![100%](https://progress-bar.dev/100/?title=done&color=555555)     |
| Option to switch databases                                  | ![100%](https://progress-bar.dev/100/?title=done&color=555555)     |
| Option to add/remove database                               | ![100%](https://progress-bar.dev/100/?title=done&color=555555)     |
| Option to show information _(backups, keys, records, etc)_  | ![100%](https://progress-bar.dev/100/?title=done&color=555555)     |
| Scrape `title` from website                                 | ![100%](https://progress-bar.dev/100/?title=done&color=555555)     |
| Scrape `Description` from website                           | ![100%](https://progress-bar.dev/100/?title=done&color=555555)     |
| Multi-Select _(for delete? for migrate? for any action…🤔)_ | ![Planned](https://progress-bar.dev/0/?title=planned&color=b8860b) |

#### Databases

| Description                                               | Progress                                                           |
| --------------------------------------------------------- | ------------------------------------------------------------------ |
| Add support for multi-database _(e.g: personal and work)_ | ![100%](https://progress-bar.dev/100/?title=done&color=555555)     |
| ~~Create `trash.db` or `dump.db` for deleted records~~    | ![100%](https://progress-bar.dev/100/?title=done&color=555555)     |
| Option to migrate from `deleted` to `bookmark` table      | ![Planned](https://progress-bar.dev/0/?title=planned&color=b8860b) |
| Option to search in **ALL** databases                     | ![Planned](https://progress-bar.dev/0/?title=planned&color=b8860b) |

#### Backups

| Description                                                       | Progress                                                       |
| ----------------------------------------------------------------- | -------------------------------------------------------------- |
| Prompt for backup every `<PYMARKS_BACKUP_MAX_AGE>` number of days | ![100%](https://progress-bar.dev/100/?title=done&color=555555) |
| Option to disable check on runtime                                | ![100%](https://progress-bar.dev/100/?title=done&color=555555) |
| Keep `<PYMARKS_BACKUP_MAX_AMOUNT>` of backup files                | ![100%](https://progress-bar.dev/100/?title=done&color=555555) |

#### Misc

| Description                                                       | Progress                                                           |
| ----------------------------------------------------------------- | ------------------------------------------------------------------ |
| Add renumbered for the `rowid` _(Each time a record is deleted?)_ | ![Planned](https://progress-bar.dev/0/?title=planned&color=b8860b) |
| ~~Add URL `validation` when reading from clipboard~~              | ![Planned](https://progress-bar.dev/1/?title=suspended)            |

</details>
