---
sidebar_position: 4
---

# Chapter 3: Humanoid Structure with URDF

## Learning Objectives

By the end of this chapter, you will be able to:
- Explain the role of URDF in robotics
- Create and interpret URDF models for robot structures
- Define links, joints, and frames in URDF
- Understand how structure connects to control and simulation systems
- Design basic humanoid robot models using URDF

## Introduction to URDF

Unified Robot Description Format (URDF) is an XML-based format used in ROS to describe robot models. It defines the physical and visual properties of a robot, including its links (rigid parts), joints (connections between links), and kinematic relationships. URDF plays a crucial role in robotics by providing a standardized way to represent robot structure, which is essential for motion planning, simulation, and visualization.

For humanoid robots, URDF becomes particularly important as it must accurately represent the complex structure of a human-like robot with multiple degrees of freedom, sensors distributed throughout the body, and intricate kinematic chains that mirror human anatomy.

## The Role of URDF in Robotics

URDF serves several critical functions in a robotic system:

1. **Visualization**: URDF models allow tools like RViz to display a visual representation of the robot
2. **Simulation**: Physics simulators like Gazebo use URDF to create realistic simulation environments
3. **Motion Planning**: Planning algorithms rely on URDF for collision checking and kinematic calculations
4. **Control**: Controllers use URDF to understand the robot's structure and kinematics
5. **Documentation**: URDF serves as a comprehensive specification of the robot's mechanical design

## Links, Joints, and Frames

### Links

A link in URDF represents a rigid part of the robot. Each link has physical and visual properties:

- **Visual**: Defines how the link looks (geometry, material, origin)
- **Collision**: Defines collision properties for physics simulation
- **Inertial**: Defines mass, center of mass, and inertia matrix

```xml
<link name="link_name">
  <visual>
    <geometry>
      <cylinder length="0.6" radius="0.1"/>
    </geometry>
    <material name="blue">
      <color rgba="0 0 0.8 1"/>
    </material>
  </visual>
  <collision>
    <geometry>
      <cylinder length="0.6" radius="0.1"/>
    </geometry>
  </collision>
  <inertial>
    <mass value="1"/>
    <inertia ixx="1.0" ixy="0.0" ixz="0.0" iyy="1.0" iyz="0.0" izz="1.0"/>
  </inertial>
</link>
```

### Joints

A joint connects two links and defines the allowed motion between them. The relationship is always parent-child, where the child link moves relative to the parent:

```xml
<joint name="joint_name" type="revolute">
  <parent link="parent_link"/>
  <child link="child_link"/>
  <origin xyz="0 0 1" rpy="0 0 0"/>
  <axis xyz="0 0 1"/>
  <limit lower="-1.57" upper="1.57" effort="100" velocity="1"/>
</joint>
```

Joint types include:
- **Revolute**: Rotational joint with limited range
- **Continuous**: Rotational joint without limits
- **Prismatic**: Linear sliding joint with limits
- **Fixed**: No movement allowed
- **Floating**: 6 degrees of freedom
- **Planar**: Movement constrained to a plane

### Frames

URDF establishes a tree of coordinate frames, where each link has its own frame. The `origin` element in joints specifies the transformation from the parent frame to the child frame using XYZ translation and RPY (roll, pitch, yaw) rotation. This creates a kinematic chain that describes how each part of the robot moves relative to others.

## Creating a Basic Humanoid Model

Here's an example of a simplified humanoid torso model in URDF:

