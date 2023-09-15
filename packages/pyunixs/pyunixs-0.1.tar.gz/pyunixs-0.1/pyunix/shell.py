from getpass import getuser
from socket import gethostname
from os import getcwd, chdir
from termcolor import colored
from os.path import expanduser, exists
import subprocess
import readline, glob
import shlex
import sys



# function for auto tab completion
def tab_auto_completion():
    readline.set_completer_delims(' \t\n;')
    readline.parse_and_bind("tab: complete")
    readline.set_completer(complete_line)

#function to get ps1
def get_ps1():
   
    branch = ""
    try:
        result = subprocess.check_output(['git', 'branch', '--show-current'], stderr=subprocess.DEVNULL,universal_newlines=True)
        branch = result.strip()
    
    except subprocess.CalledProcessError as e:
        branch = ""

    user_name = getuser()
    host_name = gethostname()
    directory = getcwd()
    if branch != "":
        ps1 = f"👋 {user_name}@{host_name} : {directory} : git({branch}) ⚡️ "  #ps1 => primary prompt variable
    else : 
        ps1 = f"👋 {user_name}@{host_name} : {directory} ⚡️ "  #ps1 => primary prompt variable

    return ps1

# auto complete file names using glon
def complete_line(text, state):
    return (glob.glob(text+'*')+[None])[state]

# run the cmd using subprocess
def execute(raw_cmd, cmd, stdin, stdout, stderr):
    
    try:
        p = subprocess.Popen(shlex.split(cmd), stdin = stdin, stdout = stdout, stderr = stderr)
        return p
    except Exception as e:
        print(colored(f"Please check the command: {raw_cmd}\nERROR: {e}", "red"))

# function to process the redirection work using 
def redirect_out(symbol, location, p): # '>'

    if not p:
        return

    out = p.stdout
    mode = "w"
    location = expanduser(location)
    if symbol.endswith(">>"):
        mode = "a"

    if (len(symbol) == 2 or len(symbol) == 3) and ord(symbol[0]) == 50:
        if p.stderr:
            out = p.stderr

    try:
        with open(location.strip(), mode) as f:
            for line in iter(out.readline, b''):
                f.write(line.decode())
    except FileNotFoundError as e:
        print(colored(f"ERROR FileNotFoundError: {e}", "red"))

# function to check the < redirection cmd
def redirect_in(cmd): # '<'
    if "<" not in cmd:
        return cmd

    
    command, file_name = cmd.rsplit('<',1)
    #print(command, file_name)

    try:
        if command and file_name and command.count("'") % 2 == 0 and command.count('"') % 2 == 0:
            command = command.strip()
            file_name = file_name.strip()

            file_name =  expanduser(file_name)


           # print(f"cat {file_name} | {command}")


            return f"cat {file_name} | {command}"
    except FileNotFoundError as e:
        print(colored(f"ERROR FileNotFoundError: {e}", "red"))

    return cmd
#function to check the redirection
def execute_redirection(symbol, location, cmd_output):
    if symbol.endswith(">"):
        redirect_out(symbol, location, cmd_output)

    return {"returncode": 0, 'stdout': "", 'stdin': ""}

def pre_loop(histfile):
    if readline:
            readline.read_history_file(histfile)


#function to save the last executed cmd to history
def post_loop(histfile, histfile_size):
    if readline:
        readline.set_history_length(histfile_size)
        readline.write_history_file(histfile)
        
# function to check any redirection and quotes are closed properly
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

#function to check the double quotes character by character
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

# function to remove escape deliminator in the entered cmd
def custom_parser(cmd):
    cmd_list = []
    tmp = ""
    raw_execution = 1

    ## if any \ is added before cmd replace it 

    for i,word in enumerate(unix_split(cmd)):
        

        if (word.endswith(">") and len(word)<4 and '\\' not in word):
            cmd_list.append(tmp)
            cmd_list.append(word)
            tmp = ""
            raw_execution = 0
            print(cmd_list)

        else:
            word = word.replace("\>",">")
            word = word.replace("\|","|")
            tmp = tmp + " " + word
          #  print(f"tmp:{tmp}")

    if tmp != "":
        cmd_list.append(tmp)

    output_cmd_list = []
    single_quotes = 0
    double_quotes = 0
     
     # checking no of single quotes and double quotes in the code

    for line in cmd_list:
        raw_execution, tmp_list, single_quotes, double_quotes = letter_parser(line, raw_execution, single_quotes, double_quotes)
        output_cmd_list += tmp_list

    #print(f"output : {output_cmd_list}")

    for i in range(len(output_cmd_list)):
        line = output_cmd_list.pop(0)
        if line.strip() != "":
            output_cmd_list.append(line)
        
  #  print(f"raw : {raw_execution}, output : {output_cmd_list}")
    return raw_execution, output_cmd_list

# function to display history
def display_history_file(file_path):
    try:
        with open(file_path, 'r') as file:
            print("Contents of History File:")
            line_number = 1
            line = file.readline()
            while line:
                print(f"{line_number}: {line.strip()}")
                line_number += 1
                line = file.readline()
    except FileNotFoundError:
        print(f"Error: The history file '{file_path}' was not found.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")


## function to get input
def shell():

    #for histoy
    histfile = expanduser('~/.py_shell_history')
    if not exists(histfile):
        with open(histfile, "w+") as f:
            pass
    histfile_size = 1000

    #for tab auto completion
    tab_auto_completion()

    while True:
        ps1 = get_ps1()
        pre_loop(histfile)
        cmd = input(colored(ps1,"green", attrs=['bold'])).strip()
        
        if cmd == "exit":
                break
        if cmd == "history":
            display_history_file(expanduser('~/.py_unix_shell_history'))
            continue
        
        if cmd.strip() == "":
            continue

        raw_cmd = cmd
        cmd = redirect_in(cmd)
        
       # print(f"out -  redirect : {cmd}")
        raw_execution, cmd_list = custom_parser(cmd)
        #print(cmd_list)

        # cd cmd executed here from chdir
        if raw_execution:

            cd_check = cmd_list[0].strip().split()
            if cd_check[0] == "cd" and len(cd_check) == 2:
                chdir(expanduser(cd_check[1]))
                continue

            p = execute(raw_cmd, cmd_list[0], sys.stdin, sys.stdout, sys.stderr)
            if p:
                p.wait()
            continue

        pipe_check = 0
        redirect_check = 0
        redirect_symbol = ""
        p = None

        for i, line in enumerate(cmd_list):

            if line == "|":
                pipe_check = 1
                continue
            elif line.endswith(">") or line.endswith(">>"):
                redirect_symbol = line
                redirect_check = 1
                continue
            
            if pipe_check == 1:
                if not p:
                    break
                if i == len(cmd_list)-1:
                    p = execute(raw_cmd, line, p.stdout, sys.stdout, sys.stderr)
                else:
                    p = execute(raw_cmd, line, p.stdout, subprocess.PIPE, subprocess.PIPE)
                pipe_check = 0

            elif redirect_check == 1:
                redirect_out(redirect_symbol, line, p)
                redirect_check = 0
                redirect_symbol = ""
            else:
                p = execute(raw_cmd, line, None, subprocess.PIPE, subprocess.PIPE)

            if p:
                p.wait()

        post_loop(histfile, histfile_size)


if __name__ == "__main__":
    shell()
    
