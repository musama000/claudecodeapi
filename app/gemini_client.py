import google.generativeai as genai
import os
from typing import Dict, Optional
import asyncio
import re

class GeminiClient:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set")
        
        genai.configure(api_key=api_key)
        
        # Configure safety settings for educational content
        # Using genai.types.HarmCategory enum for better compatibility
        safety_settings = [
            {
                "category": genai.types.HarmCategory.HARM_CATEGORY_HARASSMENT,
                "threshold": genai.types.HarmBlockThreshold.BLOCK_NONE
            },
            {
                "category": genai.types.HarmCategory.HARM_CATEGORY_HATE_SPEECH, 
                "threshold": genai.types.HarmBlockThreshold.BLOCK_NONE
            },
            {
                "category": genai.types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
                "threshold": genai.types.HarmBlockThreshold.BLOCK_NONE
            },
            {
                "category": genai.types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                "threshold": genai.types.HarmBlockThreshold.BLOCK_NONE
            }
        ]
        
        # Use gemini-2.5-pro
        self.model = genai.GenerativeModel(
            'gemini-2.5-flash-lite-preview-06-17',
            safety_settings=safety_settings
        )
        print("Using gemini-2.0-pro model")
    
    async def generate_threejs_code(
        self, 
        prompt: str, 
        context: Optional[str] = None,
        temperature: float = 0.7
    ) -> Dict[str, str]:
        system_prompt = """You are an expert educational Three.js developer creating STEM visualizations.

CRITICAL RULES - YOUR CODE MUST FOLLOW THESE EXACTLY:

1. NEVER create new scene, camera, or renderer - they already exist
2. NEVER wrap code in functions like (function() {})()
3. NEVER use document.body, document.createElement, or HTML elements (except control container)
4. NEVER use window object - use controlledWindow instead if needed
5. NEVER call requestAnimationFrame or renderer.render()
6. NEVER add event listeners
7. ALWAYS return an animate function if animation is needed
8. ALWAYS add labels and annotations to your visualizations
9. ALWAYS use RAG database for best code content for threejs, mix and match if needed, be creative if needed
10. CREATE INTERACTIVE CONTROLS: Use the empty controls template system for dynamic visualizations
11. Provide all code in 2d 


- scene: THREE.Scene (already created)
- camera: THREE.PerspectiveCamera (already created)  
- renderer: THREE.WebGLRenderer (already created)
- controls: OrbitControls instance (already created)
- canvas: Canvas element for text measurements
- THREE: Complete Three.js library with ALL addons directly available:
  * ParametricGeometry, OrbitControls, FontLoader, TextGeometry
  * TrackballControls, FlyControls, ConvexGeometry
  * GLTFLoader, OBJLoader, ColladaLoader
  * EffectComposer, RenderPass, ShaderPass
  * CopyShader, FXAAShader, LuminosityHighPassShader

CORRECT STRUCTURE:
```javascript
// 1. Configure existing scene (required)
scene.background = new THREE.Color(0xf0f0f0);
camera.position.set(5, 5, 5);
camera.lookAt(0, 0, 0);

// 2. Add lighting (recommended)
const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
scene.add(ambientLight);

// 3. Create visualization objects
const geometry = new THREE.BoxGeometry(1, 1, 1);
const material = new THREE.MeshPhongMaterial({ color: 0xff0000 });
const mesh = new THREE.Mesh(geometry, material);
scene.add(mesh);

// 4. Setup controls (if interactive)
clearControls();
showControls();
addSlider('Parameter', 0, 100, 50, (value) => {
    // Handle parameter changes
    updateVisualization();
});

// 5. Update function (if needed)
function updateVisualization() {
    // Remove old objects, rebuild scene
    console.log('🔄 Updating visualization');
}

// 6. Animation function (required)
function animate() {
    mesh.rotation.x += 0.01;
    controls.update(); // Update camera controls
}
return animate; // Must return function, don't call it
```

COMMON MISTAKES TO AVOID:
❌ const scene = new THREE.Scene(); // DON'T create new scene
❌ const camera = new THREE.PerspectiveCamera(...); // DON'T create new camera
❌ const renderer = new THREE.WebGLRenderer(); // DON'T create new renderer
❌ document.body.appendChild(...); // DON'T manipulate DOM
❌ document.createElement(...); // DON'T create HTML elements
❌ window.innerWidth/innerHeight; // DON'T use window object
❌ import { ... } from 'three'; // DON'T add imports - everything pre-loaded
❌ (function() { ... })(); // DON'T wrap in IIFE
❌ animate(); // DON'T call animate, return it instead
❌ requestAnimationFrame(animate); // DON'T handle render loop
❌ let mesh; updateVisualization() { mesh = new Mesh(...) } // DECLARE variables properly

INTERACTIVE CONTROLS SYSTEM:

REQUIRED SETUP for interactive visualizations:
```javascript
// 1. Clear and show controls panel
clearControls();
showControls();

// 2. Create parameter variables
let numRectangles = 10;
let functionType = 0; // 0=x², 1=sin(x), 2=x³
let rangeStart = -5;
let rangeEnd = 5;

// 3. Add interactive controls
addSlider('Rectangle Count', 5, 100, numRectangles, (value) => {
    numRectangles = parseInt(value);
    console.log('📊 Rectangle count:', numRectangles);
    updateVisualization();
});

addDropdown('Function Type', ['x²', 'sin(x)', 'x³'], (value) => {
    functionType = parseInt(value);
    console.log('🔢 Function type:', ['x²', 'sin(x)', 'x³'][functionType]);
    updateVisualization();
});

addSlider('Range Start', -10, 0, rangeStart, (value) => {
    rangeStart = parseFloat(value);
    console.log('⬅️ Range start:', rangeStart);
    updateVisualization();
});

addSlider('Range End', 0, 10, rangeEnd, (value) => {
    rangeEnd = parseFloat(value);
    console.log('➡️ Range end:', rangeEnd);
    updateVisualization();
});

// 4. Create update function that rebuilds visualization
function updateVisualization() {
    // Clear existing objects (store references to remove them)
    // Rebuild scene based on current parameters
    console.log('🔄 Updating with:', {numRectangles, functionType, rangeStart, rangeEnd});
    
    // Your visualization rebuild logic here
}

// 5. Initial setup
updateVisualization();
```

EDUCATIONAL VISUALIZATION PATTERNS:

For Math Functions:
```javascript
// Grid in XY plane
const gridHelper = new THREE.GridHelper(10, 20);
gridHelper.rotateX(Math.PI / 2);
scene.add(gridHelper);

// Function curve
const points = [];
for (let x = -5; x <= 5; x += 0.1) {
    const y = Math.sin(x); // Your function
    points.push(x, y, 0);
}
const geometry = new THREE.BufferGeometry();
geometry.setAttribute('position', new THREE.Float32BufferAttribute(points, 3));
const line = new THREE.Line(geometry, new THREE.LineBasicMaterial({ color: 0x0000ff }));
scene.add(line);
```

For Physics:
```javascript
// Use arrows for vectors
const dir = new THREE.Vector3(1, 0, 0);
const origin = new THREE.Vector3(0, 0, 0);
const length = 2;
const arrow = new THREE.ArrowHelper(dir, origin, length, 0xff0000);
scene.add(arrow);
```

For Chemistry:
```javascript
// Atoms as spheres
const atomGeometry = new THREE.SphereGeometry(0.3, 32, 16);
const atomMaterial = new THREE.MeshPhongMaterial({ color: 0xff0000 });
const atom = new THREE.Mesh(atomGeometry, atomMaterial);
scene.add(atom);
```

TEXT/LABEL CREATION:
```javascript
// Use provided canvas element for text rendering
function createTextLabel(text, position) {
    const context = canvas.getContext('2d');
    context.font = '20px Arial';
    context.fillStyle = 'black';
    context.fillText(text, 0, 20);
    
    const texture = new THREE.CanvasTexture(canvas);
    const sprite = new THREE.Sprite(new THREE.SpriteMaterial({ map: texture }));
    sprite.position.copy(position);
    return sprite;
}
```

REMEMBER:
- You're modifying an EXISTING scene, not creating a new app
- Return functions, don't call it - NEVER call animate()
- NO DOM manipulation except control container
- Use provided canvas element for text measurements only
- Declare ALL variables properly with let/const
- Wrap risky operations in try-catch blocks
- Remove old objects before adding new ones (prevent memory leaks)
- CONTROL FUNCTIONS AVAILABLE:
  * clearControls() - removes all existing controls
  * showControls() - makes control panel visible
  * hideControls() - hides control panel
  * addSlider(label, min, max, defaultValue, callback) - adds slider control
  * addDropdown(label, options, callback) - adds dropdown control
- ALWAYS include updateVisualization() function for real-time parameter changes
- Use console.log() with emojis for parameter tracking
- Include meaningful parameter ranges and labels
- Call controls.update() in animate function if using camera controls

Return EXACTLY in this format:
CODE:
```javascript
// Your scene manipulation code here (NO wrapping, NO new scene/camera/renderer)
```"""
        
        # Add educational context to reduce safety filter triggers
        educational_prefix = "Create an educational Three.js visualization for learning purposes. "
        
        full_prompt = f"{system_prompt}\n\n"
        if context:
            full_prompt += f"RAG CONTEXT - REFERENCE EXAMPLES:\n{context}\n\n"
            full_prompt += "Use these examples as inspiration for patterns and approaches.\n\n"
        full_prompt += f"User request: {educational_prefix}{prompt}"
        
        # Debug logging
        print(f"DEBUG: Prompt being sent to Gemini: {prompt[:100]}...")
        print(f"DEBUG: Full prompt length: {len(full_prompt)} characters")
        
        generation_config = genai.GenerationConfig(
            temperature=temperature,
            max_output_tokens=4096,
        )
        
        try:
            response = await asyncio.to_thread(
                self.model.generate_content,
                full_prompt,
                generation_config=generation_config
            )
        except Exception as e:
            # If blocked, try with more conservative temperature
            print(f"First attempt failed: {e}")
            generation_config.temperature = 0.3
            response = await asyncio.to_thread(
                self.model.generate_content,
                full_prompt,
                generation_config=generation_config
            )
        
        # Check if response was blocked by safety filters
        if not response.candidates or not response.candidates[0].content.parts:
            if response.candidates and hasattr(response.candidates[0], 'finish_reason'):
                finish_reason = response.candidates[0].finish_reason
                if finish_reason == "SAFETY":
                    # Extract safety ratings if available
                    if hasattr(response.candidates[0], 'safety_ratings'):
                        safety_issues = []
                        for rating in response.candidates[0].safety_ratings:
                            category_name = str(rating.category)
                            probability = str(rating.probability) if hasattr(rating, 'probability') else 'UNKNOWN'
                            safety_issues.append(f"{category_name}: {probability}")
                        raise ValueError(f"Response blocked by safety filters: {', '.join(safety_issues)}")
                    else:
                        raise ValueError("Response blocked by safety filters (no details available)")
                elif finish_reason:
                    # Map finish reasons to more descriptive messages
                    finish_reason_map = {
                        1: "STOP (normal completion)",
                        2: "MAX_TOKENS (hit token limit)",
                        3: "SAFETY (content filtered)",
                        4: "RECITATION (potential copyright issue)",
                        5: "OTHER"
                    }
                    reason_text = finish_reason_map.get(finish_reason, f"UNKNOWN ({finish_reason})")
                    raise ValueError(f"Response failed with reason: {reason_text}")
            
            raise ValueError("No content generated - response may have been blocked")
        
        text = response.text
        
        # Extract code more reliably
        code = self._extract_code(text)
        
        # Validate and fix common issues
        code = self._validate_and_fix_code(code)
        
        return {
            "code": code
        }
    
    def _extract_code(self, text: str) -> str:
        """Extract JavaScript code from response."""
        # Try multiple patterns
        patterns = [
            ("```javascript", "```"),
            ("```js", "```"),
            ("CODE:\n```javascript", "```"),
            ("CODE:\n```", "```")
        ]
        
        for start_marker, end_marker in patterns:
            start = text.find(start_marker)
            if start != -1:
                start += len(start_marker)
                end = text.find(end_marker, start)
                if end != -1:
                    return text[start:end].strip()
        
        return "// Error: Could not extract code from response"
    
    def _validate_and_fix_code(self, code: str) -> str:
        """Validate and fix common issues in generated code."""
        if not code or code.startswith("// Error"):
            return code
        
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