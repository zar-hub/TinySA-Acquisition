import pyautogui
import win32gui, time
import keyboard
import tinysa
import numpy as np
import matplotlib
from matplotlib import pyplot as plt

arinst_hwld = 0
winlist, toplists = [], []
buttons = {}

dt = 0.01
wait_scan = 0.5
wait_before_scan = .7

def enum_cb(hwnd, results):
    winlist.append((hwnd, win32gui.GetWindowText(hwnd)))
    
class InterfaceButton():
    def __init__(self, x=0, y=0, text = "", hwld = 0):
        global arinst_hwld
        self.x = x
        self.y = y
        self.text = text
        self.hwld = arinst_hwld
    def click(self):
        # if not foreground, bring to foreground
        old_hwld = win32gui.GetForegroundWindow()
        if old_hwld != self.hwld:
            win32gui.SetForegroundWindow(self.hwld)
            time.sleep(dt)
        pyautogui.click(self.x, self.y)
        # return to the old window
        if old_hwld != self.hwld:
            win32gui.SetForegroundWindow(old_hwld)
            time.sleep(dt)

def type_freq(freq):
    # convert freq to string
    freq = "%d" % freq
    for s in freq:
        buttons[s].click()

def set_gen_freq(freq):
    buttons["freq"].click()
    type_freq(freq)
    buttons["entr"].click()

def measure_freq(freq):
    print(f"gen freq: {int(freq)}")
    set_gen_freq(freq/1e6)
    print(f"center freq: {int(freq)}")
    tsa.set_center(freq)
    data = np.zeros(3)
    time.sleep(wait_before_scan)
    for i in range(3):
        data[i] = tsa.marker_value()
        time.sleep(wait_scan)
    print(data)
    return data

def init_arinst():
    global arinst_hwld
    global buttons
    # init the arinst window
    win32gui.EnumWindows(enum_cb, toplists)
    for hwld, title in winlist:
        if "arinst" in title.lower():
            arinst_hwld = hwld
            break
        
    if(arinst_hwld == 0):
        print("Arinst not found...")
        raise OSError("device not found")

    # resize the arinst window to standard size
    win32gui.MoveWindow(arinst_hwld, -10, 0, 960, 540, True)

    # load the buttons from arinstInterface.txt
    
    with open("arinstInterface.txt", "r") as f:
        print("Loading buttons")
        for line in f:
            x, y, text = line.strip().split(",")
            buttons[text]  = InterfaceButton(int(float(x)), int(float(y)), text)
    return arinst_hwld
            
def init_tsa():
    # get the tinysa object
    tsa = tinysa.TinySA()
    return tsa

def get_trace(tsa):
    tsa.send_command("trace 1 value\r")
    data = tsa.fetch_data()
    x = []
    for line in data.split('\n'):
        if line:
            d = line.strip().split(' ')
            x.append([float(d[-2]), float(d[-1])])
    return np.array(x)


def get_samples(tsa, sample_freq, wait_before_scan = None, wait_scan = None):
    if wait_before_scan is None:
        wait_before_scan = globals()["wait_before_scan"]
    if wait_scan is None:
        wait_scan = globals()["wait_scan"]
    
    data = -90 * np.ones((len(sample_freq), 2))
    
    # generate the plot
    fig = plt.figure(figsize=(5, 3))
    ax = fig.subplots(2, 1)
    ax[1].set_xlabel("Frequency (GHz)")
    ax[1].set_ylabel("Amplitude (dBm)")
    ax[1].set_title("Peak and Noise")
    ax[1].legend(["Peak", "Noise"])
    ax[1].set_ylim(-100, 0)
    ax[1].set_xlim(sample_freq[0]/1e9, sample_freq[-1]/1e9)
    
    plt.show(block=False)
    
    for i, freq in enumerate(sample_freq):
        print(f"Measuring frequency: {freq/1e9} GHz")
        
        # set the generator frequency
        set_gen_freq(freq/1e6)
        tsa.set_center(freq)
       
        time.sleep(wait_before_scan) 
        for j in range(3):
            print(f"--- Measuring peak and noise: {j}")
            trace = get_trace(tsa)   
            peak = tsa.marker_value(1)
            noise = tsa.marker_value(2)
            
            ax[0].clear()
            ax[0].plot(trace[:,0], trace[:,1])
            # draw the peak and noise lines
            ax[0].axhline(y=peak, color='g')
            ax[0].axhline(y=noise, color='r')
            
            plt.draw()
            plt.pause(wait_scan)
            
        peak = tsa.marker_value(1)
        noise = tsa.marker_value(2)
        
        # update the values of the peak and noise
        ax[1].clear()
        data[i, 0] = peak
        data[i, 1] = noise
        ax[1].plot(sample_freq/1e9, data[:,0], 'g-')
        ax[1].plot(sample_freq/1e9, data[:,1], 'r-')
        ax[1].set_ylim(-100, 0)
        plt.draw()
    
    return data    

