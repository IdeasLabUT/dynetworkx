import time

def timer(method):
    def timed(*args, **kwargs):
        start = time.time()
        result = method(*args, **kwargs)
        end = time.time()
        print('{}: {:.4f} sec'.format(method.__name__, end - start))
        return result
    return timed
