import sys
import subprocess
import platform
import time
try:
    import tkinter as tk
except ImportError:
    sys.exit("Tkinter not found.")

class ShutdownApplet:
    def __init__(self):
        self.window = tk.Tk()
        self.label = tk.Label(master=self.window, text="00:00:00")
        self.seconds = 5 * 60
        self.next_decr = 0
        self.shutting_down = False
        self.timer = None
        self.bg = self.window.cget("background")
        
        self.window.title("DownShutter")
        self.window.resizable(width=False, height=False)
        self.window.call('wm', 'attributes', '.', '-topmost', '1')
        #window.iconbitmap(default='resources/')

        self.label = tk.Label(master=self.window, text=self.seconds_to_str(self.seconds))
        self.label.config(font=("Courier bold", 44))
        self.label.pack()

        self.label.bind("<MouseWheel>", self.on_scroll)
        self.label.bind("<Button-1>", self.on_click)
        self.label.bind("<Return>", self.on_click)

    def run(self) -> None:
        self.window.mainloop()
        if self.shutting_down:
            self.cancel_system_call()

    def find_OS(self) -> str:
        return platform.system()

    def seconds_to_str(self, seconds:  int, colons: bool = True) -> str:
        secs = seconds % 60
        seconds -= secs
        mins = seconds % (60*60)
        seconds -= mins
        hours = seconds % (24*60*60)
        seconds -= hours
        if colons:
            s = "{h:02d}:{m:02d}:{s:02d}".format(h=int(hours/(60*60)), m=int(mins/60), s=secs)
        else:
            s = "{h:02d} {m:02d} {s:02d}".format(h=int(hours/(60*60)), m=int(mins/60), s=secs)
        return s

    def min_max_seconds(self, s: int) -> int:
        if s < 60:
                s = 60
        day = (24*60*60) - 1
        if s > day:
            s = day
        return s

    def on_scroll(self, event: tk.Event) -> None:
        if not self.shutting_down:
            if event.delta > 0:
                self.seconds += 60
            elif event.delta < 0:
                self.seconds -= 60

            self.seconds = self.min_max_seconds(self.seconds)
            self.label.config(text=self.seconds_to_str(self.seconds))
        pass

    def on_click(self, event) -> None:
        if self.shutting_down:
            self.cancel_system_call()
        elif not self.shutting_down:
            self.timer = self.window.after(100, self.on_timer)
            self.next_decr = time.time()
            self.do_system_call()
        pass

    def on_timer(self) -> None:
        self.timer = self.window.after(100, self.on_timer)
        if time.time() > self.next_decr + 1:
            self.next_decr += 1
            self.seconds -= 1
            colons = bool(self.seconds % 2) or self.seconds < 3*60
            self.label.config(text=self.seconds_to_str(self.seconds, colons))
            
            if self.seconds < 5*60 and self.seconds > 3*60:
                self.label.config(fg='red')
            if self.seconds < 3*60:
                if self.seconds % 2:
                    self.label.config(fg='red', bg=self.bg)
                else:
                    self.label.config(fg='black', bg='red')
        pass

    def do_system_call(self) -> None:
        self.shutting_down = True
        os = self.find_OS()
        if os == "Windows":
            subprocess.run("shutdown -s -t {}".format(self.seconds))
        pass

    def cancel_system_call(self) -> None:
        self.shutting_down = False
        try:
            self.label.config(fg='black', bg=self.bg)
            self.window.after_cancel(self.timer)
        except:
            # window already closed
            pass
        os = self.find_OS()
        if os == "Windows":
            subprocess.run("shutdown -a")
        pass



def main():
    ShutdownApplet().run()

if __name__ == "__main__":
    main()