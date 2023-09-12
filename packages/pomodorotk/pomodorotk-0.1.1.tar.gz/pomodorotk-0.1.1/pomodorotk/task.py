class Task:
    """A task"""
    def __init__(self, name, expected_pomodoros):
        """Task initialization"""
        self.observers = set()
        self.name = name
        self.expected_pomodoros = expected_pomodoros
        self.remaining_pomodoros = expected_pomodoros
        self.started_pomodoros = 0
        self.started = False

    def add_observer(self, observer):
        """Add an observer to the task"""
        self.observers.add(observer)

    def remove_observer(self, observer):
        """Remove an observer from the task"""
        self.observers.remove(observer)

    def notify_observers(self):
        """Notify all the observers of the task"""
        for observer in self.observers:
            observer(self)

    def add_pomodoro(self):
        """Increment the number of expected pomodoros"""
        self.expected_pomodoros += 1
        self.remaining_pomodoros += 1
        self.notify_observers()

    def remove_pomodoro(self):
        """Decrement the number of expected pomodoros"""
        if self.remaining_pomodoros > 0:
            self.expected_pomodoros -= 1
            self.remaining_pomodoros -= 1
        if self.started_pomodoros > self.expected_pomodoros:
            self.started_pomodoros = self.expected_pomodoros
        self.notify_observers()


    def finish(self):
        """Decrement the number of remaining pomodoros"""
        if self.started and self.remaining_pomodoros:
            self.remaining_pomodoros -= 1
            self.started = False
        self.notify_observers()

    def start(self):
        """Increment the number of started pomodoros"""
        self.started_pomodoros += 1
        self.started = True
        self.notify_observers()

    @property
    def finished(self):
        """Return True if the task is finished"""
        return not self.started and self.remaining_pomodoros <= 0


class TaskQueue:
    """A queue of tasks"""
    def __init__(self):
        self.tasks = []
        self.finished = []

    def add_task(self, task):
        """Add a task to the queue"""
        self.tasks.append(task)

    def all_tasks(self):
        """Return all the tasks in the queue"""
        return self.finished + self.tasks

    def tip(self):
        """Return the first unfinished task in the queue"""
        return self.tasks[0]

    def remove_finished(self):
        """Remove all the finished tasks from the queue"""
        while self.tasks and self.tip().finished:
            self.finished.append(self.tasks.pop(0))

    def remove_all(self):
        """Remove all the tasks from the queue"""
        self.tasks = []
        self.finished = []

    def remove(self, task):
        """Remove a task from the queue"""
        if task in self.tasks:
            self.tasks.remove(task)
        elif task in self.finished:
            self.finished.remove(task)
