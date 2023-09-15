import h5py
import numpy as np
import pickle5

def read_movie_from_h5(filename):
    h5f = h5py.File(filename,'r')
    movie_bgr_h5=h5f['movie_bgr_real'][:]
    h5f.close()
    return movie_bgr_h5

def unPickle(filename):
    '''
    to shorten 3 lines into 1 line
    '''
    with open(filename,'rb') as f:
        output = pickle5.load(f)
    f.close()
    return output

def makePickle(filename,data):
    with open(filename,'wb') as f:
        pickle5.dump(data,f)
    f.close()
    