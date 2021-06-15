import os
from tkinter import *
from tkinter import scrolledtext
import re
import datetime
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure
from ctypes import windll

windll.shcore.SetProcessDpiAwareness(1)
print("Device Scaling Obtained")

root = Tk() # label tkinter as root
root.title("APRS Parser with Graphing") # Title on window
root.grid_rowconfigure(0, weight=1) # weight here causes the row to take up more space than necessary
root.columnconfigure(0, weight=1)

frame_main = Frame(root,bg="maroon") # create a frame in root
frame_main.grid(sticky='news') # idk

header = Label(frame_main, text="Press Ctrl-v to paste raw APRS data below and then hit the parse button", font=('Helvetica', '14'), bg = 'maroon', fg = 'gold')
header.grid(row=0,column=0,padx=5,pady=5,sticky='nw')

textArea = scrolledtext.ScrolledText(frame_main, wrap = WORD, width = 180, height =10, font = ("Helvetica", 8))
textArea.grid(row=1, column=0, padx=5, pady=5)

readText = Button(frame_main, text = "Parse Text Above", height = 1, width = 20, font=('Helvetica', '12'), command = lambda: writeFile())
readText.grid(row=2, column=0, sticky = 'nw', pady = 2, padx = 5)

frame_setAxes = Frame(frame_main, bg = "maroon")
frame_setAxes.grid(row=4, column = 0, sticky = 'nw')

selectXValue = IntVar()
selectXValue.set(2)
buttonLabels = ["Minutes","Packet Number","Altitude (ft)","Altitude (m)","Pressure (Pa)","Temperature (C)","Temperature (F)","3D Position"]
Label(frame_setAxes, text= "SET X-AXIS", bg="maroon", fg = "gold", font=('Helvetica', '14', 'bold')).grid(row=0, column=0, padx = 5, sticky = 'nw')

for currentLabel in buttonLabels:
    buttonIndex = buttonLabels.index(currentLabel)+1
    Radiobutton(frame_setAxes, text=currentLabel, font=('Helvetica', '14'), selectcolor = "black", bg="maroon", fg="lightgray", variable=selectXValue, value=buttonIndex).grid(row=buttonIndex,column=0, padx = 5, sticky = 'nw')

selectYValue = IntVar()
selectYValue.set(1)
Label(frame_setAxes, text= "SET Y-AXIS", fg = "gold", bg="maroon", font=('Helvetica', '14', 'bold')).grid(row=0, column=1, padx = 5, sticky = 'nw')
for currentLabel in buttonLabels:
    buttonIndex = buttonLabels.index(currentLabel)+1
    Radiobutton(frame_setAxes, text=currentLabel, font=('Helvetica', '14'), selectcolor = "black", bg="maroon", fg="lightgray", variable=selectYValue, value=buttonIndex).grid(row=buttonIndex,column=1, padx = 5, sticky = 'nw')

mapRefresh = Button(frame_setAxes, text = "Refresh Graph", height = 1, width = 20, font=('Helvetica', '12'), command = lambda: refreshGraph())
mapRefresh.grid(row=10, column=0, padx = 5, pady = 2, sticky="W")

csvHeader = "Date, Time, Latitude, Longitude, Altitude (ft), Altitude (m), packetNumber, Temperature (C), Temperature (F), Pressure (Pa), Flight Minutes \n"

allEverything = [[]]
for y in range(0,10):
    allEverything.append([])

