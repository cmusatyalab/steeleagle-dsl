package org.droneDSL.compile.codeGen.concrete;

import kala.collection.immutable.ImmutableMap;
import kala.collection.mutable.MutableMap;
import kala.text.StringSlice;
import kala.tuple.Tuple;
import kala.tuple.Tuple2;
import org.aya.intellij.GenericNode;
import org.droneDSL.compile.parser.BotPsiElementTypes;
import org.jetbrains.annotations.NotNull;

public interface Parse {
  enum TaskKind {
    Detect,
    Track,
    Avoid,
    Test,
  }

  class AttributeMap {
    MutableMap<StringSlice, GenericNode<? extends GenericNode<?>>> content = MutableMap.create();
    TaskKind kind;

    public GenericNode<? extends GenericNode<?>> get(String name) {
      return content.get(StringSlice.of(name));
    }
  }


  static ImmutableMap<String, Task>  createTaskMap(GenericNode<?> node){
    return ImmutableMap.from(node.child(BotPsiElementTypes.TASK).
        childrenOfType(BotPsiElementTypes.TASK_DECL).map(Parse::createTask));
  }

  @NotNull
  static Tuple2<String, Task> createTask(GenericNode<? extends GenericNode<?>> task) {
    var attrMap = createMap(task);
    var taskID = task.child(BotPsiElementTypes.TASK_NAME).tokenText().toString();

    return switch (attrMap.kind) {
      case Detect -> {
        var gimbal_pitch = attrMap.get("gimbal_pitch").child(BotPsiElementTypes.NUMBER).tokenText();
        var drone_rotation = attrMap.get("drone_rotation").child(BotPsiElementTypes.NUMBER).tokenText();
        var sample_rate = attrMap.get("sample_rate").child(BotPsiElementTypes.NUMBER).tokenText();
        var hover_delay = attrMap.get("hover_delay").child(BotPsiElementTypes.NUMBER).tokenText();
        var model = attrMap.get("model").child(BotPsiElementTypes.NAME).tokenText();
        // waypoints
        var wayPoints = attrMap.get("way_points").child(BotPsiElementTypes.ANGLE_BRACKED).child(BotPsiElementTypes.NAME).tokenText().toString();
        // HSV
        var nums = attrMap.get("hsv_upper_bound").child(BotPsiElementTypes.PAREN).child(BotPsiElementTypes.TUPLE).childrenOfType(BotPsiElementTypes.NUMBER).map(t -> t.tokenText().toInt()).toImmutableSeq();
        var hsv_upper_bound  = new DetectTask.HSV(nums.get(0), nums.get(1), nums.get(2));
        nums = attrMap.get("hsv_lower_bound").child(BotPsiElementTypes.PAREN).child(BotPsiElementTypes.TUPLE).childrenOfType(BotPsiElementTypes.NUMBER).map(t -> t.tokenText().toInt()).toImmutableSeq();
        var hsv_lower_bound  = new DetectTask.HSV(nums.get(0), nums.get(1), nums.get(2));
        // construct new task
        var detectTask = new DetectTask(
            taskID,
            wayPoints,
            gimbal_pitch.toFloat(),
            drone_rotation.toFloat(),
            sample_rate.toInt(),
            hover_delay.toInt(),
            model.toString(),
            hsv_lower_bound,
            hsv_upper_bound
        );
        yield Tuple.of(taskID, detectTask);
      }

      case Track -> {
        // HSV
        var nums = attrMap.get("hsv_upper_bound").child(BotPsiElementTypes.PAREN).child(BotPsiElementTypes.TUPLE).childrenOfType(BotPsiElementTypes.NUMBER).map(t -> t.tokenText().toInt()).toImmutableSeq();
        var hsv_upper_bound  = new TrackTask.HSV(nums.get(0), nums.get(1), nums.get(2));
        nums = attrMap.get("hsv_lower_bound").child(BotPsiElementTypes.PAREN).child(BotPsiElementTypes.TUPLE).childrenOfType(BotPsiElementTypes.NUMBER).map(t -> t.tokenText().toInt()).toImmutableSeq();
        var hsv_lower_bound  = new TrackTask.HSV(nums.get(0), nums.get(1), nums.get(2));
        var gimbal_pitch = attrMap.get("gimbal_pitch").child(BotPsiElementTypes.NUMBER).tokenText();
        var model = attrMap.get("model").child(BotPsiElementTypes.NAME).tokenText();
        var target_class = attrMap.get("class").child(BotPsiElementTypes.NAME).tokenText();
        var altitude = attrMap.get("altitude").child(BotPsiElementTypes.NUMBER).tokenText();
        var descent_speed = attrMap.get("descent_speed").child(BotPsiElementTypes.NUMBER).tokenText();
        var orbit_speed = attrMap.get("orbit_speed").child(BotPsiElementTypes.NUMBER).tokenText();
        var follow_speed = attrMap.get("follow_speed").child(BotPsiElementTypes.NUMBER).tokenText();
        var yaw_speed = attrMap.get("yaw_speed").child(BotPsiElementTypes.NUMBER).tokenText();

        // construct new task
        var trackTask = new TrackTask(
            taskID,
            gimbal_pitch.toFloat(),
            target_class.toString(),
            model.toString(),
            hsv_lower_bound,
            hsv_upper_bound,
            altitude.toFloat(),
            descent_speed.toFloat(),
            orbit_speed.toFloat(),
            follow_speed.toFloat(),
            yaw_speed.toFloat()
        );
        yield Tuple.of(taskID, trackTask);
      }

      case Avoid -> {
        var speed = attrMap.get("speed").child(BotPsiElementTypes.NUMBER).tokenText();
        var model = attrMap.get("model").child(BotPsiElementTypes.NAME).tokenText();
        // waypoints
        var wayPoints = attrMap.get("way_points").child(BotPsiElementTypes.ANGLE_BRACKED).child(BotPsiElementTypes.NAME).tokenText().toString();
        // construct new task
        var avoidTask = new AvoidTask(
            taskID,
            wayPoints,
            speed.toFloat(),
            model.toString()
        );
        yield Tuple.of(taskID, avoidTask);
      }

      case Test -> {
        //waypoints
        var wayPoints = attrMap.get("way_points").child(BotPsiElementTypes.ANGLE_BRACKED).child(BotPsiElementTypes.NAME).tokenText().toString();
        // construct new task
        var testTask = new TestTask(
            taskID,
            wayPoints
        );
        yield Tuple.of(taskID, testTask);
      }
    };
  }

