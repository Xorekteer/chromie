import time  # sleep()
import datetime  # datetime.now()
import json  # dump(), load()
import os  # isdir()
import subprocess  # popen

import sys
sys.path.append("../jsondumpable")
sys.path.append("../notifiers")
from jsondumpable import JSONDumpable  # superclass
import mailer


class Scheduler(JSONDumpable):
    """
    Schedules tasks.
    Notifies iff there is any output (can run in background).

    Tunable Class Variables:
        cls.sleep_interval       - sleep interval between checks
        JSONDUMPABLE.dump_file   - name of json file

    Tunable Instance Variables (set them in the JSON file):
        obj.name                 - identifier, can be anything
        obj.job_dates
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
    obj --> set_job_dates(...)
    cls --> schedule()
    cls --> load_from_json_file()
    cls --> run_Scheduler()
        - Main
        - Load from JSON and repeat
    JSONDUMPABLE --> dump_to_json_file()
    
    """



    # Interval between consecutive checks (seconds)
    sleep_interval = 60
    
    # List with all current jobs:
    current_jobs = []
    

    

    def __init__(self, current_jobs=None):
        """ Default init."""
        self.on_missed_call      = "Not implemented."        # Default: "Not implemented"
        self.job_name            = "Unnamed"                 # Default: "Unnamed"
        self.notification_method = "terminal"                # Default: "terminal"
        self.dt_next_run         = datetime.datetime.now()   # set first call time to now
        super().__init__()



    # JSON serialization format string for dtnextrun
    jsnfrmtstrng_dtnextrun = "%Y %m %d %A %H:%M:%S.%f Timezone: NA DoY: %j WoY: %W"

    # Sets next run time. Called automatically on set_job_dates(), so user never has to call it
    def __set_dt_next_run(self):
        self.dt_next_run = datetime.datetime.now()        # current time

        # checking DOW
        # DOW is special because jumping one day could accidentally jump            >
        # over a possible time of running: set instead to next day midnight until   >
        # correct day is found                                                      |
        if "All" not in self.job_dates['dow']:
            while self.dt_next_run.isoweekday() not in self.job_dates['dow']:
                # set to today midnight
                self.dt_next_run = datetime.datetime(self.dt_next_run.year, self.dt_next_run.month, self.dt_next_run.day)
                # add one day
                self.dt_next_run += datetime.timedelta(days=1)

        # checking SECONDS
        if "All" not in self.job_dates['seconds']:
            while self.dt_next_run.second not in self.job_dates['seconds']:
                self.dt_next_run += datetime.timedelta(seconds=1)

        # checking MINUTES
        if "All" not in self.job_dates['minutes']:
            while self.dt_next_run.minute not in self.job_dates['minutes']:
                 self.dt_next_run += datetime.timedelta(minutes=1)

        # checking HOURS
        if "All" not in self.job_dates['hours']:
            while self.dt_next_run.hour not in self.job_dates['hours']:
                self.dt_next_run += datetime.timedelta(hours=1)

        # checking DAYS
        if "All" not in self.job_dates['days']:
            while self.dt_next_run.day not in self.job_dates['days']:
                self.dt_next_run += datetime.timedelta(days=1)

        # checking MONTHS
        if "All" not in self.job_dates['months']:
            while self.dt_next_run.month not in self.job_dates['months']:
                self.dt_next_run += datetime.timedelta(months=1)

        # checking YEARS
        if "All" not in self.job_dates['years']:
            while self.dt_next_run.year not in self.job_dates['years']:
                self.dt_next_run += datetime.timedelta(years=1)

        # Serialize for JSON dumps
        self.dt_next_run_DUMP = self.dt_next_run.strftime(self.__class__.jsnfrmtstrng_dtnextrun)



    # List with all keywords of dict job_date:
    keywordlist = ['dow', 'seconds', 'minutes', 'hours', 'days', 'months', 'years']

    def set_job_dates(self, ISOdow=["All"], seconds=["All"], minutes=["All"], hours=["All"], days=["All"], months=["All"], years=["All"]):
        """Initialize job_dates.

        Keyword Arguments:
            ISOdow  {list of ints / ["All"]}   -- [ISO weekdays so 1=Monday, 7=Sunday]
            minutes {list of ints / ["All"]} 
            days    {list of ints / ["All"]} 
            months  {list of ints / ["All"]} 
            years   {list of ints / ["All"]}
            seconds {list of ints / ["All"]} 
        """
        self.job_dates = dict()
        self.job_dates["dow"]     = ISOdow
        self.job_dates["seconds"] = seconds
        self.job_dates["minutes"] = minutes
        self.job_dates["hours"]   = hours
        self.job_dates["days"]    = days
        self.job_dates["months"]  = months
        self.job_dates["years"]   = years

        self.__set_dt_next_run()



    @classmethod
    def schedule(cls, still_waiting=True):
        "Start scheduler process."
        while True:
            for job in cls.current_jobs:
                if datetime.datetime.now() > job.dt_next_run:
                    p = subprocess.Popen(job.shell_call_string, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                    just_in = p.stdout.read().decode()  # fetch all outputs
                                                        # note: this will also fetch delayed outputs
                    # display any non-empty output from the called script in a terminal paging (echo "text"|less) window
                    if just_in != '':
                        if job.notification_method == 'terminal':
                            subprocess.run('gnome-terminal -- sh -c "echo \'' + str(just_in) + '\'|less"', shell=True)
                        elif job.notification_method == 'email-once':
                            mailer.notify_in_email(just_in)         # send e-mail
                            job.notification_method = 'terminal'    # further notifications in terminal                       
                    job.__set_dt_next_run()   # set next call time
                    job.dump_to_json_file()   # Dump job to JSON
            time.sleep(cls.sleep_interval)


    var_str_list = [
        'job_name',
        'job_dates',
        'shell_call_string',
        'dt_next_run_DUMP',
        'on_missed_call',
        'notification_method'
        ]
    dump_file = 'schfile.json'


    # Validators for loading from JSON
    valid_notification_methods  = ['terminal', 'email-once']     # valid notification methods
    @classmethod
    def load_from_json_file(cls):
        """ Load jobs from an schfile.json """

        nextrun_correction_warning_string = """\
JSON dt_next_run string had to be reformatted. 
The job was run an next run date is set.
You should only see this message if a new job was added.                    
"""
        with open(cls.dump_file, 'r') as file:
            jobs = json.load(file)
            for job in jobs:                            # for each job in the json 
                newjob = cls()                          # create a new instance and initialize
                newjob.job_name            = job['job_name']
                newjob.job_dates           = job['job_dates']
                newjob.shell_call_string   = job['shell_call_string']
                newjob.on_missed_call      = job['on_missed_call']
                newjob.notification_method = job['notification_method']
                
                # Try parsing next run time
                try:
                    newjob.dt_next_run    = datetime.datetime.strptime(
                        job['dt_next_run_DUMP'],
                        cls.jsnfrmtstrng_dtnextrun
                        )
                # Value of dt_next_run not according to specification?
                # This is expected if new job was added.
                except (ValueError, TypeError):
                    subprocess.run('gnome-terminal -- sh -c "echo \'' 
                    + str(nextrun_correction_warning_string)        # warn that next run time will be reset
                    + '\'|less"', shell=True)
                                            
                    newjob.__set_dt_next_run()    # reset next run time
                
                # Validation
                if newjob.notification_method not in cls.valid_notification_methods:
                    subprocess.run('gnome-terminal -- sh -c "echo \'' 
                    + 'Invalid notification method of job ' + newjob.job_name 
                    + '\'|less"', shell=True)
                    raise ValueError("Invalid notification method in JSON")



    @classmethod
    def create_json_file(cls):
        if os.path.exists(os.getcwd() + "/schfile.json"):
            print("JSON exists already.")
        else:
            instance = cls()
            instance.shell_call_string = 'echo "hello"'
            instance.set_job_dates(seconds=[0], minutes=[0])
            # manually empty next run time because we expect user to change job_dates before running, >
            # risking jumping over a run
            instance.dt_next_run_DUMP = ""   
            cls.dump_to_json_file()



    @classmethod
    def run_Scheduler(cls):
        cls.load_from_json_file()
        cls.schedule()


if __name__ == "__main__":
    Scheduler.run_Scheduler()