def writeFile():
    global folder
    global allEverything
    global ind
    global plotLabel
    global callsignNumber
    ind = 0

    today = datetime.datetime.now()
    folder = "APRS Data " + today.strftime("%m-%d-%y")

    if os.path.exists(folder) == False:
        os.makedirs(folder)
    fileTime = today.strftime("%H-%M")
    fileName = 'rawDataRunAt' + fileTime + '.txt'
    file = os.path.join(folder,fileName)

    writeRawFile = open(file,'w')
    writeRawFile.write(textArea.get('1.0', 'end-1c'))
    writeRawFile.close()

    readRawFile = open(file, 'r')

    flightMinsAdd = 0
    onlyOnce = True

    #for x in file:
    for x in readRawFile:
        try:
            data = x
            currentTime = re.split('-|:| ', data)
            year = currentTime[0]
            month = currentTime[1]
            day = currentTime[2]
            hour = currentTime[3]
            minute = currentTime[4]
            second = currentTime[5]

            if(ind==0):
                callsignNumber = data[data.find('T: ') + 3 : data.find('>')]
                plotLabel = callsignNumber + " " + month + "/" + day + "/" + year
                startHour = int(hour)
                startMinute = int(minute)
                startSecond = int(second)
                startDay = int(day)
                destination = callsignNumber + "_ParsedAt_" + fileTime + ".csv"
                parsedDest = os.path.join(folder,destination)
                parsedFile = open(parsedDest, 'w')
                parsedFile.write(csvHeader)

            date = data[:data.find(' ')]
            junk = data[:data.find('!')]
            junk = junk.replace(',',' ')
            data = data[data.find('!')+1:]

            lat = data[:data.find('N')]
            lat = str(int(float(lat)*100)/10000)
            print(lat)

            lon = data[data.find('/')+1 : data.find('E')]
            lon = str(int(float(lon)*100)/10000)
            print(lon)

            alt = data[data.find('=')+1 : data.find(',')]
            alt = str(int(alt))
            altInt = int(alt)
            altMInt = altInt * 0.3048
            print(altMInt)

            packetNumberString = data[data.find('StrTrk,') + 7 :]
            packetNumber = int(packetNumberString[: packetNumberString.find(',')])

            temperature = int(data[data.find('V,') + 2 : data.find('C,')])
            temperatureF = temperature*9.0/5.0 + 32.0

            try:
                pressure = int(data[data.find('C,') + 2 : data.find('Pa,')])
            except:
                pressure = 0

            if(int(day)!=startDay and onlyOnce==True):
                startDay = int(day)
                startHour = int(hour)
                startMinute = int(minute)
                startSecond = int(second)
                flightMinsAdd = flightMinutesInt
                onlyOnce = False

            flightMinutesInt = int(((int(hour)-startHour)*60)+(int(minute)-startMinute)+ ((int(second)-startSecond)/60)) + flightMinsAdd

            if(ind < 2):
                allEverything[0].append(flightMinutesInt)
                allEverything[1].append(packetNumber)
                allEverything[2].append(altInt)
                allEverything[3].append(altMInt)
                allEverything[4].append(int(pressure))
                allEverything[5].append(int(temperature))
                allEverything[6].append(temperatureF)
                allEverything[7].append(float(lat))
                allEverything[8].append(float(lon))
                ind +=1
            else:
                for y in range(ind):
                    if(allEverything[2][y] == altInt):
                        break
                    if(y==ind-1):
                        allEverything[0].append(flightMinutesInt)
                        allEverything[1].append(packetNumber)
                        allEverything[2].append(altInt)
                        allEverything[3].append(altMInt)
                        allEverything[4].append(int(pressure))
                        allEverything[5].append(int(temperature))
                        allEverything[6].append(temperatureF)
                        allEverything[7].append(float(lat))
                        allEverything[8].append(float(lon))

                        ind+=1

                        csvString = "C: " + date + "," + hour + ":" + minute + ":" + second + "," + lat + "," + lon + "," + alt + "," + str(altMInt) + "," + str(packetNumber) + "," + str(temperature) + "," + str(temperatureF) + "," + str(pressure) + "," + str(flightMinutesInt) + ",,," + junk + "\n"
                        parsedFile.write(csvString)

        except:
            #print("BAD PACKET!")
            pass

    header = Label(frame_main, text="Data Parsed and saved to: " + destination, font=('Helvetica', '14'), bg = 'maroon', fg = 'gold')
    header.grid(row=3,column=0,padx=5,pady=5,sticky='nw')

def refreshGraph():
    try:
        fig.destroy()
        myFig.destroy()
    except:
        pass

    AxesLabels = ["Minutes Since Launch", "Packet Number", "Altitude (ft)", "Altitude (m)", "Pressure (Pa)", "Temperature (C)", "Temperature (F)"]

    xAxis = allEverything[selectXValue.get()-1]
    xLabel = AxesLabels[selectXValue.get()-1]
    yAxis = allEverything[selectYValue.get()-1]
    yLabel = AxesLabels[selectYValue.get()-1]

    fig = Figure(figsize=(7, 4), dpi=100)
    myFig = fig.add_subplot(111)
    myFig.set_title(plotLabel)
    myFig.set_xlabel(xLabel)
    myFig.set_ylabel(yLabel)
    myFig.grid(color='gray', linestyle='-', linewidth=0.5)
    myFig.plot(xAxis, yAxis, color='r', linestyle='None', marker='o', markersize = 3.0)

    canvas = FigureCanvasTkAgg(fig, frame_setAxes)  # A tk.DrawingArea.
    canvas.draw()
    canvas.get_tk_widget().grid(row = 0, column = 2, rowspan=100, padx = 5, pady = 5)

    imageFileName = callsignNumber + " " +  xLabel + " vs " + yLabel + ".png"
    imagePath = os.path.join(folder, imageFileName)
    buttonLabel = "Save Plot as:  " + imageFileName
    saveButton = Button(frame_setAxes, text = buttonLabel , height = 1, width = 70, font=('Helvetica', '12'), command = lambda: savePlot(xLabel,yLabel,xAxis,yAxis,imagePath))
    saveButton.grid(row = 101, column = 2, padx = 5, pady = 5, sticky = 'nw')

def savePlot(xLabel, yLabel, xAxis, yAxis, imagePath):
    fig = Figure(figsize=(12, 7), dpi=100)
    myFig = fig.add_subplot(111)
    myFig.set_title(plotLabel)
    myFig.set_xlabel(xLabel)
    myFig.set_ylabel(yLabel)
    myFig.grid(color='gray', linestyle='-', linewidth=0.5)
    myFig.plot(xAxis, yAxis, color='r', linestyle='None', marker='o', markersize = 3.0)

    fig.savefig(imagePath)

root.mainloop()