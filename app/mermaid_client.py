import os
import asyncio
from typing import Dict, Optional
import anthropic
from anthropic import AsyncAnthropic

class MermaidClient:
    def __init__(self):
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set")
        
        self.client = AsyncAnthropic(api_key=api_key)
        print("Using Claude for Mermaid diagram generation")
    
    async def generate_mermaid_diagram(
        self, 
        prompt: str, 
        diagram_type: str = "flowchart",
        context: Optional[str] = None,
        temperature: float = 0.3
    ) -> Dict[str, str]:
        system_prompt = """You are an expert at creating Mermaid diagrams. Your task is to generate valid Mermaid syntax based on user requests.

CRITICAL RULES:
1. ONLY return valid Mermaid diagram syntax
2. DO NOT include markdown code blocks (```mermaid or ```)
3. DO NOT include any explanations or additional text
4. The output should be ready to render directly in a Mermaid renderer
5. Start directly with the diagram type declaration

SUPPORTED DIAGRAM TYPES:
- flowchart: For process flows, decision trees, workflows
- sequenceDiagram: For interaction sequences between entities
- classDiagram: For UML class relationships
- stateDiagram-v2: For state machines and transitions
- erDiagram: For entity-relationship diagrams
- journey: For user journey mapping
- gantt: For project timelines and schedules
- pie: For percentage/distribution visualization
- quadrantChart: For 2x2 matrix analysis
- requirementDiagram: For requirement specifications
- gitGraph: For Git workflow visualization
- C4Context: For C4 architecture context diagrams
- mindmap: For hierarchical mind maps
- timeline: For chronological events
- zenuml: For ZenUML sequence diagrams
- sankey-beta: For flow and energy diagrams
- xychart-beta: For bar and line charts
- block-beta: For block/grid layouts
- packet-beta: For network packet structures
- kanban: For task boards
- architecture-beta: For system architecture
- radar-beta: For spider/skills charts
- treemap-beta: For hierarchical data visualization

MERMAID SYNTAX EXAMPLES:

Flowchart:
flowchart TD
    A[Start] --> B{Decision}
    B -->|Yes| C[Action 1]
    B -->|No| D[Action 2]
    C --> E[End]
    D --> E

Flowchart with Subgraphs:
flowchart TD
    A[Start] --> B{Check User}
    B -->|Valid| C[Process Request]
    B -->|Invalid| D[Return Error]
    
    subgraph Authentication
        C --> E[Validate Token]
        E --> F[Check Permissions]
    end
    
    subgraph Processing
        F --> G[Execute Logic]
        G --> H[Prepare Response]
    end
    
    H --> I[End]
    D --> I

Flowchart with Color Styling:
flowchart TD
    A[Start]:::startStyle --> B{Check Input}
    B -->|Valid| C[Process Data]:::processStyle
    B -->|Invalid| D[Show Error]:::errorStyle
    C --> E[Save Results]:::successStyle
    D --> F[End]:::endStyle
    E --> F
    
    classDef startStyle fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef processStyle fill:#f3e5f5,stroke:#4a148c,stroke-width:2px,color:#000
    classDef errorStyle fill:#ffebee,stroke:#c62828,stroke-width:2px,color:#000
    classDef successStyle fill:#e8f5e8,stroke:#2e7d32,stroke-width:2px,color:#000
    classDef endStyle fill:#f5f5f5,stroke:#424242,stroke-width:2px,color:#000

Sequence Diagram:
sequenceDiagram
    participant A as Alice
    participant B as Bob
    A->>B: Hello Bob
    B-->>A: Hello Alice

Class Diagram:
classDiagram
    class Animal {
        +String name
        +int age
        +makeSound()
    }
    class Dog {
        +bark()
    }
    class Cat {
        +meow()
    }
    Animal <|-- Dog : inherits
    Animal <|-- Cat : inherits

Class Diagram with Relationships:
classDiagram
    class User {
        -String userId
        -String name
        +login()
        +logout()
    }
    class Order {
        -String orderId
        -Date orderDate
        +createOrder()
        +cancelOrder()
    }
    class Product {
        -String productId
        -String name
        -Double price
    }
    class ShoppingCart {
        -List~Product~ items
        +addItem()
        +removeItem()
    }
    
    %% Relationships in Class Diagrams:
    %% Association: --> 
    %% Inheritance: <|--
    %% Composition: *--
    %% Aggregation: o--
    %% Implementation: <|..
    %% Dependency: <..
    %% With multiplicity: "1" --> "*"
    
    User "1" --> "*" Order : places
    Order "*" --> "*" Product : contains
    User "1" --> "1" ShoppingCart : has
    ShoppingCart "1" o-- "*" Product : contains
    
    %% IMPORTANT: Do NOT use ER diagram syntax like ||--o{ in class diagrams!
    %% That syntax is ONLY for erDiagram type

State Diagram:
stateDiagram-v2
    [*] --> Idle
    Idle --> Processing : Start
    Processing --> Error : Failed
    Processing --> Success : Completed
    Error --> Idle : Reset
    Success --> [*]

Entity Relationship Diagram:
erDiagram
    CUSTOMER ||--o{ ORDER : places
    ORDER ||--|{ LINE-ITEM : contains
    CUSTOMER {
        string name
        string address
        string phone
    }
    ORDER {
        int orderNumber
        date orderDate
    }

User Journey:
journey
    title My working day
    section Go to work
      Make tea: 5: Me
      Go upstairs: 3: Me
      Do work: 1: Me, Cat
    section Go home
      Go downstairs: 5: Me
      Sit down: 5: Me

Gantt Chart:
gantt
    title Project Timeline
    dateFormat YYYY-MM-DD
    section Design
    UI Design           :done,    des1, 2024-01-01, 2024-01-07
    Database Design     :active,  des2, 2024-01-04, 7d
    section Development
    Backend API         :         dev1, after des2, 10d
    Frontend            :         dev2, after dev1, 10d

Pie Chart:
pie title Sales Distribution
    "Product A" : 35
    "Product B" : 25
    "Product C" : 20
    "Product D" : 20

Quadrant Chart:
quadrantChart
    title Reach and engagement of campaigns
    x-axis Low Reach --> High Reach
    y-axis Low Engagement --> High Engagement
    quadrant-1 We should expand
    quadrant-2 Need to promote
    quadrant-3 Re-evaluate
    quadrant-4 May be improved
    Campaign A: [0.3, 0.6]
    Campaign B: [0.45, 0.23]
    Campaign C: [0.57, 0.69]
    Campaign D: [0.78, 0.34]

Requirement Diagram:
requirementDiagram
    requirement test_req {
    id: 1
    text: the test text.
    risk: high
    verifymethod: test
    }
    element test_entity {
    type: simulation
    }
    test_entity - satisfies -> test_req

GitGraph:
gitGraph:
    commit
    branch develop
    commit
    commit
    checkout main
    merge develop
    commit
    branch feature
    commit
    commit
    checkout main
    merge feature

C4 Diagram:
C4Context
    title System Context diagram for Internet Banking System
    Person(customerA, "Banking Customer", "A customer of the bank")
    System(SystemAA, "Internet Banking System", "Allows customers to view information")
    System_Ext(SystemC, "E-mail system", "The internal email system")
    Rel(customerA, SystemAA, "Uses")
    Rel(SystemAA, SystemC, "Sends e-mails", "SMTP")

Mindmap:
mindmap
  root((mindmap))
    Origins
      Long history
      Popularisation
        British popular psychology author Tony Buzan
    Research
      On effectiveness<br/>and features
      On Automatic creation
        Uses
            Creative techniques
            Strategic planning
            Argument mapping

Timeline:
timeline
    title History of Social Media
    2002 : LinkedIn
    2004 : Facebook
    2005 : YouTube
    2006 : Twitter
    2010 : Instagram
    2011 : Snapchat

ZenUML:
zenuml
    title Order Processing
    Customer.placeOrder() {
        OrderService.validateOrder()
        if(valid) {
            PaymentService.processPayment()
            if(success) {
                InventoryService.reserveItems()
                ShippingService.scheduleDelivery()
                return "Order confirmed"
            } else {
                return "Payment failed"
            }
        } else {
            return "Invalid order"
        }
    }

Sankey:
sankey-beta
    Electricity,Residential,80
    Electricity,Commercial,65  
    Electricity,Industrial,75
    Residential,Heating,45
    Residential,Cooling,25
    Residential,Appliances,10

XY Chart:
xychart-beta
    title "Sales Revenue"
    x-axis [jan, feb, mar, apr, may, jun, jul]
    y-axis "Revenue (in $)" 0 --> 10000
    bar [5000, 6000, 7500, 8200, 9500, 10000, 8500]
    line [4000, 5000, 6000, 7000, 8000, 9000, 8000]

Block Diagram:
block-beta
columns 3
  A B C
  D E F
  G H I

Block Diagram with Labels:
block-beta
columns 3
  A["Block A"] B["Block B"] C["Block C"]
  D["Block D"] E["Block E"] F["Block F"]

Block Diagram Simple Layout:
block-beta
  Frontend Backend Database
  Mobile API Cache

Packet Diagram:
packet-beta
    title Packet Structure
    0-7: "Version"
    8-15: "Type"
    16-31: "Length"
    32-63: "Payload"

Kanban:
kanban
  Todo
    [Create README]
    [Write Tests]
  In Progress
    [Implement Feature A]
    [Fix Bug #123]
  Done
    [Deploy to Production]
    [Update Documentation]

Architecture:
architecture-beta
    group public_api(cloud)[Public API]
    group private_api(server)[Private API]
    
    service web(database)[Web Server] in public_api
    service api(server)[API Gateway] in public_api
    service database1(database)[Database] in private_api
    service cache1(disk)[Cache] in private_api
    
    web:R --> L:api
    api:B --> T:database1
    api:B --> T:cache1

Radar Chart:
radar-beta
    title Skills Assessment
    axis communication["Communication"], technical["Technical"], leadership["Leadership"]
    axis problemSolving["Problem Solving"], creativity["Creativity"]
    
    curve alice["Alice"]{90, 85, 80, 88, 75}
    curve bob["Bob"]{75, 90, 85, 80, 82}
    
    graticule circle
    max 100

Radar Chart Restaurant Example:
radar-beta
    title Restaurant Comparison
    axis food["Food Quality"], service["Service"], price["Price"]
    axis ambiance["Ambiance"]
    
    curve a["Restaurant A"]{4, 3, 2, 4}
    curve b["Restaurant B"]{3, 4, 3, 3}
    curve c["Restaurant C"]{2, 3, 4, 2}
    curve d["Restaurant D"]{2, 2, 4, 3}
    
    graticule polygon
    max 5

Treemap:
treemap-beta
    "Section 1"
        "Leaf 1.1": 12
        "Section 1.2"
            "Leaf 1.2.1": 12
    "Section 2"
        "Leaf 2.1": 20
        "Leaf 2.2": 25

CRITICAL DIAGRAM-SPECIFIC RULES:
1. CLASS DIAGRAMS vs ER DIAGRAMS - DO NOT CONFUSE THEM:
   - classDiagram uses: -->, <|--, *--, o--, <|.., <.., with optional multiplicity like "1" --> "*"
   - erDiagram uses: ||--o{, ||--||, }o--||, etc.
   - NEVER use ER syntax (||--o{) in a class diagram!
   - NEVER use class syntax (-->) in an ER diagram!

2. When user asks for relationships between classes (like User and Order):
   - If diagram_type is "classDiagram": Use class diagram syntax: User "1" --> "*" Order : places
   - If diagram_type is "erDiagram": Use ER syntax: User ||--o{ Order : places
   - Check the diagram_type parameter to determine which syntax to use!

FORMATTING RULES:
- Use clear, descriptive node labels
- Include proper connectors and relationships
- Use appropriate styling when helpful
- Keep diagrams readable and well-structured
- Use standard Mermaid syntax only
- For complex flowcharts, consider using subgraphs to group related nodes:
  subgraph GroupName
      node1 --> node2
  end
- Subgraphs help organize complex processes and improve diagram readability
- When using colors in flowcharts, ensure proper contrast:
  * Use light fill colors with dark text (color:#000 or color:#333)
  * Use dark fill colors with light text (color:#fff or color:#f0f0f0)
  * Apply styles with :::className syntax and define classDef
  * Example: classDef errorStyle fill:#ffebee,stroke:#c62828,color:#000
- Color coding helps distinguish different types of nodes (start, process, error, success, end)

Return ONLY the Mermaid diagram code, nothing else."""
        
        # Construct the prompt based on diagram type and user request
        if context:
            full_prompt = f"Create a {diagram_type} diagram for: {prompt}\n\nAdditional context: {context}"
        else:
            full_prompt = f"Create a {diagram_type} diagram for: {prompt}"
        
        # Debug logging
        print(f"DEBUG: Generating Mermaid diagram for: {prompt[:100]}...")
        print(f"DEBUG: Diagram type: {diagram_type}")
        
        try:
            response = await self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=2048,
                temperature=temperature,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": full_prompt}
                ]
            )
        except Exception as e:
            print(f"First attempt failed: {e}")
            # Fallback to older model if needed
            response = await self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=2048,
                temperature=0.3,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": full_prompt}
                ]
            )
        
        # Extract the response text
        raw_text = response.content[0].text.strip()
        
        print(f"DEBUG: Raw response from Claude: {raw_text[:200]}...")
        
        # Clean up any potential markdown code blocks that might have been included
        mermaid_code = self._clean_mermaid_code(raw_text)
        
        # Validate the diagram syntax
        mermaid_code = self._validate_mermaid_syntax(mermaid_code, diagram_type)
        
        print(f"DEBUG: Final Mermaid code: {mermaid_code[:200]}...")
        
        return {
            "mermaid_code": mermaid_code
        }
    
    def _clean_mermaid_code(self, code: str) -> str:
        """Remove any markdown code blocks and extra formatting."""
        import re
        
        print(f"DEBUG: Cleaning code: {code[:200]}...")
        
        # Remove markdown code blocks
        code = re.sub(r'```mermaid\s*\n?', '', code)
        code = re.sub(r'```\s*$', '', code)
        code = re.sub(r'^```\s*\n?', '', code)
        
        # Remove any leading/trailing whitespace
        code = code.strip()
        
        # Check if the response is already valid Mermaid code
        diagram_types = ['flowchart', 'sequenceDiagram', 'classDiagram', 'stateDiagram-v2', 'stateDiagram', 
                        'erDiagram', 'journey', 'gantt', 'pie', 'quadrantChart', 'requirementDiagram', 
                        'gitGraph', 'C4Context', 'mindmap', 'timeline', 'zenuml', 'sankey-beta', 
                        'xychart-beta', 'block-beta', 'packet-beta', 'kanban', 'architecture-beta', 
                        'radar-beta', 'treemap-beta', 'graph']
        
        # If code starts with a diagram type, it's likely already clean
        if any(code.startswith(dt) for dt in diagram_types):
            print("DEBUG: Code already starts with diagram type")
            return code
        
        # Remove any explanatory text before or after the diagram
        lines = code.split('\n')
        diagram_started = False
        clean_lines = []
        
        for line in lines:
            line_stripped = line.strip()
            # Look for diagram type declarations
            if any(line_stripped.startswith(dt) for dt in diagram_types):
                diagram_started = True
                clean_lines.append(line)
                print(f"DEBUG: Found diagram start: {line_stripped}")
            elif diagram_started:
                # Once diagram started, include all subsequent lines that look like Mermaid syntax
                if line_stripped and not any(line_stripped.lower().startswith(word) for word in ['here', 'this', 'the above', 'note']):
                    clean_lines.append(line)
        
        if clean_lines:
            result = '\n'.join(clean_lines)
            print(f"DEBUG: Cleaned to: {result[:200]}...")
            return result
        
        # If no diagram type found but has Mermaid-like syntax, try to keep it
        if any(pattern in code.lower() for pattern in ['-->', '---', '|', 'participant', 'class', 'entity']):
            print("DEBUG: Found Mermaid-like patterns, keeping original")
            return code
        
        print("DEBUG: No Mermaid patterns found")
        return code
    
    def _validate_mermaid_syntax(self, code: str, expected_type: str) -> str:
        """Basic validation and correction of Mermaid syntax."""
        if not code:
            return f"{expected_type} TD\n    A[No diagram generated]"
        
        diagram_types = ['flowchart', 'sequenceDiagram', 'classDiagram', 'stateDiagram-v2', 'stateDiagram', 
                        'erDiagram', 'journey', 'gantt', 'pie', 'quadrantChart', 'requirementDiagram', 
                        'gitGraph', 'C4Context', 'mindmap', 'timeline', 'zenuml', 'sankey-beta', 
                        'xychart-beta', 'block-beta', 'packet-beta', 'kanban', 'architecture-beta', 
                        'radar-beta', 'treemap-beta', 'graph']
        
        # Ensure the diagram starts with the correct type
        if not any(code.strip().startswith(dt) for dt in diagram_types):
            # If no diagram type specified, add the expected one
            if expected_type == 'flowchart':
                code = f"flowchart TD\n{code}"
            else:
                code = f"{expected_type}\n{code}"
        
        return code