import time
import tkinter as tk
from importlib import resources
from tkinter import ttk

from pydub import AudioSegment, playback


class Timer:
    """
    A timer that can run for a given number of seconds and call a function
    """

    def __init__(self, alarm_fn, update_clock_fn):
        """Initialize the timer"""
        self.started = None
        self.seconds = None
        self.alarm_fn = alarm_fn
        self.update_clock_fn = update_clock_fn

    def update(self):
        """
        Update the timer and call the alarm function if the timer has expired
        """
        if self.started:
            elapsed = int(time.time()) - self.started
            remaining = max(self.seconds - elapsed, 0)
            self.update_clock_fn(remaining)
            if remaining <= 0:
                self.alarm_fn()
                self.stop()

    def start(self, seconds):
        """Start the timer for the given number of seconds"""
        self.seconds = seconds
        self.started = time.time()

    def stop(self):
        """Stop the timer"""
        self.started = None


def main():
    # Update the clock every UPDATE_TIME_MS milliseconds
    UPDATE_TIME_MS = 250

    # Create a window and main frame using ttk themed widgets
    root = tk.Tk()
    ttk.Style().theme_use("clam")
    root.title("Pomodoro Timer")
    root_frame = ttk.Frame(root).pack()

    # Set background color to white
    root.configure(bg="white", padx=10, pady=10)
    root.resizable(False, False)

    # Create a state label widget
    state_label = tk.Label(
        root_frame, text="Timer", bg="white", fg="black", font="none 12 bold"
    )
    # Create a label widget
    time_label = tk.Label(
        root_frame, text="00:00", bg="white", fg="black", font="none 30 bold"
    )


    def start_updating_clock(seconds):
        """Start the timer and begin updating the clock"""
        timer.start(seconds)
        update_clock(seconds)


    def update_clock(remainding):
        """Update the clock with the remaining time and reschedule the update"""
        # Convert remaining seconds to mm:ss format
        minutes = int(remainding / 60)
        seconds = int(remainding % 60)
        time_string = "{:02d}:{:02d}".format(minutes, seconds)
        # Update the time label
        time_label.configure(text=time_string)
        root.after(UPDATE_TIME_MS, timer.update)


    mp3resource = resources.files("pomodorotk").joinpath("alarm.mp3")
    with resources.as_file(mp3resource) as mp3file:
        alarm_sound = AudioSegment.from_mp3(mp3file)


    def alarm():
        """Play the alarm sound"""
        playback.play(alarm_sound)


    # Create a timer object
    timer = Timer(alarm, update_clock)

    # Pack the labels
    state_label.pack(padx=10, pady=10)
    time_label.pack(padx=10, pady=10)


    # Create buttons to start and stop the timer
    start = ttk.Button(
        root_frame, text="Start", width=10, command=lambda: start_updating_clock(25 * 60)
    )
    break_ = ttk.Button(
        root_frame, text="Break", width=10, command=lambda: start_updating_clock(5 * 60)
    )
    long_break = ttk.Button(
        root_frame,
        text="Long Break",
        width=10,
        command=lambda: start_updating_clock(15 * 60),
    )
    test = ttk.Button(
        root_frame,
        text="Test",
        width=10,
        command=lambda: start_updating_clock(2),
    )
    stop = ttk.Button(root_frame, text="Stop", width=10, command=timer.stop)

    # Pack the buttons
    start.pack(side=tk.LEFT, padx=5)
    break_.pack(side=tk.LEFT, padx=5)
    long_break.pack(side=tk.LEFT, padx=5)
    stop.pack(side=tk.LEFT, padx=5)
    test.pack(side=tk.LEFT, padx=5)

    # Run the main loop
    tk.mainloop()