if __name__ == "__main__":
    # Start a hook in a new thread, which calls sys.exit() when 'Esc' is pressed
    init_arinst()
    tsa = init_tsa()
    
    # check if all the buttons are working
    # for button in buttons.values():
    #     print(button.text)
    #     button.click()
    #     time.sleep(.1)
    
    # get the tinysa object
    
    # parameters
    filename = "LF_LNA_BOX_R19.txt"
    cols = "Frequency (GHz),Peak (mV),Noise (mV),SigPeak (mV),SigNoise (mV)"
    sample_freq = np.linspace(.25e9, 6e9, 100)
    # sample_freq = np.linspace(5e9, 6e9, 10)
    dt = 0.001
    n_repeats = 6
    wait_before_scan = .8
    wait_scan = .4
    tsa.set_span(25e6)
    
    print("Starting the measurement")
    timeEstimate = len(sample_freq) * (wait_before_scan + n_repeats * wait_scan) / 60
    print(f"Time estimate: {timeEstimate} minutes")
    
    # peaks and noise
    data = np.zeros((len(sample_freq), 2))
    sig = np.zeros((len(sample_freq), 2))
    
    # generate the plot
    fig = plt.figure(figsize=(5, 3))
    fig.canvas.manager.window.setGeometry(650, 0, 500, 1000)
    ax = fig.subplots(2, 1)
    
    peakLine, = ax[1].plot(sample_freq/1e9, data[:,0], 'g-')
    # noiseLine, = ax[1].plot(sample_freq/1e9, data[:,1], 'r-')
    plt.show(block=False)
    
    # start timer
    start = time.time()    

    for i, freq in enumerate(sample_freq):
        # print(f"Measuring frequency: {freq/1e9} GHz")
        # set the generator frequency
        set_gen_freq(freq/1e6)
        time.sleep(.1)
        tsa.set_center(freq)
        tsa.send_command(f"marker 1 {freq/1e6}M\r")
       
        time.sleep(wait_before_scan) 
        
        peak = []
        noise = []
        
        for j in range(n_repeats):
           
            # the trace is in dBm :( 
            # trace = get_trace(tsa)   
            
            trace = tsa.data()
            mid = len(trace) // 2
            
            peak.append(trace[mid-20:mid+5].max())
            noise.append(tsa.marker_value(2))
            # print(f"Peak: {peak}, Noise: {noise}")
            
            ax[0].clear()
            # ax[0].plot(trace[:,0], trace[:,1])
            ax[0].plot(np.arange(len(trace)), trace)
            # draw the peak and noise lines
            ax[0].axhline(y=peak[j], color='g')
            ax[0].axhline(y=noise[j], color='r')
            ax[0].axvline(x=mid - 20, color='y')
            ax[0].axvline(x=mid + 5, color='y')
            
            plt.draw()
            plt.pause(wait_scan)
        
        # compute the mean and the standard deviation
        sig_peak = np.std(peak, ddof=1)
        sig_noise = np.std(noise, ddof=1)    
        peak = np.mean(peak)
        noise = np.mean(noise)
        
        print(f"Peak: {peak}, Noise: {noise}")
        print(f"Peak std: {sig_peak}, Noise std: {sig_noise}")
        
        data[i, 0] = peak
        data[i, 1] = noise
        sig[i, 0] = sig_peak
        sig[i, 1] = sig_noise
        
        # update the values of the peak and noise
        ax[1].clear()
        ax[1].errorbar(sample_freq/1e9, data[:,0] * 1e3,
                       yerr = sig[:,0]* 1e3, fmt = 'g-')
        ax[1].errorbar(sample_freq/1e9, data[:,1] * 1e3, 
                   yerr = sig[:,1]* 1e3, fmt = 'r-')
        plt.draw()
        
        # print(f"time elapsed: {(time.time() - start) / 60} | {timeEstimate}")

    # save the data with a name  
    np.savetxt(filename, np.column_stack((sample_freq * 1e-9, data * 1e3, sig * 1e3)), 
               delimiter=',', 
               header=cols,
               fmt="%.5e")
    
    # wait for the user to close the plot
    plt.show()
    
        