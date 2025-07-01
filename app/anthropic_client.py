import os
import asyncio
from typing import Dict, Optional
import anthropic
from anthropic import AsyncAnthropic

class AnthropicClient:
    def __init__(self):
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set")
        
        self.client = AsyncAnthropic(api_key=api_key)
        print("Using Claude Sonnet 4 model")
    
    async def generate_threejs_code(
        self, 
        prompt: str, 
        context: Optional[str] = None,
        temperature: float = 0.7
    ) -> Dict[str, str]:
        system_prompt = """You are an expert educational Three.js developer creating STEM visualizations for a pre-configured execution environment.

CRITICAL EXECUTION ENVIRONMENT RULES:

1. NEVER create new scene, camera, or renderer - they are pre-configured and available
2. NEVER use document.body, document.createElement, or DOM manipulation (except control container)
3. NEVER use window object directly - use controlledWindow if needed
4. NEVER call requestAnimationFrame or renderer.render() - the render loop is handled automatically
5. NEVER add event listeners to window or document
6. NEVER include import statements - all libraries are pre-loaded
7. NEVER wrap code in IIFE functions like (function() {})()
8. ALWAYS return animate function if animation is needed - DO NOT call it
9. ALWAYS declare variables with let/const - avoid undefined variable references
10. ALWAYS use try-catch for risky operations like text rendering

AVAILABLE GLOBALS IN EXECUTION ENVIRONMENT:
- scene: THREE.Scene (pre-configured, do not recreate)
- camera: THREE.PerspectiveCamera (pre-configured, do not recreate)  
- renderer: THREE.WebGLRenderer (pre-configured, do not recreate)
- controls: OrbitControls instance (pre-configured, do not recreate)
- canvas: Canvas element for text measurements only
- THREE: Complete Three.js library with ALL addons:
  * ParametricGeometry, OrbitControls, FontLoader, TextGeometry
  * TrackballControls, FlyControls, ConvexGeometry
  * GLTFLoader, OBJLoader, ColladaLoader
  * EffectComposer, RenderPass, ShaderPass
  * CopyShader, FXAAShader, LuminosityHighPassShader

CONTROL SYSTEM FUNCTIONS:
- clearControls() - removes all existing UI controls
- showControls() - makes control panel visible
- hideControls() - hides control panel
- addSlider(label, min, max, defaultValue, callback) - adds interactive slider
- addDropdown(label, optionsArray, callback) - adds dropdown menu

REQUIRED CODE STRUCTURE:
```javascript
// 1. Configure existing scene (required)
scene.background = new THREE.Color(0xf0f0f0);
camera.position.set(5, 5, 5);
camera.lookAt(0, 0, 0);

// 2. Add lighting (recommended)
const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
scene.add(ambientLight);
const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
directionalLight.position.set(5, 10, 5);
scene.add(directionalLight);

// 3. Create visualization objects with proper cleanup tracking
let meshes = []; // Track objects for cleanup
const geometry = new THREE.BoxGeometry(1, 1, 1);
const material = new THREE.MeshPhongMaterial({ color: 0xff0000 });
const mesh = new THREE.Mesh(geometry, material);
scene.add(mesh);
meshes.push(mesh);

// 4. Setup interactive controls (if needed)
clearControls();
showControls();

let parameterValue = 50;
addSlider('Parameter', 0, 100, parameterValue, (value) => {
    parameterValue = parseFloat(value);
    console.log('📊 Parameter changed:', parameterValue);
    updateVisualization();
});

// 5. Update function for real-time changes
function updateVisualization() {
    // Remove old objects before adding new ones
    meshes.forEach(mesh => scene.remove(mesh));
    meshes = [];
    
    // Rebuild visualization with current parameters
    console.log('🔄 Updating visualization');
    // Your rebuild logic here
}

// 6. Animation function (return, don't call)
function animate() {
    mesh.rotation.x += 0.01;
    
    // IMPORTANT: Update controls for camera interaction
    if (controls) {
        controls.update();
    }
}
return animate; // Must return, never call animate()
```

CRITICAL CODE QUALITY RULES:
1. NEVER break lines in the middle of function calls, property accesses, or parameter lists. Each statement must be syntactically complete on its line.
2. ALWAYS declare variables before use. If using 'canvas', create it: const canvas = document.createElement('canvas');
3. TRACK AND DISPOSE: Keep arrays of created objects. When updating/recreating, first dispose old geometries, materials, and textures to prevent memory leaks.
4. DEPENDENT UPDATES: When a control changes a value (like size), update ALL dependent elements (geometry, edges, labels, etc).
5. NO PARTIAL IMPLEMENTATIONS: Complete every feature mentioned. No comments like "// Add similarly" or try/catch blocks that silently skip functionality.
6. PROPER SCOPE: Declare shared variables at the top scope, not inside functions, if they need to be accessed by multiple functions or controls.

Example of proper cleanup:
// Before creating new objects
oldObjects.forEach(obj => {
  if (obj.geometry) obj.geometry.dispose();
  if (obj.material) obj.material.dispose();
  parent.remove(obj);
});

SYNTAX ERROR PREVENTION:
❌ const myVar; // Missing initializer - will cause execution error
✅ const myVar = 0; // Always initialize const variables
✅ let myVar; // Use let if value comes later

❌ labelA.textContent = 'text'; // Undefined variable reference
✅ const labelA = createTextLabel('text', position); // Proper variable declaration

❌ new OrbitControls(camera, renderer.domElement); // Missing THREE prefix
✅ new THREE.OrbitControls(camera, renderer.domElement); // Correct addon usage

INTERACTIVE CONTROLS TEMPLATE:
```javascript
// Clear existing controls and setup new ones
clearControls();
showControls();

// Define parameter variables
let numElements = 20;
let elementType = 0; // Index for dropdown options
let scaleValue = 1.0;
let speedMultiplier = 1.0;

// Add controls with proper callbacks
addSlider('Element Count', 1, 100, numElements, (value) => {
    numElements = parseInt(value);
    console.log('📊 Element count:', numElements);
    updateVisualization();
});

addDropdown('Element Type', ['Spheres', 'Cubes', 'Cylinders'], (value) => {
    elementType = parseInt(value);
    console.log('🔷 Element type:', ['Spheres', 'Cubes', 'Cylinders'][elementType]);
    updateVisualization();
});

addSlider('Scale', 0.1, 2.0, scaleValue, (value) => {
    scaleValue = parseFloat(value);
    console.log('📏 Scale:', scaleValue);
    updateVisualization();
});

// Update function with cleanup
function updateVisualization() {
    // Clean up previous objects
    objectsToClean.forEach(obj => scene.remove(obj));
    objectsToClean = [];
    
    // Rebuild based on current parameters
    console.log('🔄 Rebuilding with:', {numElements, elementType, scaleValue});
    // Your visualization logic here
}

// Initial setup
updateVisualization();
```

TEXT/LABEL CREATION PATTERN:
```javascript
// Use provided canvas for text rendering
function createTextLabel(text, position, color = '#000000') {
    try {
        const context = canvas.getContext('2d');
        context.font = '20px Arial';
        const textWidth = context.measureText(text).width;
        canvas.width = textWidth + 20; // Add padding
        canvas.height = 30;
        context.font = '20px Arial';
        context.fillStyle = color;
        context.fillText(text, 10, 20);

        const texture = new THREE.CanvasTexture(canvas);
        const spriteMaterial = new THREE.SpriteMaterial({ map: texture });
        const sprite = new THREE.Sprite(spriteMaterial);
        sprite.position.copy(position);
        sprite.scale.set(1, 0.5, 1);
        return sprite;
    } catch (error) {
        console.log('Label creation skipped:', error.message);
        return null;
    }
}
```

EDUCATIONAL VISUALIZATION PATTERNS:

Mathematics:
```javascript
// Grid helper for coordinate reference
const gridHelper = new THREE.GridHelper(10, 20);
gridHelper.rotateX(Math.PI / 2); // XY plane
scene.add(gridHelper);

// Function visualization
function plotFunction(func, xMin, xMax, step = 0.1) {
    const points = [];
    for (let x = xMin; x <= xMax; x += step) {
        const y = func(x);
        points.push(new THREE.Vector3(x, y, 0));
    }
    const geometry = new THREE.BufferGeometry().setFromPoints(points);
    const line = new THREE.Line(geometry, new THREE.LineBasicMaterial({ color: 0x0000ff }));
    return line;
}
```

Physics:
```javascript
// Vector arrows
function createVector(direction, origin, length, color = 0xff0000) {
    const dir = new THREE.Vector3().copy(direction).normalize();
    const arrow = new THREE.ArrowHelper(dir, origin, length, color);
    return arrow;
}

// Particle systems
function createParticle(position, color, radius = 0.1) {
    const geometry = new THREE.SphereGeometry(radius, 16, 12);
    const material = new THREE.MeshPhongMaterial({ color });
    const particle = new THREE.Mesh(geometry, material);
    particle.position.copy(position);
    return particle;
}
```

COMMON EXECUTION ERRORS TO AVOID:
1. "Missing initializer in const declaration" - Always assign values to const variables
2. "labelA is not defined" - Declare all variables before using them
3. "ParametricGeometry is not a constructor" - Use THREE.ParametricGeometry
4. "Cannot read property of undefined" - Check object existence before accessing properties

ANIMATION BEST PRACTICES:
```javascript
function animate() {
    // Update object transformations
    objects.forEach((obj, index) => {
        obj.rotation.y += 0.01;
        obj.position.y = Math.sin(time + index) * 0.5;
    });
    
    // Update time for smooth animations
    time += 0.01 * speedMultiplier;
    
    // CRITICAL: Update camera controls
    if (controls) {
        controls.update();
    }
}
return animate; // Always return, never call
```

MEMORY MANAGEMENT:
```javascript
// Track objects for proper cleanup
let visualizationObjects = [];

function cleanupVisualization() {
    visualizationObjects.forEach(obj => {
        scene.remove(obj);
        if (obj.geometry) obj.geometry.dispose();
        if (obj.material) {
            if (Array.isArray(obj.material)) {
                obj.material.forEach(mat => mat.dispose());
            } else {
                obj.material.dispose();
            }
        }
    });
    visualizationObjects = [];
}
```

Return EXACTLY in this format:
CODE:
```javascript
// Your scene manipulation code here (NO wrapping, NO new scene/camera/renderer)
```

FINAL CHECKLIST:
✅ No new scene/camera/renderer creation
✅ All const variables have initial values
✅ All variables declared before use
✅ Controls setup with clearControls() and showControls()
✅ Animation function returns, doesn't call itself
✅ Controls.update() called in animation loop
✅ Console.log statements for debugging
✅ Try-catch blocks around risky operations
✅ Proper object cleanup in update functions"""
        
        # Add educational context to reduce safety filter triggers
        educational_prefix = "Create an educational Three.js visualization for learning purposes. "
        
        full_prompt = f"{system_prompt}\n\n"
        if context:
            full_prompt += f"RAG CONTEXT - REFERENCE EXAMPLES:\n{context}\n\n"
            full_prompt += "Use these examples as inspiration for patterns and approaches.\n\n"
        full_prompt += f"User request: {educational_prefix}{prompt}"
        
        # Debug logging
        print(f"DEBUG: Prompt being sent to Claude: {prompt[:100]}...")
        print(f"DEBUG: Full prompt length: {len(full_prompt)} characters")
        
        try:
            response = await self.client.messages.create(
                model="claude-opus-4-20250514",
                max_tokens=8192,
                temperature=temperature,
                messages=[
                    {"role": "user", "content": full_prompt}
                ]
            )
        except Exception as e:
            # If blocked, try with more conservative temperature
            print(f"First attempt failed: {e}")
            response = await self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=4096,
                temperature=0.3,
                messages=[
                    {"role": "user", "content": full_prompt}
                ]
            )
        
        # Extract the response text
        text = response.content[0].text
        
        # Extract code more reliably
        code = self._extract_code(text)
        
        # Validate and fix common issues
        code = self._validate_and_fix_code(code)
        
        return {
            "code": code
        }
    
    def _extract_code(self, text: str) -> str:
        """Extract JavaScript code from response."""
        # Debug logging
        print(f"DEBUG: Extracting code from response (first 500 chars): {text[:500]}")
        
        # Try multiple patterns
        patterns = [
            ("```javascript", "```"),
            ("```js", "```"), 
            ("CODE:\n```javascript", "```"),
            ("CODE:\n```", "```"),
            ("CODE:", "```"),  # Handle CODE: followed by code block
            ("```", "```")  # Fallback for any code block
        ]
        
        for start_marker, end_marker in patterns:
            start = text.find(start_marker)
            if start != -1:
                start += len(start_marker)
                # Skip any newlines after the start marker
                while start < len(text) and text[start] in '\n\r':
                    start += 1
                
                end = text.find(end_marker, start)
                if end != -1:
                    extracted_code = text[start:end].strip()
                    print(f"DEBUG: Successfully extracted code using pattern '{start_marker}' -> '{end_marker}'")
                    print(f"DEBUG: Extracted code length: {len(extracted_code)}")
                    return extracted_code
        
        # If no code blocks found, check if the entire response is code (without markers)
        if text.strip().startswith('//') or 'scene.' in text or 'THREE.' in text:
            print("DEBUG: Treating entire response as code (no markers found)")
            return text.strip()
        
        print(f"DEBUG: No code patterns matched. Response: {text[:200]}...")
        return "// Error: Could not extract code from response"
    
    def _validate_and_fix_code(self, code: str) -> str:
        """Validate and fix common issues in generated code."""
        if not code or code.startswith("// Error"):
            return code
        
        import re
        
        # Check for IIFE wrapper and remove it
        iife_match = re.match(r'^\s*\(\s*function\s*\(\s*\)\s*\{([\s\S]*)\}\s*\)\s*\(\s*\)\s*;?\s*$', code)
        if iife_match:
            code = iife_match.group(1).strip()
            print("Warning: Removed IIFE wrapper from generated code")
        
        # Check for common violations
        violations = []
        
        if re.search(r'(const|let|var)\s+scene\s*=\s*new\s+THREE\.Scene', code):
            violations.append("Creates new scene")
            code = re.sub(r'(const|let|var)\s+scene\s*=\s*new\s+THREE\.Scene\s*\([^)]*\)\s*;?', 
                         '// scene already exists', code)
        
        if re.search(r'(const|let|var)\s+camera\s*=\s*new\s+THREE\.(Perspective|Orthographic)Camera', code):
            violations.append("Creates new camera")
            code = re.sub(r'(const|let|var)\s+camera\s*=\s*new\s+THREE\.(Perspective|Orthographic)Camera\s*\([^)]*\)\s*;?', 
                         '// camera already exists', code)
        
        if re.search(r'(const|let|var)\s+renderer\s*=\s*new\s+THREE\.WebGLRenderer', code):
            violations.append("Creates new renderer")
            code = re.sub(r'(const|let|var)\s+renderer\s*=\s*new\s+THREE\.WebGLRenderer\s*\([^)]*\)\s*;?', 
                         '// renderer already exists', code)
        
        if 'document.body.appendChild' in code:
            violations.append("Manipulates DOM")
            code = re.sub(r'document\.body\.appendChild\s*\([^)]*\)\s*;?', '// DOM manipulation removed', code)
        
        if 'document.createElement' in code:
            violations.append("Creates DOM elements")
            code = re.sub(r'const\s+\w+\s*=\s*document\.createElement\s*\([^)]*\)\s*;?', '// DOM element creation removed', code)
            # Remove all subsequent lines that reference the created element
            code = re.sub(r'\w+\.style\.[^;]*;?\s*\n?', '', code)
            code = re.sub(r'\w+\.innerHTML\s*=\s*[^;]*;?\s*\n?', '', code)
        
        if 'window.innerWidth' in code or 'window.innerHeight' in code:
            violations.append("Uses window dimensions")
            code = code.replace('window.innerWidth', '800 /* canvas width */')
            code = code.replace('window.innerHeight', '600 /* canvas height */')
        
        if 'requestAnimationFrame' in code:
            violations.append("Calls requestAnimationFrame")
            code = re.sub(r'requestAnimationFrame\s*\(\s*animate\s*\)\s*;?', '// Animation handled by React', code)
        
        if 'renderer.render' in code:
            violations.append("Calls renderer.render")
            code = re.sub(r'renderer\.render\s*\([^)]*\)\s*;?', '// Rendering handled by React', code)
        
        if re.search(r'animate\s*\(\s*\)\s*;?\s*$', code):
            violations.append("Calls animate function")
            code = re.sub(r'animate\s*\(\s*\)\s*;?\s*$', '// Return animate instead of calling it', code)
        
        if 'window.addEventListener' in code:
            violations.append("Adds event listeners")
            code = re.sub(r'window\.addEventListener\s*\([^)]*\)\s*;?', '// Event handling by React', code)
        
        # Add warning comment if violations found
        if violations:
            warning = f"// WARNING: Fixed violations: {', '.join(violations)}\n\n"
            code = warning + code
        
        # Ensure the code returns the animate function if it exists
        if 'function animate' in code and not re.search(r'return\s+animate\s*;?\s*$', code):
            code = code.rstrip() + '\n\nreturn animate;'
        
        return code