---
sidebar_position: 3
---

# Chapter 2: Python Control with rclpy

## Learning Objectives

By the end of this chapter, you will be able to:
- Create ROS 2 nodes in Python using the rclpy client library
- Implement publishers to send data to topics
- Implement subscribers to receive data from topics
- Create and use services for request-response communication
- Connect AI logic to robot controllers using Python

## Introduction to rclpy

The Robot Operating System 2 (ROS 2) Python client library, rclpy, provides a Python API for interacting with ROS 2. It allows you to create nodes, publish and subscribe to topics, and provide or consume services using Python, which is particularly important for integrating AI algorithms that are often prototyped and deployed in Python.

Python's simplicity and the rich ecosystem of scientific computing libraries make it an ideal choice for AI and robotics applications. With rclpy, you can leverage this ecosystem while maintaining compatibility with the broader ROS 2 ecosystem.

## Creating a ROS 2 Node in Python

A ROS 2 node in Python is essentially a Python class that inherits from `rclpy.Node`. Here's the basic structure:

```python
import rclpy
from rclpy.node import Node

class MyNode(Node):
    def __init__(self):
        super().__init__('node_name')
        # Node initialization code goes here

def main(args=None):
    rclpy.init(args=args)
    node = MyNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
```

### Node Naming and Initialization

When creating a node, you must provide a unique name. This name is used for identification in the ROS 2 graph and for logging purposes. Choose descriptive names that indicate the node's purpose, such as 'camera_driver', 'image_processor', or 'motion_controller'.

## Publishers and Subscribers

### Publishers

A publisher allows a node to send messages to a topic. To create a publisher, you use the `create_publisher()` method of your node:

```python
from std_msgs.msg import String

class PublisherNode(Node):
    def __init__(self):
        super().__init__('publisher_node')
        self.publisher = self.create_publisher(String, 'topic_name', 10)
        timer_period = 0.5  # seconds
        self.timer = self.create_timer(timer_period, self.timer_callback)

    def timer_callback(self):
        msg = String()
        msg.data = 'Hello World: %d' % self.get_clock().now().nanoseconds
        self.publisher.publish(msg)
        self.get_logger().info('Publishing: "%s"' % msg.data)
```

The second parameter is the topic name, and the third parameter is the queue size for outgoing messages.

### Subscribers

A subscriber allows a node to receive messages from a topic. To create a subscriber, you use the `create_subscription()` method:

```python
from std_msgs.msg import String

class SubscriberNode(Node):
    def __init__(self):
        super().__init__('subscriber_node')
        self.subscription = self.create_subscription(
            String,
            'topic_name',
            self.listener_callback,
            10)
        self.subscription  # prevent unused variable warning

    def listener_callback(self, msg):
        self.get_logger().info('I heard: "%s"' % msg.data)
```

## Services in Python

Services provide a request-response communication pattern. To create a service server:

```python
from example_interfaces.srv import AddTwoInts

class ServiceServer(Node):
    def __init__(self):
        super().__init__('service_server')
        self.srv = self.create_service(AddTwoInts, 'add_two_ints', self.add_two_ints_callback)

    def add_two_ints_callback(self, request, response):
        response.sum = request.a + request.b
        self.get_logger().info('Incoming request\na: %d b: %d' % (request.a, request.b))
        return response
```

And to create a service client:

```python
import rclpy
from rclpy.node import Node
from example_interfaces.srv import AddTwoInts

class ServiceClient(Node):
    def __init__(self):
        super().__init__('service_client')
        self.cli = self.create_client(AddTwoInts, 'add_two_ints')
        while not self.cli.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('service not available, waiting again...')
        self.req = AddTwoInts.Request()

    def send_request(self, a, b):
        self.req.a = a
        self.req.b = b
        self.future = self.cli.call_async(self.req)
        rclpy.spin_until_future_complete(self, self.future)
        return self.future.result()
```

## Connecting AI Logic to Robot Controllers

One of the key advantages of using Python with ROS 2 is the ability to easily integrate AI algorithms with robot control systems. For example, you might have a neural network running in Python that processes sensor data and outputs control commands:

```python
import numpy as np
import tensorflow as tf  # Example AI framework
from sensor_msgs.msg import Image
from geometry_msgs.msg import Twist

class AIBasedController(Node):
    def __init__(self):
        super().__init__('ai_controller')

        # Subscribe to sensor data
        self.image_sub = self.create_subscription(
            Image, 'camera/image_raw', self.image_callback, 10)

        # Publish control commands
        self.cmd_vel_pub = self.create_publisher(Twist, 'cmd_vel', 10)

        # Load pre-trained AI model
        self.model = tf.keras.models.load_model('path/to/model')

    def image_callback(self, msg):
        # Process image and convert ROS message to format expected by AI model
        processed_image = self.process_ros_image(msg)

        # Run inference
        control_output = self.model.predict(processed_image)

        # Convert AI output to ROS command
        cmd_msg = self.convert_to_cmd_vel(control_output)

        # Publish control command
        self.cmd_vel_pub.publish(cmd_msg)
```

This pattern allows AI algorithms to seamlessly integrate with ROS 2's communication framework, enabling sophisticated robot behaviors based on machine learning models.

## Best Practices for Python Control

1. **Error Handling**: Always include proper exception handling in your nodes
2. **Resource Management**: Ensure nodes are properly destroyed and resources are freed
3. **Threading**: Be aware of threading implications when working with callbacks
4. **Parameter Management**: Use ROS 2 parameters for configurable values
5. **Logging**: Use the built-in logging facilities for debugging and monitoring

## Key Takeaways

- rclpy provides the Python interface to ROS 2 functionality
- Nodes are the fundamental units of computation in ROS 2
- Publishers and subscribers enable asynchronous communication via topics
- Services provide synchronous request-response communication
- Python's AI ecosystem integrates seamlessly with ROS 2 for intelligent robot control

## Exercises

1. Write a Python node that publishes random numbers to a topic every second.
2. Create a subscriber that listens to the random number topic and calculates a running average.
3. Modify the example AI controller to accept parameters for model path and control frequency.
4. Design a service that accepts a target position and returns whether the robot can reach it.

## Summary

This chapter covered the fundamentals of creating ROS 2 nodes in Python using rclpy. We explored publishers and subscribers for asynchronous communication, services for synchronous request-response patterns, and how to connect AI logic to robot controllers. These concepts enable the integration of Python-based AI algorithms with ROS 2's robust communication framework.