import nidaqmx
import tkinter as tk
from tkinter import ttk

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure


class voltageContinuousInput(tk.Frame):

    def __init__(self, master):
        # tk.Frame.__init__(self, master)
        super().__init__(master)

        #Configure root tk class
        self.master = master
        self.master.title("Voltage - Continuous Input")
        self.master.iconbitmap("Voltage - Continuous Input.ico")
        self.master.geometry("1100x600")

        self.create_widgets()
        self.pack()
        self.run = False

    def create_widgets(self):
        #The main frame is made up of three subframes
        self.channelSettingsFrame = channelSettings(self, title ="Channel Settings")
        self.channelSettingsFrame.grid(row=0, column=1, sticky="ew", pady=(20,0), padx=(20,20), ipady=10)

        self.inputSettingsFrame = inputSettings(self, title="Input Settings")
        self.inputSettingsFrame.grid(row=1, column=1, pady=(20,0), padx=(20,20), ipady=10)

        self.graphDataFrame = graphData(self)
        self.graphDataFrame.grid(row=0, rowspan=2, column=2, pady=(20,0), ipady=10)


    def startTask(self):
        #Prevent user from starting task a second time
        self.inputSettingsFrame.startButton['state'] = 'disabled'

        #Shared flag to alert task if it should stop
        self.continueRunning = True

        #Get task settings from the user
        physicalChannel = self.channelSettingsFrame.physicalChannelEntry.get()
        maxVoltage = int(self.channelSettingsFrame.maxVoltageEntry.get())
        minVoltage = int(self.channelSettingsFrame.minVoltageEntry.get())
        sampleRate = int(self.inputSettingsFrame.sampleRateEntry.get())
        self.numberOfSamples = int(self.inputSettingsFrame.numberOfSamplesEntry.get()) #Have to share number of samples with runTask

        #Create and start task
        self.task = nidaqmx.Task()
        self.task.ai_channels.add_ai_voltage_chan(physicalChannel, min_val=minVoltage, max_val=maxVoltage)
        self.task.timing.cfg_samp_clk_timing(sampleRate,sample_mode=nidaqmx.constants.AcquisitionType.CONTINUOUS,samps_per_chan=self.numberOfSamples)
        self.task.start()

        #spin off call to check 
        self.master.after(10, self.runTask)

    def runTask(self):
        #Check if task needs to update the graph
        samplesAvailable = self.task._in_stream.avail_samp_per_chan
        if(samplesAvailable >= self.numberOfSamples):
            # vals = self.task.read(self.numberOfSamples)
            vals = self.task.read(samplesAvailable)
            self.graphDataFrame.ax.cla()
            self.graphDataFrame.ax.set_title("Acquired Data")
            self.graphDataFrame.ax.plot(vals)
            self.graphDataFrame.graph.draw()

        #check if the task should sleep or stop
        if(self.continueRunning):
            self.master.after(10, self.runTask)
        else:
            self.task.stop()
            self.task.close()
            self.inputSettingsFrame.startButton['state'] = 'enabled'

    def stopTask(self):
        #call back for the "stop task" button
        self.continueRunning = False

class channelSettings(tk.LabelFrame):

    def __init__(self, parent, title):
        # tk.LabelFrame.__init__(self, parent, text=title, labelanchor='n')
        super().__init__(parent, text=title, labelanchor='n')
        self.parent = parent
        self.grid_columnconfigure(0, weight=1)
        self.xPadding = (30,30)
        self.create_widgets()

    def create_widgets(self):

        self.physicalChannelLabel = ttk.Label(self, text="Physical Channel")
        self.physicalChannelLabel.grid(row=0,sticky='w', padx=self.xPadding, pady=(10,0))

        self.physicalChannelEntry = ttk.Entry(self)
        self.physicalChannelEntry.insert(0, "FieldSensor/ai1")
        self.physicalChannelEntry.grid(row=1, sticky="ew", padx=self.xPadding)

        self.maxVoltageLabel = ttk.Label(self, text="Max Voltage")
        self.maxVoltageLabel.grid(row=2,sticky='w', padx=self.xPadding, pady=(10,0))
        
        self.maxVoltageEntry = ttk.Entry(self)
        self.maxVoltageEntry.insert(0, "10")
        self.maxVoltageEntry.grid(row=3, sticky="ew", padx=self.xPadding)

        self.minVoltageLabel = ttk.Label(self, text="Min Voltage")
        self.minVoltageLabel.grid(row=4,  sticky='w', padx=self.xPadding,pady=(10,0))

        self.minVoltageEntry = ttk.Entry(self)
        self.minVoltageEntry.insert(0, "-10")
        self.minVoltageEntry.grid(row=5, sticky="ew", padx=self.xPadding,pady=(0,10))

class inputSettings(tk.LabelFrame):

    def __init__(self, parent, title):
        # tk.LabelFrame.__init__(self, parent, text=title, labelanchor='n')
        super().__init__(parent, text=title, labelanchor='n')
        self.parent = parent
        self.xPadding = (30,30)
        self.create_widgets()

    def create_widgets(self):
        self.sampleRateLabel = ttk.Label(self, text="Sample Rate")
        self.sampleRateLabel.grid(row=0, column=0, columnspan=2, sticky='w', padx=self.xPadding, pady=(10,0))

        self.sampleRateEntry = ttk.Entry(self)
        self.sampleRateEntry.insert(0, "1000")
        self.sampleRateEntry.grid(row=1, column=0, columnspan=2, sticky='ew', padx=self.xPadding)

        self.numberOfSamplesLabel = ttk.Label(self, text="Number of Samples")
        self.numberOfSamplesLabel.grid(row=2, column=0, columnspan=2, sticky='w', padx=self.xPadding, pady=(10,0))

        self.numberOfSamplesEntry = ttk.Entry(self)
        self.numberOfSamplesEntry.insert(0, "100")
        self.numberOfSamplesEntry.grid(row=3, column=0, columnspan=2, sticky='ew', padx=self.xPadding)

        self.startButton = ttk.Button(self, text="Start Task", command=self.parent.startTask)
        self.startButton.grid(row=4, column=0, sticky='w', padx=self.xPadding, pady=(10,0))

        self.stopButton = ttk.Button(self, text="Stop Task", command=self.parent.stopTask)
        self.stopButton.grid(row=4, column=1, sticky='e', padx=self.xPadding, pady=(10,0))

class graphData(tk.Frame):

    def __init__(self, parent):
        # tk.Frame.__init__(self, parent)
        super().__init__(parent)
        self.create_widgets()

    def create_widgets(self):
        self.graphTitle = ttk.Label(self, text="Voltage Input")
        self.fig = Figure(figsize=(7,5), dpi=100)
        self.ax = self.fig.add_subplot(1,1,1)
        self.ax.grid()
        self.ax.set_title("Acquired Data")
        self.graph = FigureCanvasTkAgg(self.fig, self)
        self.graph.draw()
        self.toolbar = NavigationToolbar2Tk(self.graph, self)
        self.toolbar.update()
        self.graph.get_tk_widget().pack()


if __name__ == '__main__':
    #Creates the tk class and primary application "voltageContinuousInput"
    # root = tk.Tk()
    app = voltageContinuousInput(tk.Tk())

    #start the application
    app.mainloop()