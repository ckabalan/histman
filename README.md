# ZSH History Manager

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
