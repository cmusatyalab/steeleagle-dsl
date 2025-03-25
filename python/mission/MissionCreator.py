import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
from interfaces.Task import TaskArguments, TaskType


class MissionCreator:

    # transition
    @staticmethod
    def start_transit(triggered_event):
        logger.info("start_transit\n")
        return "patrol_hiviz"
    @staticmethod
    def patrol_hiviz_transit(triggered_event):
        if (triggered_event == "hsv_detection"):
            return "tracking"
        if (triggered_event == "done"):
            return "patrol_blue"
    @staticmethod
    def tracking_transit(triggered_event):
        if (triggered_event == "done"):
            return "patrol_hiviz"
    @staticmethod
    def patrol_blue_transit(triggered_event):
        if (triggered_event == "hsv_detection"):
            return "tracking"
        if (triggered_event == "done"):
            return "patrol_hiviz"
    @staticmethod
    def default_transit(triggered_event):
        logger.info(f"MissionController: no matched up transition, triggered event {triggered_event}\n", triggered_event)
    #task
    @staticmethod
    def define_mission(transitMap, task_arg_map):
        #define transition
        logger.info("MissionController: define the transitMap\n")
        transitMap["start"] = MissionCreator.start_transit
        transitMap["patrol_hiviz"]= MissionCreator.patrol_hiviz_transit
        transitMap["tracking"]= MissionCreator.tracking_transit
        transitMap["patrol_blue"]= MissionCreator.patrol_blue_transit
        transitMap["default"]= MissionCreator.default_transit
        # define task
        logger.info("MissionController: define the tasks\n")
        # TASKpatrol_hiviz
        task_attr_patrol_hiviz = {}
        task_attr_patrol_hiviz["gimbal_pitch"] = "-30.0"
        task_attr_patrol_hiviz["drone_rotation"] = "0.0"
        task_attr_patrol_hiviz["sample_rate"] = "2"
        task_attr_patrol_hiviz["hover_delay"] = "0"
        task_attr_patrol_hiviz["coords"] = "[{'lng': -79.9504949, 'lat': 40.4156604, 'alt': 7.0},{'lng': -79.9504814, 'lat': 40.415542, 'alt': 7.0},{'lng': -79.9498149, 'lat': 40.4155384, 'alt': 7.0},{'lng': -79.9498672, 'lat': 40.4158794, 'alt': 7.0},{'lng': -79.9505143, 'lat': 40.4158539, 'alt': 7.0},{'lng': -79.9504949, 'lat': 40.4156604, 'alt': 7.0}]"
        task_attr_patrol_hiviz["model"] = "visdrone"
        task_attr_patrol_hiviz["upper_bound"] = [50, 255, 255]
        task_attr_patrol_hiviz["lower_bound"] = [30, 100, 100]
        transition_attr_patrol_hiviz = {}
        transition_attr_patrol_hiviz["hsv_detection"] = "car"
        task_arg_map["patrol_hiviz"] = TaskArguments(TaskType.Detect, transition_attr_patrol_hiviz, task_attr_patrol_hiviz)
        #TASKtracking
        task_attr_tracking = {}
        task_attr_tracking["model"] = "visdrone"
        task_attr_tracking["class"] = "car"
        task_attr_tracking["gimbal_pitch"] = "-30.0"
        task_attr_tracking["upper_bound"] = [30, 100, 100]
        task_attr_tracking["lower_bound"] = [50, 255, 255]
        transition_attr_tracking = {}
        task_arg_map["tracking"] = TaskArguments(TaskType.Track, transition_attr_tracking, task_attr_tracking)
        # TASKpatrol_blue
        task_attr_patrol_blue = {}
        task_attr_patrol_blue["gimbal_pitch"] = "-30.0"
        task_attr_patrol_blue["drone_rotation"] = "0.0"
        task_attr_patrol_blue["sample_rate"] = "2"
        task_attr_patrol_blue["hover_delay"] = "0"
        task_attr_patrol_blue["coords"] = "[{'lng': -79.9504949, 'lat': 40.4156604, 'alt': 7.0},{'lng': -79.9504814, 'lat': 40.415542, 'alt': 7.0},{'lng': -79.9498149, 'lat': 40.4155384, 'alt': 7.0},{'lng': -79.9498672, 'lat': 40.4158794, 'alt': 7.0},{'lng': -79.9505143, 'lat': 40.4158539, 'alt': 7.0},{'lng': -79.9504949, 'lat': 40.4156604, 'alt': 7.0}]"
        task_attr_patrol_blue["model"] = "visdrone"
        task_attr_patrol_blue["upper_bound"] = [215, 255, 255]
        task_attr_patrol_blue["lower_bound"] = [195, 100, 100]
        transition_attr_patrol_blue = {}
        transition_attr_patrol_blue["hsv_detection"] = "car"
        task_arg_map["patrol_blue"] = TaskArguments(TaskType.Detect, transition_attr_patrol_blue, task_attr_patrol_blue)