```xml
<?xml version="1.0"?>
<robot name="simple_humanoid_torso">
  <!-- Base link (torso) -->
  <link name="base_link">
    <visual>
      <geometry>
        <box size="0.3 0.2 0.5"/>
      </geometry>
      <material name="white">
        <color rgba="1 1 1 1"/>
      </material>
    </visual>
    <collision>
      <geometry>
        <box size="0.3 0.2 0.5"/>
      </geometry>
    </collision>
    <inertial>
      <mass value="10"/>
      <inertia ixx="1.0" ixy="0.0" ixz="0.0" iyy="1.0" iyz="0.0" izz="1.0"/>
    </inertial>
  </link>

  <!-- Neck joint and head link -->
  <joint name="neck_joint" type="revolute">
    <parent link="base_link"/>
    <child link="head_link"/>
    <origin xyz="0 0 0.3" rpy="0 0 0"/>
    <axis xyz="0 1 0"/>
    <limit lower="-0.785" upper="0.785" effort="10" velocity="2"/>
  </joint>

  <link name="head_link">
    <visual>
      <geometry>
        <sphere radius="0.1"/>
      </geometry>
      <material name="light_blue">
        <color rgba="0.5 0.5 1 1"/>
      </material>
    </visual>
    <collision>
      <geometry>
        <sphere radius="0.1"/>
      </geometry>
    </collision>
    <inertial>
      <mass value="2"/>
      <inertia ixx="0.01" ixy="0.0" ixz="0.0" iyy="0.01" iyz="0.0" izz="0.01"/>
    </inertial>
  </link>

  <!-- Right shoulder joint and arm -->
  <joint name="right_shoulder_joint" type="revolute">
    <parent link="base_link"/>
    <child link="right_upper_arm_link"/>
    <origin xyz="-0.2 0 0.1" rpy="0 0 0"/>
    <axis xyz="0 1 0"/>
    <limit lower="-1.57" upper="1.57" effort="10" velocity="2"/>
  </joint>

  <link name="right_upper_arm_link">
    <visual>
      <geometry>
        <cylinder length="0.3" radius="0.05"/>
      </geometry>
      <material name="gray">
        <color rgba="0.5 0.5 0.5 1"/>
      </material>
    </visual>
    <collision>
      <geometry>
        <cylinder length="0.3" radius="0.05"/>
      </geometry>
    </collision>
    <inertial>
      <mass value="1"/>
      <inertia ixx="0.01" ixy="0.0" ixz="0.0" iyy="0.01" iyz="0.0" izz="0.01"/>
    </inertial>
  </link>
</robot>
```

This model demonstrates the basic structure: a base link (torso) connected to child links (head and arm) through joints that define their relative motion.

## Connecting Structure to Control and Simulation

URDF models connect to control and simulation systems in several ways:

### Kinematic Solvers

Forward and inverse kinematics solvers use the URDF's kinematic chain to calculate joint positions needed to achieve desired end-effector poses. The DH parameters or geometric relationships are derived from the URDF structure.

### Controller Integration

Controllers in ROS 2 use URDF to understand the robot's structure and can interface with the robot state publisher to maintain awareness of joint positions:

```python
from urdf_parser_py.urdf import URDF
from pykdl_utils.kdl_kinematics import KDLKinematics

# Load URDF from parameter server or file
robot = URDF.from_parameter_server()
kinematics = KDLKinematics(robot, 'base_link', 'end_effector_link')
```

### Simulation Physics

Physics engines in simulation environments (like Gazebo) use the inertial properties defined in URDF to simulate realistic robot dynamics, collisions, and interactions with the environment.

## Best Practices for URDF Design

1. **Tree Structure**: URDF must form a tree (no loops/cycles in the kinematic chain)
2. **Mass Properties**: Accurate mass and inertia properties are crucial for simulation
3. **Joint Limits**: Realistic joint limits prevent impossible movements
4. **Frame Origins**: Choose origins that simplify calculations and match conventions
5. **Modularity**: Organize complex robots into manageable subassemblies
6. **Validation**: Use tools like `check_urdf` to validate your models

## URDF Tools and Ecosystem

Several tools facilitate URDF development and validation:

- **check_urdf**: Validates URDF syntax and structure
- **urdf_tutorial**: Provides examples and best practices
- **rviz**: Visualizes URDF models in real-time
- **gazebo**: Enables physics simulation of URDF robots
- **moveit**: Motion planning framework that uses URDF models

## Key Takeaways

- URDF is an XML-based format for describing robot structure in ROS
- Links represent rigid parts, joints define allowed motion between links
- Frames establish the coordinate system hierarchy for kinematic calculations
- URDF connects to control, simulation, and visualization systems
- Accurate URDF models are essential for realistic robot simulation and control

## Exercises

1. Create a simple 2-link planar manipulator in URDF with revolute joints
2. Add collision and visual properties to your manipulator model
3. Sketch how the kinematic chain of a 6-DOF manipulator would be represented in URDF
4. Explain how changing joint limits in URDF affects robot motion planning

## Summary

This chapter explored the Unified Robot Description Format (URDF), which serves as the standard for describing robot structure in ROS. We examined the fundamental concepts of links, joints, and frames, and how they come together to represent complex humanoid robot structures. We looked at how URDF connects to control and simulation systems, enabling accurate modeling of robotic systems. These concepts are essential for understanding how robot structure relates to motion planning, control, and simulation in Physical AI applications.