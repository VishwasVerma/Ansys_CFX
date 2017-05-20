# python3/user/bin

import numpy as np
import os


def getdata(filename):
    data = []
    with open(filename) as originalfile:
        data = [line.split() for line in originalfile]
        #print(data)
    data = np.array(data)
    return (data)

def scale_cordinate(data,scaling_factor):
    # data is supposed to be contaning x, y , z cordinates
    # airfoil geometry is supposed to be on xy plane
    data_length = int(np.size(data)/3)
    newdata = np.zeros((data_length,3))
    for i in range(data_length):
       line = data[i]
       newdata[i][0] = float(line[0]) * scaling_factor
       newdata[i][1] = float(line[1]) * scaling_factor
       newdata[i][2] = float(line[2])
    return (newdata)

def writetext(scaled_data, newfile, z_location, profile_number = 0):
    file = open(newfile,'a')
    file.write("# profile %i \n" %profile_number )
    for i,d in enumerate(scaled_data):
        line = scaled_data[i]
        file.write(str(z_location) + " " + str(line[0]) + " " + str(line[1]) + '\n')
    file.write("\n")
    file.close()

def translate_geometry(data, x_shift, y_shift, z_shift = 0):
    data_length = int(np.size(data)/3)
    newdata = np.zeros((data_length,3))
    for i in range(data_length):
       line = data[i]
       newdata[i][0] = float(line[0]) + x_shift
       newdata[i][1] = float(line[1]) + y_shift
       newdata[i][2] = float(line[2])# since this module is airfoil specific no need of spon variation z_location
    return (newdata)

def findsurfaces(data):
    data_length = int(np.size(data)/3)
    top_surface = []
    bottom_surface = []
    counter = 0
    for i in range(data_length):
        line = data[i]
        top_surface.append(line)
        if float(line[0]) == 1 :
            break
        counter += 1
    for i in range(counter,data_length):
        line = data[i]
        bottom_surface.append(line)
    top_surface = np.array(top_surface)
    bottom_surface = np.array(bottom_surface)
    return(top_surface,bottom_surface)

def findcentriod(data):
    # assumes that the geometry is 2D
    x_cord = 0
    y_cord = 0
    data_length = int(np.size(data)/3)
    for i in range(data_length):
        line = data[i]
        x_cord += float(line[0])
        y_cord += float(line[1])
    x_cord = x_cord/data_length
    y_cord = y_cord/data_length
    return(x_cord,y_cord)

def designmodular_compatable_file(data, newfile, group_number):
    file = open(newfile, 'a')
    file.write( "#Group" + " " + "Number" + " " + "X_coord" +" " + "Y_coord" + " " + "Z_coord" + '\n')
    for i,d in enumerate(data):
        line = data[i]
        file.write (str(group_number) + " " + str(i) + " " + str(line[0]) + " " + str(line[1]) + " " + str(line[2]) + '\n')
    file.close()

def make_ansys_file(datafile):
    datafile = "eppler_396.txt"
    data = getdata(datafile)
    top_surface, bottom_surface = findsurfaces(data)
    x_top_cord, y_top_cord = findcentriod(top_surface)
    x_bottom_cord, y_bottom_cord = findcentriod(bottom_surface)
    top_surface_translate_to_top = translate_geometry(top_surface, 0, 0.5)
    bottom_surface_translate_to_bottom = translate_geometry(bottom_surface, 0, -0.5)
    new_top_surface = translate_geometry(top_surface_translate_to_top, -1*x_top_cord, 0)#-1*y_top_cord)
    new_bottom_surface = translate_geometry(bottom_surface_translate_to_bottom, -1*x_bottom_cord, -1*y_bottom_cord)
    scaled_new_top_surface = scale_cordinate(new_top_surface, 2.0) # scaling factor = 1.5
    scaled_new_bottom_surface = scale_cordinate(new_bottom_surface, 2.)
    back_new_top_surface = translate_geometry(scaled_new_top_surface, x_top_cord, 0)#y_top_cord)
    back_new_bottom_surface = translate_geometry(scaled_new_bottom_surface, x_bottom_cord, y_bottom_cord)

    top_surface_file = "top_surface.txt"
    bottom_surface_file = "bottom_surface.txt"
    try:
        os.remove(top_surface_file)
    except OSError:
        pass

    designmodular_compatable_file(back_new_top_surface, top_surface_file, group_number = 1)
    #writetext(back_new_top_surface, top_surface_file)
    try:
        os.remove(bottom_surface_file)
    except OSError:
        pass

    writetext(back_new_bottom_surface,bottom_surface_file)

def theta2rad(theta):
    radian = (theta * np.pi )/ 180
    return (radian)

def rotate_geometry(data, theta): # theta is in degree
    radian_angle = theta2rad(theta)
    data_length = int(np.size(data)/3)
    newdata = np.zeros((data_length,3))
    for i in range(data_length):
        line = data[i]
        newdata[i][0] = (float(line[0])* np.cos(radian_angle)) + (float(line[1]) * np.sin(radian_angle))
        newdata[i][1] = (-1*float(line[0]) * np.sin(radian_angle))+ (float(line[1]) * np.cos(radian_angle))
        newdata[i][2] = float(line[2])
    return (newdata)

def make_cfx_file(datafile, inputfile, newfile):
    try :
        os.remove(newfile)
    except OSError:
        pass
    cordinate_data = getdata(datafile)
    input_data = getdata(inputfile) # input file contains data for z_location and theta rotation
    chord = 3.75 # chord of the balde is 3.75cm
    x_centriod, y_centriod = findcentriod(cordinate_data)
    scaled_data = scale_cordinate(cordinate_data, chord)
    translated_data = translate_geometry(cordinate_data, -1*x_centriod, -1*y_centriod)
    input_length = int(np.size(input_data)/2)
    for i in range(input_length):
        line = input_data[i]
        rotated_data = rotate_geometry(translated_data, float(line[1]))
        back_to_same_origin_data = translate_geometry(rotated_data, x_centriod, y_centriod)
        writetext(back_to_same_origin_data, newfile, float(line[0]), i+1)

make_cfx_file("eppler_396.txt", "input_file.txt", "profile.curve")
