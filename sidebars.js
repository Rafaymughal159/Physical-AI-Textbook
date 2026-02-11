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
        {
          type: 'category',
          label: 'Module 3: The AI-Robot Brain (NVIDIA Isaac™)',
          items: [
            'modules/isaac-brain/chapter-1-isaac-sim',
            'modules/isaac-brain/chapter-2-isaac-ros',
            'modules/isaac-brain/chapter-3-navigation-nav2',
          ],
        },
        {
          type: 'category',
          label: 'Module 4: Vision-Language-Action (VLA)',
          items: [
            'modules/vla-module/chapter-1-voice-to-action',
            'modules/vla-module/chapter-2-language-based-planning',
            'modules/vla-module/chapter-3-autonomous-humanoid',
          ],
        },
      ],
    },
  ],
};

module.exports = sidebars;