  static String createTransition(GenericNode<?> node, ImmutableMap<String, Task> taskMap) {
    var missionContent = node.child(BotPsiElementTypes.MISSION).child(BotPsiElementTypes.MISSION_CONTENT);
    var startTaskID = missionContent.child(BotPsiElementTypes.MISSION_START_DECL).child(BotPsiElementTypes.TASK_NAME).tokenText().toString();
    for (var transition : missionContent.childrenOfType(BotPsiElementTypes.MISSION_TRANSITION)) {
      var cond = transition.child(BotPsiElementTypes.PAREN).child(BotPsiElementTypes.COND);
      var condId = cond.child(BotPsiElementTypes.ID).tokenText().toString();
      var argNode = cond.peekChild(BotPsiElementTypes.PAREN);
      var taskPair = transition.childrenOfType(BotPsiElementTypes.TASK_NAME)
          .map(GenericNode::tokenText)
          .map(StringSlice::toString)
          .toImmutableSeq();
      var curr_task = taskPair.get(0);
      var next_task = taskPair.get(1);

      if (argNode != null) { // transition has cond argument

        var isArgID = argNode.peekChild(BotPsiElementTypes.ID);
        if (isArgID != null) { // ID cond argument
          var arg = argNode.child(BotPsiElementTypes.ID).tokenText().toString();
          var tran = new Task.Transition<String>(condId, arg, curr_task, next_task);
          taskMap.get(curr_task).transitions.add(tran);

        } else { // number cond argument
          var arg = argNode.child(BotPsiElementTypes.NUMBER).tokenText().toDouble();
          var tran = new Task.Transition<Double>(condId, arg, curr_task, next_task);
          taskMap.get(curr_task).transitions.add(tran);
        }

      }else{ // transition has no cond argument
        var tran = new Task.Transition<Double>(condId, null, curr_task, next_task);
        taskMap.get(curr_task).transitions.add(tran);
      }

    }

    return startTaskID;
  }

  @NotNull
  private static AttributeMap createMap(GenericNode<? extends GenericNode<?>> task) {
    var isDetect = task.peekChild(BotPsiElementTypes.TASK_DETECT_KW);
    var isTrack = task.peekChild(BotPsiElementTypes.TASK_TRACK_KW);
    var isAvoid = task.peekChild(BotPsiElementTypes.TASK_AVOID_KW);
    var isTest = task.peekChild(BotPsiElementTypes.TASK_TEST_KW);
    var attrMap = new AttributeMap();
    task.child(BotPsiElementTypes.TASK_BODY).childrenOfType(BotPsiElementTypes.ATTRIBUTE)
        .forEach(attr -> attrMap.content.put(attr.child(BotPsiElementTypes.ID).tokenText(), attr.child(BotPsiElementTypes.ATTRIBUTE_EXPR)));


    if (isDetect != null) {
      attrMap.kind = TaskKind.Detect;
    } else if (isTrack!= null){
      attrMap.kind = TaskKind.Track;
    } else if (isAvoid != null){
      attrMap.kind = TaskKind.Avoid;
    } else if (isTest != null) {
      attrMap.kind = TaskKind.Test;
    } else {
      var name = task.peekChild(BotPsiElementTypes.NAME);
      // kind =
    }
    return attrMap;
  }


}
