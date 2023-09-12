import time
import tkinter as tk
from tkinter import ttk

from pydub import AudioSegment, playback

from .resources import get_resource
from .task import Task
from .tasks_frame import VISIBLE_POMODOROS, TasksFrame


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


# Update the clock every UPDATE_TIME_MS milliseconds
UPDATE_TIME_MS = 250


def main():
    test_mode = False

    # Create a window and main frame using ttk themed widgets
    root = tk.Tk()
    ttk.Style().theme_use("clam")
    root.title("Pomodoro Timer")
    root_frame = ttk.Frame(root).pack()

    # Set background color to white
    root.configure(bg="white", padx=10, pady=10)

    # Initialize style
    style = ttk.Style()
    # Create style used by default for all Frames
    style.configure("TFrame", background="white")
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

    with get_resource("alarm.mp3") as mp3file:
        alarm_sound = AudioSegment.from_mp3(mp3file)

    def alarm(tasks_frame):
        """Play the alarm sound"""
        tasks_frame.finish_pomodoro()
        playback.play(alarm_sound)

    def start_pomodoro(seconds, tasks_frame):
        """Start a pomodoro"""
        tasks_frame.start_pomodoro()
        start_updating_clock(seconds)

    def start_break(seconds, tasks_frame):
        """Start a break"""
        tasks_frame.finish_pomodoro()
        start_updating_clock(seconds)

    def stop_pomodoro(tasks_frame):
        """Stop the pomodoro"""
        tasks_frame.finish_pomodoro()
        timer.stop()

    # Pack the labels
    state_label.pack(padx=10, pady=10)
    time_label.pack(padx=10, pady=10)

    # Default values for new tasks
    default_pomodoros = tk.IntVar()
    default_pomodoros.set(4)
    default_name = tk.StringVar()
    default_name.set("Task")

    # Create a bar to create tasks
    create_task_bar = ttk.Frame(root_frame)
    task_name_label = ttk.Label(create_task_bar, text="Task name:", background="white")
    task_name = ttk.Entry(create_task_bar, width=20, textvariable=default_name)
    task_pomodoros = ttk.Spinbox(
        create_task_bar,
        from_=1,
        to=VISIBLE_POMODOROS,
        width=2,
        textvariable=default_pomodoros,
    )
    add_task = ttk.Button(
        create_task_bar,
        text="Add task",
        command=lambda: tasks_frame.add_task(
            Task(task_name.get(), int(task_pomodoros.get())),
            task_frame_parent=tasks_frame.frame,
        ),
    )

    # Create a timer object
    timer = Timer(lambda: alarm(tasks_frame), update_clock)

    # Create buttons to start and stop the timer
    button_bar = ttk.Frame(root_frame)
    start = ttk.Button(
        button_bar,
        text="Start",
        width=10,
        command=lambda: start_pomodoro(25 * 60, tasks_frame),
    )
    break_ = ttk.Button(
        button_bar,
        text="Break",
        width=10,
        command=lambda: start_break(5 * 60, tasks_frame),
    )
    long_break = ttk.Button(
        button_bar,
        text="Long Break",
        width=10,
        command=lambda: start_break(15 * 60, tasks_frame),
    )
    if test_mode:
        test = ttk.Button(
            button_bar,
            text="Test",
            width=10,
            command=lambda: start_pomodoro(2, tasks_frame),
        )
    stop = ttk.Button(
        button_bar, text="Stop", width=10, command=lambda: stop_pomodoro(tasks_frame)
    )

    # Pack the buttons
    start.pack(side=tk.LEFT, padx=5)
    break_.pack(side=tk.LEFT, padx=5)
    long_break.pack(side=tk.LEFT, padx=5)
    stop.pack(side=tk.LEFT, padx=5)
    if test_mode:
        test.pack(side=tk.LEFT, padx=5)
    button_bar.pack(side=tk.TOP)

    # Pomodoro frame
    tasks_frame = TasksFrame(root_frame)
    tasks_frame.pack(side=tk.TOP, fill="both", expand=True, padx=10, pady=10)

    # Pack the create tasks bar
    task_name_label.pack(side=tk.LEFT, padx=5)
    task_name.pack(side=tk.LEFT, padx=5)
    task_pomodoros.pack(side=tk.LEFT, padx=5)
    add_task.pack(side=tk.LEFT, padx=5)
    create_task_bar.pack(side=tk.TOP, padx=5)

    # Run the main loop
    tk.mainloop()
