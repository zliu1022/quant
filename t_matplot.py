#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
import numpy as np

if __name__ == '__main__':
    xpoints = np.array([1, 2, 6, 8])
    ypoints = np.array([3, 8, 1, 10])
    plt.plot(xpoints, ypoints, 'o')

    ypoints = np.array([3, 8, 1, 10, 5, 7])
    #plt.plot(ypoints, marker = '1')
    plt.plot(ypoints, 'o:r')
    plt.show()

    '''
    '-'	Solid line	
    ':'	Dotted line	
    '--'	Dashed line	
    '-.'	Dashed/dotted line

    'r'	Red
    'g'	Green
    'b'	Blue
    'c'	Cyan
    'm'	Magenta
    'y'	Yellow
    'k'	Black
    'w'	White
    # https://www.w3schools.com/colors/colors_names.asp

    plt.plot(ypoints, marker = 'o', ms = 20)
    plt.plot(ypoints, marker = 'o', ms = 20, mec = 'r', mfc = 'r')
    plt.plot(ypoints, marker = 'o', ms = 20, mec = '#4CAF50', mfc = '#4CAF50')
    ypoints = np.array([3, 8, 1, 10])
    plt.plot(ypoints, 'o:r')

    plt.plot(ypoints, marker = 'o', ms = 20, mec = 'hotpink', mfc = 'hotpink')
    plt.plot(ypoints, linestyle = 'dotted')
    plt.plot(ypoints, linestyle = 'dashed')
    plt.plot(ypoints, linewidth = '20.5')
    '''

    x = np.array([80, 85, 90, 95, 100, 105, 110, 115, 120, 125])
    y = np.array([240, 250, 260, 270, 280, 290, 300, 310, 320, 330])
    plt.plot(x, y)
    font1 = {'family':'serif','color':'blue','size':20}
    font2 = {'family':'serif','color':'darkred','size':15}

    plt.title("Sports Watch Data", fontdict = font1, loc = 'left')
    plt.xlabel("Average Pulse", fontdict = font2)
    plt.ylabel("Calorie Burnage", fontdict = font2)

    plt.grid(color = 'green', linestyle = '--', linewidth = 0.5)

    plt.show()

    x = np.array([0, 1, 2, 3])
    y = np.array([3, 8, 1, 10])

    plt.subplot(2, 3, 1)
    plt.title("SALES")
    plt.plot(x,y)

    x = np.array([0, 1, 2, 3])
    y = np.array([10, 20, 30, 40])

    plt.subplot(2, 3, 2)
    plt.title("INCOME")
    plt.plot(x,y)

    x = np.array([0, 1, 2, 3])
    y = np.array([3, 8, 1, 10])

    plt.subplot(2, 3, 3)
    plt.plot(x,y)

    x = np.array([0, 1, 2, 3])
    y = np.array([10, 20, 30, 40])

    plt.subplot(2, 3, 4)
    plt.plot(x,y)

    x = np.array([0, 1, 2, 3])
    y = np.array([3, 8, 1, 10])

    plt.subplot(2, 3, 5)
    plt.plot(x,y)

    x = np.array([0, 1, 2, 3])
    y = np.array([10, 20, 30, 40])

    plt.subplot(2, 3, 6)
    plt.plot(x,y)

    plt.suptitle("MY SHOP")
    plt.show()

x = np.array([5,7,8,7,2,17,2,9,4,11,12,9,6])
y = np.array([99,86,87,88,111,86,103,87,94,78,77,85,86])
plt.scatter(x, y, color = 'hotpink')

x = np.array([2,2,8,1,15,8,12,9,7,3,11,4,7,14,12])
y = np.array([100,105,84,105,90,99,90,95,94,100,79,112,91,80,85])
plt.scatter(x, y, color = '#88c999')

x = np.array([5,7,8,7,2,17,2,9,4,11,12,9,6])
y = np.array([99,86,87,88,111,86,103,87,94,78,77,85,86])
sizes = np.array([20,50,100,200,500,1000,60,90,10,300,600,800,75])
plt.scatter(x, y, s=sizes, alpha=0.5)
plt.show()

x = np.random.randint(100, size=(100))
y = np.random.randint(100, size=(100))
colors = np.random.randint(100, size=(100))
sizes = 10 * np.random.randint(200, size=(100))
plt.scatter(x, y, c=colors, s=sizes, alpha=0.5, cmap='nipy_spectral')
plt.colorbar()
plt.show()

x = np.array(["A", "B", "C", "D"])
y = np.array([3, 8, 1, 10])
plt.bar(x,y, color='red', width=0.1)
plt.show()

y = np.array([35, 25, 25, 15])
mylabels = ["Apples", "Bananas", "Cherries", "Dates"]
plt.pie(y, labels = mylabels)
plt.legend()
plt.show()
