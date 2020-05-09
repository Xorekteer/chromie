import json

class JSONDumpable():
    """
    Superclass for JSON Dumpable objects.
    Keeps a list of all instances and some useful 
    functions for serialization.

    Interface:
    cls.var_str_list {list of strings}  
        -- Set of variables to be dumped
            -- SUBCLASS VARIABLE: Set in subclass before running
            -- no default, error if not set
    cls.dump_file 
        -- Filename of file to be dumpled
            -- SUBCLASS VARIABLE: Set in subclass before running
    cls.dump_to_json_file()
        -- Dump file
    """
    
    # Initialize list w/ current jobs
    current_jobs = []
    
    # Class variable list of strings
    var_str_list=None

    # Dump file name
    dump_file = "classdump.json"

    def __init__(self, current_jobs=None):
        """ Default init."""
        self.storage_dict = list()
        
        self.__class__.current_jobs.append(self)  #add new object to list of objects  
        # Check passing by reference
        if id(self) != id(self.__class__.current_jobs[-1]):
            raise Exception("Scheduler instance passed to list of Scheduler instances by copying instead of referencing.")



    # Create dumpale JSON dict for a single object
    def __create_json_dict(self):
        self.storage_dict = dict()
        for var_str in self.__class__.var_str_list:     # ignore this error, it's intended
            exec("self.storage_dict['" + var_str + "'] = self." + var_str)



    @classmethod
    def __get_dumpable_list(cls):
        cls.cls_jsonlist = list()    # list to hold all objects
        for job in cls.current_jobs:    
            job.__create_json_dict()                    # create dict for object variables
            cls.cls_jsonlist.append(job.storage_dict)   # append job to list
        return cls.cls_jsonlist



    @classmethod
    def dump_to_json_file(cls):
        """ Write all current Repeater jobs to a repfile.json """
        with open(cls.dump_file, "w") as file:
            json.dump(cls.__get_dumpable_list(), file, indent=2)



def test():
    inst = JSONDumpable()
    inst.var1 = 15
    inst.var2 = 'foo'
    JSONDumpable.var_str_list = ['var1', 'var2']
    return JSONDumpable._JSONDumpable__get_dumpable_list()



if __name__ == "__main__":
    test()