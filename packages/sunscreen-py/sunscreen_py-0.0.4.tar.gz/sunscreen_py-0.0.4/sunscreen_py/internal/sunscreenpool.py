from multiprocessing.pool import ThreadPool

GLOBAL_POOL = None

class SunscreenPool:
    threadpool = None
    def __init__(self, threads):
        self.threadpool = ThreadPool(threads)

    @classmethod
    def initialize(_cls, threads):
        global GLOBAL_POOL
        if GLOBAL_POOL is None:
            GLOBAL_POOL = SunscreenPool(threads)
    
    @classmethod
    def get_instance(_cls):
        global GLOBAL_POOL
        class Temp:
            def map(self, func, list):
                return [func(i) for i in list]
            
        return Temp()#GLOBAL_POOL.threadpool
    
        
    