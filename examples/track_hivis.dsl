Task {
    Detect patrol_route {
        way_points: <Patrol>,
        gimbal_pitch: -30.0,
        drone_rotation: 0.0,
        sample_rate: 2,
        hover_delay: 0,
        model: coco,
        hsv_lower_bound: (175, 100, 100), # red
        hsv_upper_bound: (180, 255, 255)
    }

    Track tracking {
        gimbal_pitch: -30.0,
        model: coco,
        class: person,
        hsv_lower_bound: (175, 100, 100),
        hsv_upper_bound: (180, 255, 255)
    }
}


Mission {
    Start patrol_route
    Transition ( hsv_detection( car ) ) patrol_route -> tracking
    Transition (done) tracking -> patrol_route
    Transition (done) patrol_route -> patrol_route
}