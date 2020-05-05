import time             # sleep()
import subprocess       # run(), Popen()
import json             # dump(), load()
import os               # path.exists()
import sys
sys.path.append("../jsondumpable")
from jsondumpable import JSONDumpable

class Repeater(JSONDumpable):
    """
    Repeats task periodically.

    Interface:
    obj-->set_first_call(delay_in_sec)
    obj-->set_delay(seconds=0, minutes=0, hours=0, days=0, weeks=0)
    obj-->set_shell_call(call_str)
    cls-->repeat()
    cls-->load_from_json_file()
    cls-->dump_to_json_file() 
    """

    # Interval between consecutive checks
    sleep_interval = 30      

    # Definitions of time
    chro_minute =   60
    chro_hour   =   60 * chro_minute
    chro_day    =   24 * chro_hour
    chro_week   =    7 * chro_day 

    def __init__(self, name="Unnamed", current_jobs=None):
        super().__init__()
        self.next_call = time.time()   # set first call time to now


    def set_first_call(self, delay_in_sec=0):
        """
        Set time of first call relative to now.
        Not necessary to set before first call. Default delay is 0.

        Kwargs:
        delay_in_sec {float}
        """
        self.next_call = time.time() + delay_in_sec



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



    def set_shell_call(self, call_str):
        """
        Parameters:
        call_str {string} - The shell command to execute
        """
        self.__shell_call_string = call_str



    # Sets next call relative to current time
    def __set_next_call(self):
        self.next_call = time.time() + self.delay_float

 

    @classmethod
    def repeat(cls, still_waiting=True):
        "Start repeater process."
        while True:
            for job in cls.current_jobs:
                if time.time() > job.next_call:
                    job.__set_next_call()   # next call set first to minimize time offset   >
                                            # in case of long-running script                   |
                    p = subprocess.Popen(job.__shell_call_string, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                    just_in = p.stdout.read().decode()  # fetch all outputs
                                                        # note: this will also fetch delayed outputs
                    # display any non-empty output from the called script in a terminal paging (echo "text"|less) window
                    if just_in != '':
                        subprocess.run('gnome-terminal -- sh -c "echo \'' + str(just_in) + '\'|less"', shell=True)                        
            time.sleep(cls.sleep_interval)

    var_str_list = ['next_call', 'delay_dict', '_Repeater__shell_call_string']
    dump_file = 'repfile.json'




    @classmethod
    def load_from_json_file(cls):
        """ Load jobs from a repfile.json """
        with open("repfile.json", 'r') as file:
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
                newrep.__shell_call_string = job['__shell_call_string']


    @classmethod
    def create_json_file(cls):
        #if os.path.exists(os.getcwd() + "/" + cls.dump_file):
        #    print("JSON exists already.")
        #else:
        instance = cls()
        instance.set_shell_call('echo "hello"')
        instance.set_delay(seconds=30)
        print(cls.current_jobs)
        cls.dump_to_json_file()


    @classmethod
    def run_Repeater(cls):
        cls.load_from_json_file()
        cls.repeat()



if __name__ == "__main__":
    #Repeater.run_Repeater()
    Repeater.create_json_file()