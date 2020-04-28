# Chromie -- A python based task scheduler

## What this library does:

It contains a task scheduler (NOT IMPLEMENTED) and a task repeater (EXPERIMENTAL).

### repeater.py
#### Summary:

Allows the periodic execution of shell scripts with predefined delay.
Example: call a script every x minutes.
Runs in the background and opens a news terminal if the called script writes anything to the standard output.

#### Usage

1. Edit your repfile.json to set up jobs. This should be intuitive (just copy-paste or modify old jobs).
If the repfile is lost, just create one in an interactive python shell using the class's interface.
The following command should work:

<code>
$python3 -i repeater.py
rep = Repeater()<br>
rep.set_delay(minutes=1)<br>
rep.set_shell_call("echo hello")<br>    
Repeater.dump_to_json_file()<br>  
</code>

2. Run repeater in the background by calling it from a terminal using the following:

<code>
$nohup python3 repeater.py &
</code>

You can close the terminal: the process will keep running.


3. Kill the process from system monitor or similar if desired.



#### Description

Contians a repeater class.

Each repeater object has:
- A periodicity with which it is called
- A shell command which is executed upon call    

Settings are stored in repfile.json. 


#### Technical notes

Currently redirects outputs to a new terminal in paging mode (i.e. using echo OUTPUT|less )