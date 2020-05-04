# Chromie -- A python based task scheduler

## What this library does:

Contains a task repeater and a task scheduler. The repeater executes shell calls periodically (e.g. every x hours and y minutes), the scheduler does the same on given times (e.g. every day at 18:00).

These scripts run in the background and open a news terminal if the called script writes anything to the standard output.
Read the usage guide below. The classes were designed with similar interfaces, so the guides are almost identical.

### repeater.py

#### Usage

1. Edit your repfile.json to set up jobs. This should be intuitive (just copy-paste or modify old jobs).
If the repfile is lost, just create one in an interactive python shell using the class's interface.
The following command should work:


`$python3 -i repeater.py`   

`Repeater.create_json_file()`   


2. Run repeater in the background by calling `repeater_background.sh`:

`$./repeater_background.sh`

You can close the terminal: the process will keep running.


3. Kill the process from system monitor or similar if desired.



#### Description

Contians a repeater class.

Each repeater object has:
- A periodicity with which it is called (eg.: every 3 minutes)
- A shell command which is executed upon call    

Settings are stored in repfile.json. 


#### Technical notes

Currently redirects outputs to a new terminal in paging mode (i.e. using `echo OUTPUT|less`).
If there is no output from the called script, no new window is opened.
Input to the called script is not possible.

### scheduler.py

#### Usage

1. Edit your schfile.json to set up jobs. This should be intuitive (just copy-paste or modify old jobs).
If the schfile is lost, just create one in an interactive python shell using the class's interface.
The following command should work:


`$python3 -i repeater.py`   

`Scheduler.create_json_file()`   
  

2. Run repeater in the background by calling `scheduler_background.sh`:

`$./scheduler_background.sh`

You can close the terminal: the process will keep running.


3. Kill the process from system monitor or similar if desired.



#### Description

Contians a scheduler class.

Each scheduler instance has:
- A set of times when it should run (eg. every Sunday 19:00)
- A shell command which is executed upon call    

Settings are stored in repfile.json. 


#### Technical notes

Currently redirects outputs to a new terminal in paging mode (i.e. using `echo OUTPUT|less`).
If there is no output from the called script, no new window is opened.
Input to the called script is not possible.
