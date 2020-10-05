# ZSH History Manager

This tool is meant to provide functionality that typically comes with a performance impact:

- Be able to quickly search your entire ZSH history, no matter how large.
- Be able to maintain good terminal performance by not holding the entire history in memory.

This tool copies the ZSH History file when run and can deduplicate the commands and produce a new history file.

This means you can have many backups of your history, a master history file, and a shorter actual history file for
maximum shell performance.

The one caveat is that you must use a special command to search the history, `hgi`, which originally came from my tendancy
to run `history | grep -i some-snipped-here` whenever I wanted to perform a history search.

## Installation

1. Create history backup directory:
```bash
mkdir ~/.history_backups
```
2. Clone it:
```bash
git clone https://github.com/ckabalan/histman.git ~/.history_backups/histman
```
3. Initialize virtual environment:
```bash
cd ~/.history_backups/histman
poetry init
```
3. Configure weekly backups. Add the following to your `~/.zshrc`:
```bash
/path/to/poetry/virtualenv/bin/python $HOME/.history_backups/histman/histman.py --backup-with-combine --frequency-days 7
```
4. Configure the history query alias `hgi`. Add the following to your `~/.zshrc`:
```bash
hgi () {
	/path/to/poetry/virtualenv/bin/python $HOME/.history_backups/histman/histman.py --show-live-and-combined $@
}
```

## License

ZSH History Manager is released under the [MIT License](https://opensource.org/licenses/MIT)
