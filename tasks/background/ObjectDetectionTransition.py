import asyncio
import json
import logging
from interface.Transition import Transition, auto_register_unregister
import dataplane_pb2 as dataplane

logger = logging.getLogger(__name__)

class ObjectDetectionTransition(Transition):
    def __init__(self, args, target, data):
        super().__init__(args)
        self.target = target
        self.data = data

    @auto_register_unregister
    async def run(self):
        # Non-blocking startup delay
        await asyncio.sleep(4)
        while not self._stop_event.is_set():
            logger.debug(f"Task {self.task_id}: Running object detection transition...")
            result = await self.data.get_compute_result("openscout-object")
            if len(result) == 0:
                logger.debug(f"Task {self.task_id}: No result from compute engine")
                continue
            
            # assume always use the first compute module result
            detections = json.loads(result[0])
            if len(detections) == 0:
                logger.debug(f"Task {self.task_id}: No result from compute engine bc of the GeoFence")
                continue
            
            logger.info(f"Task {self.task_id}: Detected payload: {detections=}")
            for detection in detections:
                class_attribute = detection.get('class')
                if class_attribute == self.target:
                    logger.info(f"Task {self.task_id}: Target matched! {class_attribute}")
                    await self._trigger_event("object_detection")
                    return
                
            await asyncio.sleep(0.1)  # Yield to event loop