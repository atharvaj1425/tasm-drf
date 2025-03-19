import heapq
from datetime import datetime

class TaskPriorityQueue:
    # Priority weights (higher number = higher priority)
    PRIORITY_WEIGHTS = {
        'high': 3,
        'medium': 2,
        'low': 1
    }
    
    def __init__(self):
        self.queue = []
        self.entry_finder = {}  # mapping of task id to entry
        self.counter = 0  # unique sequence count for same priority tasks
    
    def add_task(self, task):
        """Add a new task or update an existing task's priority"""
        task_id = task.id
        # Calculate priority score based on:
        # 1. Task priority (high/medium/low)
        # 2. Creation time (older tasks get higher priority)
        priority_score = self._calculate_priority_score(task)
        
        # If task already exists, remove it first
        if task_id in self.entry_finder:
            self._remove_task(task_id)
        
        # Add new entry
        entry = [priority_score, self.counter, task]
        self.entry_finder[task_id] = entry
        heapq.heappush(self.queue, entry)
        self.counter += 1
    
    def _calculate_priority_score(self, task):
        """Calculate priority score (lower score = higher priority in heap)"""
        # Invert priority weight for min-heap (we want highest priority at top)
        priority_factor = -1 * self.PRIORITY_WEIGHTS.get(task.priority, 2)
        
        # Convert timestamp to seconds since epoch for comparison
        time_factor = task.created_at.timestamp()
        
        # We want older tasks to have higher priority
        # So we negate the timestamp to get older tasks higher in the queue
        time_factor *= -1
        
        # Return composite score
        return (priority_factor, time_factor)
    
    def _remove_task(self, task_id):
        """Mark an existing task as removed"""
        entry = self.entry_finder.pop(task_id)
        entry[2] = None  # Mark as removed (avoid memory leak)
    
    def pop_task(self):
        """Remove and return the highest priority task"""
        while self.queue:
            priority, count, task = heapq.heappop(self.queue)
            if task is not None:  # Check if task wasn't removed earlier
                del self.entry_finder[task.id]
                return task
        return None  # Queue is empty
    
    def get_all_sorted(self):
        """Return all tasks in priority order without removing them"""
        result = []
        # Create a copy of the queue for iteration
        temp_queue = self.queue.copy()
        
        while temp_queue:
            priority, count, task = heapq.heappop(temp_queue)
            if task is not None:
                result.append(task)
        
        return result