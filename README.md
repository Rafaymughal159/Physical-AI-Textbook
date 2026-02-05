# Physical AI Textbook

Welcome to the Physical AI Textbook project, a comprehensive guide to bridging artificial intelligence and robotics. This textbook focuses on creating intelligent, embodied systems that can interact with the physical world through robotics.

## About

This textbook is designed for AI and software students entering robotics, with a particular focus on:

- Physical AI concepts and implementations
- Robot operating systems (specifically ROS 2)
- Integration of AI algorithms with physical systems
- Control theory for embodied agents
- Sensor fusion and perception in physical contexts

## Modules

### Module 1: The Robotic Nervous System (ROS 2)

Currently completed module covering:

1. **ROS 2 Fundamentals** - Understanding the core concepts of ROS 2 including nodes, topics, services, and messages
2. **Python Control with rclpy** - Creating ROS 2 nodes in Python and connecting AI logic to robot controllers
3. **Humanoid Structure with URDF** - Modeling humanoid robots using the Unified Robot Description Format

## Getting Started

1. Install dependencies:
   ```bash
   npm install
   ```

2. Start the development server:
   ```bash
   npm start
   ```

3. Open [http://localhost:3000](http://localhost:3000) to view the textbook in your browser.

## Contributing

This project follows the Spec-Driven Development methodology with detailed specifications in the `specs/` directory. All changes should be made with consideration to the existing specifications and architecture decisions.

## License

MIT License - see the LICENSE file for details.

## Project Structure

```
Physical_AI_Textbook/
├── docs/                    # Documentation source files
│   ├── intro.md            # Main introduction
│   └── modules/            # Course modules
│       └── ros2-fundamentals/ # ROS 2 fundamentals module
│           ├── intro.md
│           ├── chapter-1-fundamentals.md
│           ├── chapter-2-python-control.md
│           └── chapter-3-urdf-structure.md
├── specs/                  # Specifications and plans
│   └── 1-ros2-fundamentals/ # ROS 2 fundamentals specs
├── src/                    # Source code including custom CSS
│   └── css/
│       └── custom.css
├── package.json            # Project dependencies
├── docusaurus.config.js    # Docusaurus configuration
├── sidebars.js             # Navigation sidebar configuration
└── README.md              # This file
```