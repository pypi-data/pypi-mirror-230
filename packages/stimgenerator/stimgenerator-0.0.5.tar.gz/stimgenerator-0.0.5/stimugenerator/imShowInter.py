import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
from matplotlib.widgets import Slider
import h5py

from stimugenerator import visualization
from stimugenerator import dataIO


def getDistance(cropName):
    f = h5py.File(cropName,'r')
    distance = int(f['/distance'][0])
    f.close()
    
    return distance

def getCrop(cropName):
    f = h5py.File(cropName,'r')
    crop = np.array(f['/crop'])
    f.close()
    
    return crop

def setTitle(cropList,imgIndx):

    cropName = cropList[imgIndx].split('/')[-1].strip('_1.hdf5')
    distance = getDistance(cropList[imgIndx])
            
    title = cropName+'_'+str(distance)
    return title

videoPath = "../data/mouse_footage/"
videoName = "20180713_13_1.h5"

movie = dataIO.read_movie_from_h5(videoPath+videoName)

# declaration
global i

# manuelly reset everytime the program crashes -> find out why it crashes/gets slower
reStartIndex = 0
i = reStartIndex

plt.rcParams["figure.figsize"] = [7.50, 7.50]
plt.rcParams["figure.autolayout"] = True

fig, ax = plt.subplots()
# show the i-th frame of the loaded video as the starting frame
img = ax.imshow(visualization.img_real2view(movie[i][...,::-1]))

axes1 = plt.axes([0.41, 0.000001, 0.21, 0.075])
bnext1 = Button(axes1, 'next frame',color="green")

axes2 = plt.axes([0.61, 0.000001, 0.21, 0.075])
bnext2 = Button(axes2, 'sH_w_Obstacles',color="yellow")

axes3 = plt.axes([0.81, 0.000001, 0.21, 0.075])
bnext3 = Button(axes3, 'next',color="red")

axes4 = plt.axes([0.000001, 0.000001, 0.21, 0.075])
bback = Button(axes4, 'back',color="Red")

axes5 = plt.axes([0.000001, 0.91, 0.21, 0.075])
bdelete = Button(axes5, 'trash',color="purple")
# button function
def showNextFrame(val):
    global i 
    i = i+1
   
    ax.imshow(visualization.img_real2view(movie[i][...,::-1]))
    ax.set_title('Frame: '+str(i))
    fig.canvas.draw_idle()

def straightH_withObstacles(val):
    global i 

    # save
    with open('sH_w_Obstacles.txt','a+') as f:
        f.write(horizonCrops[i])
        f.write('\n')
    f.close()
    print("saved: ",horizonCrops[i])

    # show next
    i = i + 1
    print("show next no.:",i)
    
    ax.imshow(visualization.img_real2view(movie[i][...,::-1]))
    title = setTitle(horizonCrops,i)
    ax.set_title(title)

    fig.canvas.draw_idle()

def update(val):
    global i 
    i = i + 1
    ax.imshow(visualization.img_real2view(movie[i][...,::-1]))
    ax.set_title('Frame: '+str(i))
    fig.canvas.draw_idle()
    print(i)

def goback(val):
    global i 
    if i>=1:
        i = i - 1
    else:
        i = reStartIndex
    ax.imshow(visualization.img_real2view(movie[i][...,::-1]))
    ax.set_title('Frame: '+str(i))
    fig.canvas.draw_idle()
    print("show previous no.:",i)

def delete(val):
    global i 
    # save
    with open('absoluteTrashCrops.txt','a+') as f:
        f.write(horizonCrops[i])
        f.write('\n')
    f.close()
    print("saved: ",horizonCrops[i])

    # show next
    i = i + 1
    print("show next no.:",i)
    ax.imshow(visualization.img_real2view(movie[i][...,::-1]))

    ax.set_title('Frame: '+str(i))

    fig.canvas.draw_idle()
    

bnext1.on_clicked(showNextFrame) # show next frame 
bnext2.on_clicked(straightH_withObstacles)
bnext3.on_clicked(update)

bback.on_clicked(goback)
bdelete.on_clicked(delete)
plt.show()
