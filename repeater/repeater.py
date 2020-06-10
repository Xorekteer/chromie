import time             # sleep()
import subprocess       # run(), Popen()
import json             # dump(), load()
import os               # path.exists()
import sys              # path.append()

# External dependencies:
# Load from ..chromie/dep.txt:
with open("../dep.txt", 'r') as dep_file:
    deplist = list(line for line in dep_file.readlines())
for dep in deplist:
    if dep[-1] == "\n":
        dep = dep[:-1]
    sys.path.append(dep)
from jsondumpable.jsondumpable import JSONDumpable   # superclass

# Internal dependencies
sys.path.append("../notifiers")
import mailer # notify_by_email()

class Repeater(JSONDumpable):
    """
    Repeats task periodically.
    Notifies iff there is any output (can run in background).

    Tunable Class Variables:
        cls.sleep_interval       - sleep interval between checks
        JSONDUMPABLE.dump_file   - name of json file

    Tunable Instance Variables (set them in the JSON file):
        obj.name                 - identifier, can be anything
        obj.delay_dict           - repetition delay
        obj.notification_method  - notification method
        obj.shell_call_sting     - shell call to be executed upon repetition
            options:
                'terminal'   -- prints any stdout to a gnome terminal
                'email-once' -- send an email once using mailer.py(TEMPLATE)
                             >> then set to 'terminal'
    
    Other Class Variables:
        JSONDUMPABLE.var_str_list  - {list of strings} list of variables to be dumped
    
    Interface:
        cls.create_json_file()  
            - creates JSON file if not present
            - use in INTERACTIVE MODE
    
    Debugging interface (Use JSON file instead): 
    obj --> set_first_call(delay_in_sec)
    obj --> set_delay(seconds=0, minutes=0, hours=0, days=0, weeks=0)
    cls --> repeat()
    cls --> load_from_json_file()
    cls --> run_Repeater()
        - Main
        - Load from JSON and repeat
    JSONDUMPABLE --> dump_to_json_file()
    
    """

    # Interval between consecutive checks
    sleep_interval = 30      

    # Definitions of time
    chro_minute =   60
    chro_hour   =   60 * chro_minute
    chro_day    =   24 * chro_hour
    chro_week   =    7 * chro_day 

    # No init arguments since jobs are loaded from a JSON anyway
    def __init__(self, current_jobs=None):
        super().__init__()
        self.next_call           = time.time()   # set first call time to now
        self.name                = "Unnamed"
        self.notification_method = 'terminal'    # stoud piped to terminal by default




    def set_delay(self, seconds=0, minutes=0, hours=0, days=0, weeks=0):
        """ Sets delay between tasks.

        Kwargs:            
        seconds {float}       
        minutes {float}       
        hours   {float}       
        days    {float}       
        weeks   {float}
        """       
        self.delay_dict = {
            "seconds"  : seconds,
            "minutes"  : minutes,
            "hours"    : hours,
            "days"     : days,
            "weeks"    : weeks
            }
        self.delay_float = weeks*self.chro_week + days*self.chro_day + hours*self.chro_minute + seconds


    # Sets next call relative to current time
    def __set_next_call(self):
        self.next_call = time.time() + self.delay_float

 

    @classmethod
    def repeat(cls, still_waiting=True):
        "Start repeater process."
        while True:
            for job in cls.current_jobs:
                if time.time() > job.next_call:
                    p = subprocess.Popen(job.shell_call_string, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                    just_in = p.stdout.read().decode()  # fetch all outputs
                                                        # note: this will also fetch delayed outputs
                    # display any non-empty output from the called script in a terminal paging (echo "text"|less) window
                    if just_in != '':
                        if job.notification_method == 'terminal':
                            subprocess.run('gnome-terminal -- sh -c "echo \'' + str(just_in) + '\'|less"', shell=True)
                        elif job.notification_method == 'email-once':   # email-once?   >
                            mailer.notify_by_email(just_in)             # send e-mail   >
                            job.notification_method = 'terminal'        # further notifications in terminal |
                        elif job.notification_method == 'email-only':   # email-onlu?   >
                            mailer.notify_by_email(just_in)             # send e-mail
                    job.__set_next_call()   # set next call
                    job.dump_to_json_file()
            time.sleep(cls.sleep_interval)

    # JSONDumpable settings
    var_str_list = ['name' ,'next_call', 'delay_dict', 'shell_call_string', 'notification_method']
    dump_file = 'repfile.json'


    # Validators for loading from JSON
    valid_notification_methods  = ['terminal', 'email-once', 'email-only']     # valid notification methods
    @classmethod
    def load_from_json_file(cls):
        """ Load jobs from a repfile.json """
        with open(cls.dump_file, 'r') as file:
            jobs = json.load(file)
            for job in jobs:                            # for each job in the json 
                newrep = cls()                          # create a new instance and initialize
                newrep.next_call   = job['next_call']
                newrep.delay_dict  = job['delay_dict']
                newrep.delay_float = ( 
                      float( job['delay_dict']['weeks']   )   * cls.chro_week
                    + float( job['delay_dict']['weeks']   )   * cls.chro_week
                    + float( job['delay_dict']['hours']   )   * cls.chro_hour
                    + float( job['delay_dict']['minutes'] )   * cls.chro_minute
                    + float( job['delay_dict']['seconds'] )
                )
                newrep.shell_call_string   = job['shell_call_string']
                newrep.name                = job['name']
                newrep.notification_method = job['notification_method']
                # Validation
                if newrep.notification_method not in cls.valid_notification_methods:
                    subprocess.run('gnome-terminal -- sh -c "echo \'' 
                    + 'Invalid notification method of job ' + newrep.name 
                    + '\'|less"', shell=True)
                    raise ValueError("Invalid notification method in JSON")

    @classmethod
    def create_json_file(cls):
        """
        Recreates the JSON file if it doesn't exists.
        Default job calls 'echo hello' every 30 seconds.
        """
        if os.path.exists(os.getcwd() + "/" + cls.dump_file):
            print("JSON exists already.")
        else:
            instance = cls()
            instance.shell_call_string = 'echo "hello"'
            instance.set_delay(seconds=30)
            cls.dump_to_json_file()


    @classmethod
    def run_Repeater(cls):
        cls.load_from_json_file()
        cls.repeat()



if __name__ == "__main__":
    Repeater.run_Repeater()