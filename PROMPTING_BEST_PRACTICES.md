# Prompting Best Practices for Three.js RAG Generator

## Overview
These best practices ensure you get high-quality, efficient Three.js code that properly manages objects and interactions.

## 1. Clear Concept Descriptions
- Start with specific STEM concept explanations
- Be explicit about the educational goal
- Provide context about what students should learn

**Example:**
```
"Create a visualization demonstrating wave interference patterns in physics, showing how two waves combine to create constructive and destructive interference."
```

## 2. Provide RAG Context
- Include relevant equations/diagrams for accuracy
- Reference specific Three.js patterns when applicable
- Mention if you want certain visual styles or approaches

**Example:**
```
"Show wave equation: y = A*sin(kx - ωt). Use sine waves with adjustable frequency and amplitude parameters."
```

## 3. Specify UI Controls and Behavior
- Mention needed sliders/dropdowns and their ranges
- **CRITICAL:** Explicitly state that controls should UPDATE existing objects, not create new ones
- Specify if objects should be replaced or modified in place
- Define what each control should affect

**Example:**
```
"Add a radius slider (1-10, step 0.1) that UPDATES the existing sphere's geometry, not creates new spheres. Include a rotation speed slider (0-0.1, step 0.001) for fine control. Add a particle count slider (1-100, step 1) for integer values only."
```

## 4. Note Animation Needs
- Indicate if animations are required
- Clarify if animations should be smooth transitions or immediate updates
- Specify animation speed and style preferences

**Example:**
```
"Include smooth rotation animation. When sliders change, animate the transition over 0.5 seconds rather than instant updates."
```

## 5. Cleanup Requirements ⚠️ IMPORTANT
- Specify if old objects should be removed before creating new ones
- Mention memory management needs for complex visualizations
- Request proper disposal of geometries and materials

**Example:**
```
"Use proper cleanup in updateVisualization() - dispose of old geometry and materials before creating new ones to prevent memory leaks."
```

## 6. Interaction Expectations ⚠️ CRITICAL
- State whether slider changes should modify existing geometry or recreate it
- Clarify if multiple objects should be managed as a group
- Specify how objects should respond to parameter changes

**Example:**
```
"When the 'number of particles' slider changes, remove all existing particles and create the new amount. When 'particle size' changes, update the scale of existing particles without recreating them."
```

## Common Anti-Patterns to Avoid

### ❌ Bad Prompts:
- "Create a sphere with a radius slider"
- "Make some particles that can be controlled"
- "Add animation to the scene"

### ✅ Good Prompts:
- "Create a sphere visualization where the radius slider (0.5-5.0) updates the existing sphere's geometry using geometry.scale(), not creating new spheres"
- "Create a particle system where the count slider removes existing particles and creates the new amount, while the size slider updates existing particles' scale property"
- "Add rotation animation that can be paused/resumed with a button, rotating around the Y-axis at 0.01 radians per frame"

## Example Complete Prompt

```
Create a physics visualization demonstrating simple harmonic motion with a pendulum.

Educational Goal: Show how period relates to string length (T = 2π√(L/g))

Visual Requirements:
- Single pendulum with adjustable string length
- String length slider (1-10 meters, step 0.1) that UPDATES the existing pendulum, not creates new ones
- Amplitude slider (-60° to +60°, step 1) that changes the starting angle in degree increments
- Gravity slider (1-20 m/s², step 0.1) that affects the motion speed with fine control

Interaction Behavior:
- String length changes should update the existing line geometry and pivot point
- Amplitude changes should reset the pendulum to the new starting position
- Gravity changes should affect the animation speed immediately

Animation:
- Smooth pendulum swinging motion using sin/cos functions
- Period should update automatically when length or gravity changes
- Include a "Reset" button that returns to starting position

Cleanup:
- Proper disposal of old geometries when parameters change
- Track all created objects for easy cleanup
```

## Slider Step Guidelines

Choose appropriate step values based on parameter type:

- **Integer counts** (particles, objects): `step: 1`
- **Percentages** (0-100%): `step: 1` or `step: 5`
- **Small decimals** (0-1 range): `step: 0.01` or `step: 0.1`
- **Rotation speeds** (radians): `step: 0.001` or `step: 0.01`
- **Angles** (degrees): `step: 1` or `step: 5`
- **Scale factors**: `step: 0.1`
- **Physics values** (precise): `step: 0.01` or `step: 0.001`

## Tips for Better Results

1. **Be Specific About Updates**: Always clarify whether changes should modify existing objects or create new ones
2. **Mention Performance**: Request efficient solutions for complex visualizations
3. **Define Boundaries**: Set clear parameter ranges and limits
4. **Request Validation**: Ask for parameter bounds checking
5. **Specify Cleanup**: Always mention proper resource disposal for complex scenes
6. **Include Step Values**: Specify appropriate slider steps for the parameter type

## Troubleshooting Common Issues

**Problem:** Sliders create new objects instead of updating
**Solution:** Add "UPDATE existing [object], not create new" to your prompt

**Problem:** Memory leaks in complex visualizations  
**Solution:** Request "proper cleanup with geometry/material disposal"

**Problem:** Choppy animations
**Solution:** Specify "smooth transitions" and animation duration

**Problem:** Parameters don't affect the right properties
**Solution:** Be explicit about which properties each control should modify