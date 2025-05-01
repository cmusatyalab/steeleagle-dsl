package org.droneDSL.compile.codeGen.concrete;

import kala.collection.immutable.ImmutableSeq;

public class DetectTask extends Task {
  public float gimbalPitch;
  public float droneRotation;
  public int sampleRate;
  public int hoverDelay;
  public String model;

  public HSV lowerBound;
  public HSV upperBound;


  public DetectTask(String taskID, String wayPoints, float gimbalPitch, float droneRotation, int sampleRate, int hoverDelay, String model, HSV lowerBound, HSV upperBound) {
    super(taskID);
    this.wayPoints = wayPoints;
    this.gimbalPitch = gimbalPitch;
    this.droneRotation = droneRotation;
    this.sampleRate = sampleRate;
    this.hoverDelay = hoverDelay;
    this.model = model;
    this.lowerBound = lowerBound;
    this.upperBound = upperBound;
  }

  @Override
  public void debugPrint() {
    System.out.println("gimbal_pitch :" + gimbalPitch);
    System.out.println("drone_rotation :" + droneRotation);
    System.out.println("sample_rate :" + sampleRate);
    System.out.println("hover_delay :" + hoverDelay);
    System.out.println("model :" + model);
    System.out.println("hsv (lower_bound/upper_bound) :" + this.lowerBound + " / " + this.upperBound);
  }

  @Override
  public String generateDefineTaskCode() {
    return """
                # TASK%s
                task_attr_%s = {}
                task_attr_%s["gimbal_pitch"] = "%s"
                task_attr_%s["drone_rotation"] = "%s"
                task_attr_%s["sample_rate"] = "%s"
                task_attr_%s["hover_delay"] = "%s"
                task_attr_%s["coords"] = "%s"
                task_attr_%s["model"] = "%s"
                task_attr_%s["upper_bound"] = %s
                task_attr_%s["lower_bound"] = %s
        """.formatted(taskID, taskID, taskID, gimbalPitch, taskID, droneRotation, taskID, sampleRate, taskID, hoverDelay, taskID, wayPoints, taskID, model, taskID, upperBound.toString(), taskID, lowerBound.toString())
            + this.generateTaskTransCode() +
            """
                  task_arg_map["%s"] = TaskArguments(TaskType.Detect, transition_attr_%s, task_attr_%s)
          """.formatted(taskID, taskID, taskID);    
  }
}
