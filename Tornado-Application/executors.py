from concurrent import futures

# executors.py will create our threadpools, and this can be shared around different python files
# which will not re-create 10 threadpools when we call it.
# we can a handful of executors for running synchronous tasks

# Create a 10 thread threadpool that we can use to call any synchronous/blocking functions
executor = futures.ThreadPoolExecutor(10)