import numpy as np
from skimage.measure import block_reduce
from PIL import Image
from skimage.transform import resize
from stimugenerator import visualization

# to better visulaize image, use gamma correction to transfer image real to image view
def img_real2view(img):
    gamma_correction=lambda x:np.power(x,1.0/2.2)
    img_shape=img.shape
    # gray image
    if np.size(img_shape)==2:
        # uint8
        if np.max(img)>1:
            temp_view=np.zeros_like(img,dtype=np.float32)
            temp_view=np.float32(img)/255.0 # float32, 1.0
            temp_view=gamma_correction(temp_view)
            temp_view2=np.zeros_like(img,dtype=np.uint8)
            temp_view2=np.uint8(temp_view*255)
            return temp_view2
        # float
        if np.max(img)<2:
            return gamma_correction(img)
            
    # color image
    if np.size(img_shape)==3:
        # uint8, BGR
        if np.max(img)>1:
            temp_view=np.zeros_like(img,dtype=np.float32)
            temp_view=np.float32(img[...,::-1])/255.0 # gb,1.0
            temp_view[...,-1]=gamma_correction(temp_view[...,-1])
            temp_view[...,1]=gamma_correction(temp_view[...,1])
            temp_view2=np.zeros_like(img,dtype=np.uint8)
            temp_view2=np.uint8(temp_view[...,::-1]*255) # bgr,255
            return temp_view2
        # float, RGB
        if np.max(img)<2:
            return gamma_correction(img)

def downSample(img):
    # used in the Gui atm
    # input img is a 2D_matrix
    # 72x64->18x16

    output = np.zeros((18,16))
    output = block_reduce(img,block_size=(4,4),func = np.mean)

    return output

def resize_downSample(img):
    # input img is a 2D_matrix3
    # 72x64->18x16

    output = resize(img,(18,16))
    return output

def makeGif(snippet,filename):
    # snippet 1,2,120 18 16
    output = np.zeros((120,18,16,3))
    
    output[:30,:,:,:]=128
    output[-30:,:,:,:]=128
    
    output[30:-30,:,:,0] = snippet[1,30:-30,:,:]
    output[30:-30,:,:,1] = snippet[0,30:-30,:,:]
    
    grays1 = [Image.fromarray(np.uint8(frame)) for frame in output[:30]]
    
    images = [Image.fromarray(img_real2view(np.uint8(frame)[...,::-1])) for frame in output[30:90]]
    grays2 = [Image.fromarray(np.uint8(frame)) for frame in output[-30:]]
    toGif = grays1+images+grays2
    
    toGif[0].save(filename+'.gif', save_all=True, append_images=toGif[1:], loop=1, duration=34,optimize=False)