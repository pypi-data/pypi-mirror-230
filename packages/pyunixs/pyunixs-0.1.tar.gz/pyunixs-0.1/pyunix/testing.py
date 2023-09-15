

from getpass import getuser
from socket import gethostname
from os import getcwd, chdir
from termcolor import colored
from os.path import expanduser, exists
import readline, glob
import sys

def tab_auto_completion():
    readline.set_completer_delims(' \t\n;')
    readline.parse_and_bind("tab: complete")
    readline.set_completer(complete_line)

def get_ps1():
    user_name = getuser()
    directory = getcwd()
    ps1 = f"{user_name} : {directory}$ " 
    return ps1

def complete_line(text, state):
    return (glob.glob(text+'*')+[None])[state]

def pre_loop(histfile):
    if readline:
            readline.read_history_file(histfile)

def post_loop(histfile, histfile_size):
    if readline:
        readline.set_history_length(histfile_size)
        readline.write_history_file(histfile)

def redirect_in(cmd): # '<'
    if "<" not in cmd:
        return cmd

    
    command, file_name = cmd.rsplit('<',1)
    print(command, file_name)

    try:
        if command and file_name and command.count("'") % 2 == 0 and command.count('"') % 2 == 0:
            command = command.strip()
            file_name = file_name.strip()

            file_name =  expanduser(file_name)
            return f"cat {file_name} | {command}"
    except FileNotFoundError as e:
        print(colored(f"ERROR FileNotFoundError: {e}", "red"))

    return cmd

def unix_split(cmd):
    single_quotes = 0
    double_quotes = 0
    cmd_list = []
    cmd = cmd.strip()
    tmp = ""
    
    for letter in cmd:
        if letter == "'":
            single_quotes += 1
        if letter == '"':
            double_quotes += 1

        if letter == " " and single_quotes % 2 == 0 and double_quotes % 2 == 0:
            cmd_list.append(tmp)
            tmp = ""
        else:
            tmp = tmp + letter

    if tmp != "":
        cmd_list.append(tmp)

    return cmd_list


def letter_parser(cmd, raw_execution, single_quotes, double_quotes):
    cmd_list = []
    tmp = ""

    for i,letter in enumerate(cmd):

        if letter == "'":
            single_quotes += 1
        if letter == '"':
            double_quotes += 1


        if letter in ['|', '>', '<'] and single_quotes % 2 == 0 and double_quotes % 2 == 0:
            cmd_list.append(tmp)
            cmd_list.append(letter)
            tmp = ""
            raw_execution = 0

        else:
            tmp = tmp + letter

    if tmp != "":
        cmd_list.append(tmp)

    return raw_execution, cmd_list, single_quotes, double_quotes


def custom_parser(cmd):
    cmd_list = []
    tmp = ""
    raw_execution = 1

    for i,word in enumerate(unix_split(cmd)):
        if (word.endswith(">") and len(word)<4 and '\\' not in word):
            cmd_list.append(tmp)
            cmd_list.append(word)
            tmp = ""
            raw_execution = 0

        else:
            word = word.replace("\>",">")
            word = word.replace("\|","|")
            tmp = tmp + " " + word

    if tmp != "":
        cmd_list.append(tmp)

    output_cmd_list = []
    single_quotes = 0
    double_quotes = 0

    for line in cmd_list:
        raw_execution, tmp_list, single_quotes, double_quotes = letter_parser(line, raw_execution, single_quotes, double_quotes)
        output_cmd_list += tmp_list

    for i in range(len(output_cmd_list)):
        line = output_cmd_list.pop(0)
        if line.strip() != "":
            output_cmd_list.append(line)
        

    return raw_execution, output_cmd_list




        
def shell():

    #for history
    histfile = expanduser('~/.unix__history')
    if not exists(histfile):
        with open(histfile, "w+") as f:
            pass
    histfile_size = 6000

    #for tab auto completion
    tab_auto_completion()

    while True:
        ps1 = get_ps1()
        pre_loop(histfile)
        cmd = input(colored(ps1,"white")).strip()
        
        if cmd == "exit":
                break
        
        
        if cmd.strip() == "":
            continue
    

        raw_cmd = cmd
        cmd = redirect_in(cmd)
        raw_execution, cmd_list = custom_parser(cmd)
        #print(cmd_list)

        if raw_execution:

            cd_check = cmd_list[0].strip().split()
            if cd_check[0] == "cd" and len(cd_check) == 2:
                chdir(expanduser(cd_check[1]))
                continue

            p = execute(raw_cmd, cmd_list[0], sys.stdin, sys.stdout, sys.stderr)
            if p:
                p.wait()
            continue
    

        post_loop(histfile, histfile_size)


if __name__ == "__main__":
    shell()
    
