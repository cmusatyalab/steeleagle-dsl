# class DetectTask(PatrolTask):
#     model: str
#     lower_bound: tuple[int, int, int]
#     upper_bound: tuple[int, int, int]
#     transition_config: dict
#     task_id: str
#     trans_active: object
#     trans_active_lock: object
#     trigger_event_queue: object

#     async def execute(self, context):
#         await ConfigureDetection(
#             model=self.model,
#             lower=self.lower_bound,
#             upper=self.upper_bound
#         ).execute(context)

#         await super().execute(context)  # Run patrol sequence

#         # After first waypoint
#         await ClearDetectionBuffer().execute(context)
#         await DetectTransitionSetup(
#             transition_attributes=self.transition_config,
#             task_id=self.task_id,
#             trans_active=self.trans_active,
#             trans_active_lock=self.trans_active_lock,
#             trigger_event_queue=self.trigger_event_queue
#         ).execute(context)