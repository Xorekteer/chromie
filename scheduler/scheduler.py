import datetime     # datetime.now()
import time         # sleep()
import json         # dump(), load()
import subprocess   # popen
import os           # isdir()

class Scheduler():
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
        self.__class__.current_jobs.append(self)     # add newly created object to list of current jobs
        # Check passing by reference
        if id(self) != id(self.__class__.current_jobs[-1]):    # error cheching
            raise Exception("Scheduler instance passed to list of Scheduler instances by copying instead of referencing.")



    # Sets next run time. Called automatically on set_job_dates(), so user never has to call it
    def __set_dt_next_run(self):
        self.dt_next_run = datetime.datetime.now()        # current time

        # checking DOW
        if "All" not in self.job_dates['dow']:
            while self.dt_next_run.isoweekday() not in self.job_dates['seconds']:
                self.dt_next_run += datetime.timedelta(seconds=1)

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
            while self.dt_next_run.hour not in self.job_dates['hour']:
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



    def set_shell_call(self, call_str):
        """
        Parameters:
        call_str {string} - The shell command to execute
        """
        self.__shell_call_string = call_str



    @classmethod
    def schedule(cls, still_waiting=True):
        "Start scheduler process."
        while True:
            for job in cls.current_jobs:
                if datetime.datetime.now() > job.dt_next_run:
                    job.__set_dt_next_run()   # next call set first to minimize time offset   >
                                              # in case of long-running script                |
                    job.dump_to_json_file()   # Dump next run's time into the json file
                    p = subprocess.Popen(job.__shell_call_string, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                    just_in = p.stdout.read().decode()  # fetch all outputs
                                                        # note: this will also fetch delayed outputs
                    # display any non-empty output from the called script in a terminal paging (echo "text"|less) window
                    if just_in != '':
                        subprocess.run('gnome-terminal -- sh -c "echo \'' + str(just_in) + '\'|less"', shell=True)                        
            time.sleep(cls.sleep_interval)


    # Create dumpale JSON dict for a single object
    def __create_json_dict(self):
        self.storage_dict = dict()
        self.storage_dict['job_name']               = self.job_name
        self.storage_dict['job_dates']              = self.job_dates
        self.storage_dict['__shell_call_string']    = self.__shell_call_string
        self.storage_dict['dt_next_run']            = self.dt_next_run.strftime(self.__class__.jsnfrmtstrng_dtnextrun)
        self.storage_dict['on_missed_call']         = self.on_missed_call



    @classmethod
    def __get_dumpable_list(cls):
        cls.cls_jsonlist = list()       # list to hold all objects
        for job in cls.current_jobs:    
            job.__create_json_dict()                    # create dict for object variables
            cls.cls_jsonlist.append(job.storage_dict)   # append job to list
        return cls.cls_jsonlist



    @classmethod
    def dump_to_json_file(cls):
        """ Write all current Repeater jobs to a repfile.json """
        with open("schfile.json", "w") as file:
            json.dump(cls.__get_dumpable_list(), file, indent=2)




    @classmethod
    def load_from_json_file(cls):
        """ Load jobs from an schfile.json """

        nextrun_correction_warning_string = """
JSON dt_next_run string had to be reformatted. 
The job was run an next run date is set.
You should only see this message if a new job was added.                    
"""
        with open("schfile.json", 'r') as file:
            jobs = json.load(file)
            for job in jobs:                            # for each job in the json 
                newjob = cls()                          # create a new instance and initialize
                newjob.job_dates            = job['job_dates']
                newjob.__shell_call_string  = job['__shell_call_string']
                try:
                    newjob.dt_next_run      = datetime.datetime.strptime(job['dt_next_run'], cls.jsnfrmtstrng_dtnextrun)
                # Value of dt_next_run nor according to specification. Rectify and warn.
                # This is okay if new job was added.
                except (ValueError, TypeError):
                    subprocess.run('gnome-terminal -- sh -c "echo \'' + str(nextrun_correction_warning_string) + '\'|less"', shell=True)                        
                    newjob.dt_next_run      = datetime.datetime.now()
                newjob.on_missed_call       = job['on_missed_call']



    @classmethod
    def create_json_file(cls):
        if os.path.exists(os.getcwd() + "/schfile.json"):
            print("JSON exists already.")
        else:
            instance = cls()
            instance.set_shell_call('echo "hello"')
            instance.set_job_dates(seconds=[0], minutes=[0])
            cls.dump_to_json_file()



    @classmethod
    def run_Scheduler(cls):
        cls.load_from_json_file()
        cls.schedule()


if __name__ == "__main__":
    Scheduler.run_Scheduler()