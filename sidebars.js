/** @type {import('@docusaurus/plugin-content-docs').SidebarsConfig} */
const sidebars = {
  tutorialSidebar: [
    {
      type: 'category',
      label: 'Tutorial',
      items: [
        'intro',
        {
          type: 'category',
          label: 'Module 1: The Robotic Nervous System (ROS 2)',
          items: [
            'modules/ros2-fundamentals/intro',
            'modules/ros2-fundamentals/chapter-1-fundamentals',
            'modules/ros2-fundamentals/chapter-2-python-control',
            'modules/ros2-fundamentals/chapter-3-urdf-structure',
          ],
        },
        {
          type: 'category',
          label: 'Module 2: The Digital Twin (Gazebo & Unity)',
          items: [
            'modules/digital-twin/intro',
            'modules/digital-twin/chapter-1-gazebo-physics',
            'modules/digital-twin/chapter-2-unity-interaction',
            'modules/digital-twin/chapter-3-sensor-simulation',
          ],
        },
      ],
    },
  ],
};

module.exports = sidebars;