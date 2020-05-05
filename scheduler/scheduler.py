import datetime     # datetime.now()
import time         # sleep()
import json         # dump(), load()
import subprocess   # popen
import os           # isdir()
import sys
sys.path.append("../jsondumpable")
from jsondumpable import JSONDumpable

class Scheduler(JSONDumpable):
    """Class scheduler.

    cls.run()                       -   start process of scheduling
    cls.load_from_json_file(...)
    cls.dump_to_json_file(...)
    cls.sleep_interval              -   sleep interval between task checks    
    cls.current_jobs                -   all current jobs in the class
    cls.keywordlist                 -   all string keys of obj.job_dates and obj.job_m_dates in a list
    cls.schedule()

    obj.dt_next_run
    obj.job_dates           -   human readable scheduling dates
    obj.set_job_dates(...)  -   set job dates manually
    obj.__set_dt_next_run() 
    """
    # Next run time format string
    jsnfrmtstrng_dtnextrun = "%Y %m %d %A %H:%M:%S.%f Timezone: NA DoY: %j WoY: %W"

    # Interval between consecutive checks (seconds)
    sleep_interval = 5
    
    # List with all current jobs:
    current_jobs = []
    
    # List with all job_date keywords:
    keywordlist = ['dow', 'seconds', 'minutes', 'hours', 'days', 'months', 'years']
    
    # Default string for on_missed_call once the behaviour is implemented.
    dev_onmissedcalldefaultstring = "Undefined. Set CallOnce OR CallAll OR Defer"
    # 
    def __init__(self, job_name="Unnamed", current_jobs=None, on_missed_call="Not implemented."):
        """ Default init."""
        self.on_missed_call = on_missed_call
        self.job_name = job_name
        self.dt_next_run = datetime.datetime.now()   # set first call time to now
        super().__init__()


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

        # Serialize for JSON Dumps
        self.dt_next_run_DUMP = self.dt_next_run.strftime(self.__class__.jsnfrmtstrng_dtnextrun)



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
                    job.__set_dt_next_run()   # next call set first to minimize time offset   >
                                              # in case of long-running script                |
                    job.dump_to_json_file()   # Dump next run's time into the json file
                    p = subprocess.Popen(job.shell_call_string, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                    just_in = p.stdout.read().decode()  # fetch all outputs
                                                        # note: this will also fetch delayed outputs
                    # display any non-empty output from the called script in a terminal paging (echo "text"|less) window
                    if just_in != '':
                        subprocess.run('gnome-terminal -- sh -c "echo \'' + str(just_in) + '\'|less"', shell=True)                        
            time.sleep(cls.sleep_interval)


    var_str_list = [
        'job_name',
        'job_dates',
        'shell_call_string',
        'dt_next_run_DUMP',
        'on_missed_call'
        ]
    dump_file = 'schfile.json'


    @classmethod
    def load_from_json_file(cls):
        """ Load jobs from an schfile.json """

        nextrun_correction_warning_string = """
JSON dt_next_run string had to be reformatted. 
The job was run an next run date is set.
You should only see this message if a new job was added.                    
"""
        with open(cls.dump_file, 'r') as file:
            jobs = json.load(file)
            for job in jobs:                            # for each job in the json 
                newjob = cls()                          # create a new instance and initialize
                newjob.job_dates       = job['job_dates']
                newjob.job_dates       = job['job_dates']
                newjob.shell_call_string  = job['shell_call_string']
                try:
                    newjob.dt_next_run      = datetime.datetime.strptime(
                        job['dt_next_run_DUMP'],
                        cls.jsnfrmtstrng_dtnextrun
                        )
                # Value of dt_next_run nor according to specification. Rectify and warn.
                # This is okay if new job was added.
                except (ValueError, TypeError):
                    subprocess.run('gnome-terminal -- sh -c "echo \'' 
                    + str(nextrun_correction_warning_string) 
                    + '\'|less"', shell=True)
                                            
                    newjob.dt_next_run      = datetime.datetime.now()
                newjob.on_missed_call       = job['on_missed_call']



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