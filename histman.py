import click
import glob
import os
import re
from datetime import date, datetime
import shutil
import gnupg
import gzip

@click.command()
@click.option('--history-file', default=f"{os.environ['HOME']}/.zsh_history", help='Main ZSH history file')
@click.option('--backup-dir', default=f"{os.environ['HOME']}/.history_backups", help='ZSH history backups directory')
@click.option('--frequency-days', default=7, help='Number of days between backups')
@click.option('--backup', is_flag=True, help='Perform the backup if --frequency-days has passed since last backup.')
@click.option('--backup-with-combine', is_flag=True, help='Same behavior as --backup, but runs --generate-combined if a backup occured.')
@click.option('--encrypted-backup-dir', help='Directory to copy encrypted version on combined.zsh_history to.')
@click.option('--gnupg-recipient', help='Recipient for GnuPG encrypted backup.')
@click.option('--generate-combined', is_flag=True, help='Generate a combined.zsh_history file with all backed-up history.')
@click.option('--show-live-and-combined', is_flag=True, help='Mimic history -l showing combined.zsh_history and --history_file')
@click.argument('grep', nargs=-1)


def main(history_file, backup_dir, frequency_days, backup, backup_with_combine, encrypted_backup_dir, gnupg_recipient, generate_combined, show_live_and_combined, grep):
    if backup or backup_with_combine:
        perform_backup(history_file, backup_dir, frequency_days, backup_with_combine, encrypted_backup_dir, gnupg_recipient)
    if generate_combined:
        combine_history(history_file, backup_dir)
    if show_live_and_combined:
        greps = []
        for cur_grep in grep:
            if cur_grep.startswith('\'') and cur_grep.endswith('\''):
                greps.append(cur_grep[1:-1])
            else:
                greps.append(cur_grep)
        print_history(history_file, backup_dir, greps)

def print_history(history_file, backup_dir, greps):
    for history_file in [f"{backup_dir}/combined.zsh_history", history_file]:
        with open(history_file) as file:
            line = file.readline()
            cur_line = ''
            while line:
                cur_line += line
                if not line.endswith('\\\n'):
                    print_line(cur_line, greps)
                    cur_line = ''
                line = file.readline()

def print_line(line, greps):
    linesplit = line.split(';', 1)
    for grep in greps:
        if re.search(grep, linesplit[1]) is None:
            return
    unix_time = int(linesplit[0].split(':')[1].strip())
    dt = datetime.fromtimestamp(unix_time).strftime("%Y-%m-%d %H:%M")
    click.echo(f"{dt} > {linesplit[1]}", nl=False)

def combine_history(history_file, backup_dir):
    history_files = sorted(glob.glob(f"{backup_dir}/*-*-*.zsh_history"))
    #history_files.append(history_file)
    cmd_set = set()
    total_cmds = 0
    for history_file in history_files:
        with open(history_file) as file:
            line = file.readline()
            cur_line = ''
            file_cmds = 0
            while line:
                cur_line += line
                if not line.endswith('\\\n'):
                    cmd_set.add(cur_line)
                    cur_line = ''
                    file_cmds += 1
                line = file.readline()
        click.echo(f"Read {file_cmds} ({len(cmd_set) - total_cmds} new) commands from {history_file}.")
        total_cmds = len(cmd_set)
    cmd_set = sorted(cmd_set)
    dst = f"{backup_dir}/combined.zsh_history"
    with open(dst, 'w') as file:
        click.echo(f"Writing {dst} ({total_cmds} commands).")
        for cmd in cmd_set:
            file.write(cmd)
        os.chmod(dst, 0o600)

def copy_encrypted_history(backup_dir, encrypted_backup_dir, gnupg_recipient):
    src_raw = f"{backup_dir}/combined.zsh_history"
    dst_filename = f"combined.zsh_history.{date.today().strftime('%Y-%m-%d')}"
    dst_gzip = f"{backup_dir}/{dst_filename}.gz"
    dst_gpg = f"{encrypted_backup_dir}/{dst_filename}.gz.gpg"
    with open(src_raw, 'rb') as f_in:
        with gzip.open(dst_gzip, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
    with open(dst_gzip, 'rb') as f:
        click.echo(f"Encrypting {src_raw} to {dst_gpg}.")
        gpg = gnupg.GPG()
        status = gpg.encrypt_file(f, recipients=[gnupg_recipient], output=dst_gpg)
    os.remove(dst_gzip)
    click.echo(f"Done! You may decrypt {dst_gpg} with the GnuPG Key {gnupg_recipient}.")



def perform_backup(history_file, backup_dir, frequency_days, backup_with_combine, encrypted_backup_dir, gnupg_recipient):
    file_list = sorted(glob.glob(f"{backup_dir}/*-*-*.zsh_history"))
    perform_backup = False
    if len(file_list) == 0:
        perform_backup = True
        delta_days = -1
    else:
        latest_file = file_list[-1]
        filename = os.path.basename(latest_file)
        filedate = datetime.strptime(filename, '%Y-%m-%d.zsh_history').date()
        delta_days = (date.today() - filedate).days
        if delta_days > frequency_days:
            perform_backup = True
    if perform_backup:
        new_filename = f"{date.today().strftime('%Y-%m-%d')}.zsh_history"
        new_file = f"{backup_dir}/{new_filename}"
        if delta_days == -1:
            click.echo(f"ZSH history has never been backed up. Backing up to {new_filename}.")
        else:
            click.echo(f"Last ZSH history backup {delta_days}d ago. Backing up to {new_filename}.")
        shutil.copy2(history_file, new_file)
        if backup_with_combine:
            combine_history(history_file, backup_dir)
        if encrypted_backup_dir:
            copy_encrypted_history(backup_dir, encrypted_backup_dir, gnupg_recipient)

if __name__ == '__main__':
    main()

