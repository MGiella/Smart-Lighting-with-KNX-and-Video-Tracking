import multiprocessing
from multiprocessing import JoinableQueue

from pygame_interface import PygameInterface
from ultralytics import YOLO

"""VideoTracker is a Singleton that manages the object detection"""


class VideoTracker:
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self):
        self._results = JoinableQueue()
        self._jobs = JoinableQueue()
        self._model = YOLO('yolov8n.pt')
        self._started = False
        self._create_processes(5)
        self._frame_passed = 0

    def is_started(self):
        return self._started

    def start(self):
        self._started = True

    def stop(self):
        self._started = False


    def _process_results(self):
        """detect a person box and put it in results if the tracking was started"""
        while True:
            results_box = []
            if not self._jobs.empty():
                frame = self._jobs.get()
                model_results = self._model.predict(frame, True, verbose=False)
                for result in model_results:
                    for box in result.boxes.data.tolist():
                        x, y, w, h, score, class_id = box
                        # class_id 0 is the person id, score is the accuracy of the prediction
                        if class_id == 0 and score >= 0.5:
                            results_box.append((x, y, w, h))
                self._results.put(results_box)

    def _create_processes(self, concurrency):
        for _ in range(concurrency):
            p = multiprocessing.Process(target=self._process_results)
            p.daemon = True
            p.start()

    def object_detection(self, frame, interface: PygameInterface):
        """identifies the people that enters the frame, creates a box and
        put the center in the list """
        # The detection is made one time each 3 frame, has to be 3 otherwise doesn't work
        self._frame_passed += 1
        if self._frame_passed == 2:
            self._frame_passed = 0
            self._jobs.put(frame)
            centers = []
            if not self._results.empty():
                points = self._results.get()
                for point in points:
                    # Each person detected is represented as a point that is the center of a box
                    x, y, w, h = point
                    center = ((x + w / 2), (y + h / 2))
                    centers.append(center)
                    interface.create_box(x, y, w, h)
            return centers
        else:
            return []
