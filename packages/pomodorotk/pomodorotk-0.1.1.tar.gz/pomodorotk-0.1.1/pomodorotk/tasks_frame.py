import tkinter as tk
from tkinter import ttk

from .resources import get_resource
from .task import TaskQueue

BUTTON_FONT = (None, 20)
VISIBLE_POMODOROS = 8
TOMATO_SIZE = 32


class TasksFrame:
    """Frame that contains all the tasks"""

    tomato = None
    tomato_progress = None
    tomato_dis = None

    def __init__(self, parent_widget):
        self.task_queue = TaskQueue()
        self.frame = ttk.Frame(parent_widget)

        if self.tomato is None:
            self.load_images()

    @classmethod
    def load_images(cls):
        """Load the images used by the tasks"""
        with get_resource("tomato.png") as tomato:
            cls.tomato = tk.PhotoImage(file=tomato)
        with get_resource("tomato_progress.png") as tomato_progress:
            cls.tomato_progress = tk.PhotoImage(file=tomato_progress)
        with get_resource("tomato_dis.png") as tomato_dis:
            cls.tomato_dis = tk.PhotoImage(file=tomato_dis)

    def pack(self, *args, **kwargs):
        """Pack the frame"""
        self.frame.pack(*args, **kwargs)

    def start_pomodoro(self):
        """Start the first task"""
        if self.task_queue.tasks:
            self.task_queue.tip().start()

    def finish_pomodoro(self):
        """Finish the first task"""
        if self.task_queue.tasks:
            self.task_queue.tip().finish()
            self.task_queue.remove_finished()

    def add_task(self, task, task_frame_parent):
        """Add a task to the queue and update the frame"""
        self.task_queue.add_task(task)
        self._create_task_frame(task)

    def remove_task(self, task, task_frame):
        """Remove a task from the queue and update the frame"""
        self.task_queue.remove(task)
        task_frame.destroy()

    def add_pomodoro(self, task, task_frame):
        """Add a pomodoro to a task and update the frame"""
        if task.expected_pomodoros < VISIBLE_POMODOROS:
            task.add_pomodoro()

    def remove_pomodoro(self, task, task_frame):
        """Remove a pomodoro from a task and update the frame"""
        if task.expected_pomodoros > 1:
            task.remove_pomodoro()

    def _update_task_canvas(self, task, canvas):
        """Update tomatoes displayed for a task"""
        canvas.delete("all")
        active_pomodoro = task.started_pomodoros - 1
        for i in range(task.expected_pomodoros):
            offset = i // 4 * TOMATO_SIZE
            if i < active_pomodoro or (i == active_pomodoro and not task.started):
                image = self.tomato
            elif i == active_pomodoro:
                image = self.tomato_progress
            else:
                image = self.tomato_dis
            canvas.create_image(i * TOMATO_SIZE + offset, 0, image=image, anchor=tk.NW)

    def _create_task_frame(self, task):
        task_frame = ttk.Frame(self.frame)
        buttons_box = ttk.Frame(task_frame, width=64 * 3)

        delete = ttk.Button(
            buttons_box,
            text="X",
            command=lambda: self.remove_task(task, task_frame),
            style="big.TButton",
            width=1,
        )
        add_pomodoro = ttk.Button(
            buttons_box,
            text="+",
            command=lambda: self.add_pomodoro(task, task_frame),
            style="big.TButton",
            width=1,
        )
        remove_pomodoro = ttk.Button(
            buttons_box,
            text="-",
            command=lambda: self.remove_pomodoro(task, task_frame),
            style="big.TButton",
            width=1,
        )
        tomato_area = tk.Canvas(
            task_frame,
            width=TOMATO_SIZE * (VISIBLE_POMODOROS + VISIBLE_POMODOROS // 4),
            height=TOMATO_SIZE,
            highlightthickness=0,
            background="white",
        )
        self._update_task_canvas(task, tomato_area)

        task_name_frame = ttk.Frame(task_frame)
        task_name = ttk.Label(task_name_frame, text=task.name, background="white")
        task_name.pack(side=tk.LEFT, padx=5, pady=5)
        task_name_frame.pack(side=tk.TOP, fill="x", expand=True)
        tomato_area.pack(side=tk.LEFT)
        remove_pomodoro.pack(side=tk.LEFT)
        add_pomodoro.pack(side=tk.LEFT)
        delete.pack(side=tk.LEFT)

        buttons_box.pack(side=tk.TOP)

        task.add_observer(lambda task: self._update_task_canvas(task, tomato_area))

        task_frame.pack(side=tk.TOP, fill="both", expand=True)
