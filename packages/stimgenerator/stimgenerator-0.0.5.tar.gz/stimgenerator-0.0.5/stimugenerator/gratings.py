from PIL import Image
import numpy as np
import os

def make_stimulus_gif(path,stimulus):
    # make gif (original resolution)
    with Image.open(stimulus [0]) as img:
        img.save(path+"30f_34dur_start_15fgray.gif", save_all=True, append_images=[Image.open(file) for file in stimulus[1:]],
                 duration = 34, loop=1, optimize=False)
        del img

def test():
    root_path= "/gpfs01/euler/User/ydeng/data/moving_gratings/"
    gray_img_path = "/gpfs01/euler/User/ydeng/data/moving_gratings/0/gratings000/0.png"
    
    gray_screen = [gray_img_path for i in range(90)] # 90frame gray
    # pics = os.listdir("/gpfs01/euler/User/ydeng/data/moving_gratings/0/gratings000")
    directions = [str(i)+"/" for i in range(4)]
    other_configs = ['gratings000','gratings001','gratings002','gratings003','gratings004',
                     'gratings010','gratings011','gratings012','gratings013','gratings014',
                     'gratings020','gratings021','gratings022','gratings023','gratings024']
    pngs = [str(i)+'.png' for i in range(60)]
    pngs_r = pngs[::-1]
    for direction in directions:
        for config in other_configs:
            path = ''
            path = root_path+direction+config+'/'
            
            for i in range(60):
                if not os.path.isfile(path+str(i)+'.png'):
                    print("BUG")
            
            # under the last leave folder
            grating_pics = [path+each for each in pngs[0::2]]
            grating_pics_r = [path+each for each in pngs_r[0::2]]
            
            # assemble section
            stimulus = []
            # 15 frame gray screen 
            stimulus = gray_screen[:15]+ grating_pics + grating_pics_r+gray_screen[15:]
            
            # make gif (original resolution)
            # make_stimulus_gif(path,stimulus)
            
            # save downsampled -> .npy
            downsample_stimulus = np.zeros((len(stimulus),2,18,16))
            for i in range(len(stimulus)):
                original_image = Image.open(stimulus[i])
                resize_BOX = original_image.resize((16, 18), Image.BOX)
                resize_BOX_np = np.array(resize_BOX)
                toSave = resize_BOX_np[:,:,0]
                downsample_stimulus[i,:,:,:]=toSave
            downsample_stimulus = downsample_stimulus.reshape(len(stimulus)//50,50,2,18,16).transpose(0,2,1,3,4)
            
            np.save(path+config+".npy",downsample_stimulus)