
import numpy as np

def get_test_resp(neuron,neuron2mvResp):
    '''
    neuron: string, neuron_id
    neuron2mvResp: dict, neuronid->18450 datapoint responses
    
    return a ndarray with shape 3,5,150 for 1st/2nd/3rd repetition of tests' 1st/2nd/3rd/4th/5th movie seq
    '''
    mv_resp = neuron2mvResp[neuron]
    test_resp = np.zeros((3,5,150))
    
    test_resp[0,:,:] = np.reshape(neuron2mvResp[neuron][0*150:5*150],(5,150))
    test_resp[1,:,:] = np.reshape(neuron2mvResp[neuron][59*150:64*150],(5,150))
    test_resp[2,:,:] = np.reshape(neuron2mvResp[neuron][-5*150:],(5,150))
    
    return test_resp

def cell_scene_resp_dict(neuron_ids,mvResp,neuron2seqT):
    '''
    neuron_ids: a list of strings, each string is a neuron_id
    mvResp: a dictionary, nid(string)->mv_response(np.array, (123*150,))
    neuron2SeqT: a dictionary, nid(string)->(123,)scene_id +10002000300040005000 as test sequence
    
    return: a (#cell,108,150), how each cell (WITHOUT n_id info) responds to snippets 0 ~107
    '''
    numCells =len(neuron_ids)
    output = np.zeros((len(neuron_ids),108,150))
    for i in range(numCells):
        nid = neuron_ids[i] # string
        cell_resp = mvResp[nid] # np array (150*123,)
        seqT=neuron2seqT[nid] # np array (123,)
        for scene in range(108): # train_scene 0~107
            scene_idx = np.where(seqT==scene)[0][0] # when each scene was play
            output[i,scene,:] = mvResp[nid][scene_idx*150:scene_idx*150+150]
    # print(output.shape)
    return output
