# ESP32 Camera System - Architecture Documentation

## System Architecture Overview

```mermaid
graph TB
    subgraph "Hardware Layer"
        ESP32[ESP32-WROVER-DEV<br/>Camera Module OV2640<br/>WiFi 2.4GHz]
        SENSORS[Optional Sensors<br/>Motion PIR<br/>LCD Display<br/>Temperature]
    end
    
    subgraph "Network Layer"
        WIFI[WiFi Network<br/>10.0.0.0/24]
    end
    
    subgraph "Docker Services"
        BACKEND[FastAPI Backend<br/>Port 8000<br/>Python 3.13]
        N8N[n8n Automation<br/>Port 5678<br/>Workflow Engine]
        VIEWER[Image Viewer<br/>Port 8080<br/>Python Gallery]
    end
    
    subgraph "Storage"
        CAPTURES[(Captures Folder<br/>Shared Volume<br/>JPEG Images)]
        N8NDATA[(n8n Data<br/>Workflows<br/>Executions)]
    end
    
    subgraph "External Services"
        OPENAI[OpenAI API<br/>Vision & Chat<br/>GPT-4]
        EXTERNAL[External Webhooks<br/>Email/Slack/etc]
    end
    
    subgraph "Client Layer"
        BROWSER[Web Browser<br/>User Interface]
        API_CLIENT[API Clients<br/>curl/Postman/Scripts]
    end
    
    ESP32 -->|HTTP/80| WIFI
    SENSORS -->|I2C/GPIO| ESP32
    
    WIFI -->|Camera Feed| BACKEND
    WIFI -->|Direct Access| ESP32
    
    BACKEND -->|REST API| N8N
    BACKEND -->|Image Analysis| OPENAI
    BACKEND -->|Read/Write| CAPTURES
    
    N8N -->|Trigger Workflows| BACKEND
    N8N -->|Store Data| N8NDATA
    N8N -->|Send Notifications| EXTERNAL
    
    VIEWER -->|Serve Images| CAPTURES
    VIEWER -->|Fetch Images| ESP32
    
    BROWSER -->|HTTP/8000| BACKEND
    BROWSER -->|HTTP/5678| N8N
    BROWSER -->|HTTP/8080| VIEWER
    BROWSER -->|HTTP/80| ESP32
    
    API_CLIENT -->|REST Calls| BACKEND
    
    style ESP32 fill:#4a90e2,stroke:#2e5c8a,color:#fff
    style BACKEND fill:#50c878,stroke:#2d7a4a,color:#fff
    style N8N fill:#ff6b6b,stroke:#c92a2a,color:#fff
    style VIEWER fill:#ffd93d,stroke:#c9a500,color:#000
    style OPENAI fill:#9b59b6,stroke:#6c3483,color:#fff
```

## Component Interaction Flow

```mermaid
sequenceDiagram
    participant User
    participant Browser
    participant Backend
    participant ESP32
    participant n8n
    participant OpenAI
    participant Storage
    
    User->>Browser: Access Dashboard
    Browser->>Backend: GET /api/v1/esp32/status
    Backend->>ESP32: Check Device Status
    ESP32-->>Backend: Status Response
    Backend-->>Browser: Device Online
    
    User->>Browser: Capture Image
    Browser->>Backend: POST /api/v1/camera/capture
    Backend->>ESP32: GET /capture
    ESP32-->>Backend: JPEG Image Data
    Backend->>Storage: Save Image
    Backend-->>Browser: Capture Success
    
    User->>Browser: Analyze Image
    Browser->>Backend: POST /api/v1/ai/analyze-image
    Backend->>Storage: Read Image
    Backend->>OpenAI: Vision API Request
    OpenAI-->>Backend: Analysis Result
    Backend-->>Browser: Display Analysis
    
    User->>Browser: Trigger Workflow
    Browser->>Backend: POST /api/v1/n8n/trigger/camera-capture
    Backend->>n8n: Webhook POST
    n8n->>Backend: GET /api/v1/camera/capture
    Backend->>ESP32: Capture Image
    ESP32-->>Backend: Image Data
    Backend->>Storage: Save Image
    n8n->>OpenAI: Analyze Image
    OpenAI-->>n8n: Analysis
    n8n->>External: Send Notification
```

## Data Flow Architecture

```mermaid
flowchart LR
    subgraph Input
        CAM[Camera Sensor]
        MOT[Motion Sensor]
        USER[User Input]
    end
    
    subgraph Processing
        ESP[ESP32 Device]
        API[FastAPI Backend]
        WF[n8n Workflows]
    end
    
    subgraph Intelligence
        AI[AI Vision Analysis]
        RULES[Business Rules]
    end
    
    subgraph Output
        STORE[Image Storage]
        NOTIFY[Notifications]
        DISPLAY[Web Display]
    end
    
    CAM -->|Image Data| ESP
    MOT -->|Event Trigger| API
    USER -->|Commands| API
    
    ESP -->|HTTP| API
    API -->|Webhook| WF
    
    API -->|Image| AI
    WF -->|Logic| RULES
    
    AI -->|Labels/Tags| STORE
    RULES -->|Actions| NOTIFY
    API -->|Serve| DISPLAY
    
    STORE -->|Retrieve| DISPLAY
    
    style CAM fill:#4a90e2
    style API fill:#50c878
    style WF fill:#ff6b6b
    style AI fill:#9b59b6
    style STORE fill:#ffd93d
```

## API Architecture

```mermaid
graph TB
    subgraph "API Gateway - FastAPI"
        MAIN[main.py<br/>FastAPI App<br/>Port 8000]
        
        subgraph "API Routes /api/v1"
            CAMERA[/camera<br/>8 endpoints<br/>Image operations]
            ESP32[/esp32<br/>7 endpoints<br/>Device management]
            N8N[/n8n<br/>9 endpoints<br/>Workflow integration]
            SENSORS[/sensors<br/>10 endpoints<br/>Sensor data]
            AI[/ai<br/>5 endpoints<br/>Vision & Chat]
        end
        
        subgraph "Core Services"
            CONFIG[Configuration<br/>Environment vars<br/>Settings]
            LOGGING[Logging<br/>Request tracking<br/>Error handling]
        end
        
        subgraph "Data Models"
            PYDANTIC[Pydantic Models<br/>Validation<br/>Serialization]
        end
    end
    
    MAIN --> CAMERA
    MAIN --> ESP32
    MAIN --> N8N
    MAIN --> SENSORS
    MAIN --> AI
    
    CAMERA --> CONFIG
    ESP32 --> CONFIG
    N8N --> CONFIG
    SENSORS --> CONFIG
    AI --> CONFIG
    
    CAMERA --> LOGGING
    ESP32 --> LOGGING
    N8N --> LOGGING
    SENSORS --> LOGGING
    AI --> LOGGING
    
    CAMERA --> PYDANTIC
    ESP32 --> PYDANTIC
    N8N --> PYDANTIC
    SENSORS --> PYDANTIC
    AI --> PYDANTIC
    
    style MAIN fill:#50c878,stroke:#2d7a4a,color:#fff
    style CAMERA fill:#4a90e2,stroke:#2e5c8a,color:#fff
    style ESP32 fill:#4a90e2,stroke:#2e5c8a,color:#fff
    style N8N fill:#ff6b6b,stroke:#c92a2a,color:#fff
    style SENSORS fill:#ffd93d,stroke:#c9a500,color:#000
    style AI fill:#9b59b6,stroke:#6c3483,color:#fff
```

## Deployment Architecture

```mermaid
graph TB
    subgraph "Docker Compose Stack"
        subgraph "n8n Container"
            N8N_APP[n8n Application<br/>Node.js<br/>Port 5678]
            N8N_VOL[(n8n_data<br/>Volume)]
        end
        
        subgraph "Backend Container"
            BACKEND_APP[FastAPI App<br/>Python 3.13<br/>Port 8000]
            BACKEND_VOL[(captures<br/>Shared Volume)]
        end
        
        subgraph "Viewer Container"
            VIEWER_APP[Image Viewer<br/>Python 3.13<br/>Port 8080]
        end
        
        subgraph "Network"
            BRIDGE[esp32-network<br/>Bridge Network]
        end
    end
    
    subgraph "External"
        ESP32_DEV[ESP32 Device<br/>10.0.0.30:80]
        HOST[Host Machine<br/>localhost]
    end
    
    N8N_APP --> N8N_VOL
    BACKEND_APP --> BACKEND_VOL
    VIEWER_APP --> BACKEND_VOL
    
    N8N_APP --> BRIDGE
    BACKEND_APP --> BRIDGE
    VIEWER_APP --> BRIDGE
    
    BRIDGE -.->|HTTP| ESP32_DEV
    
    HOST -->|5678| N8N_APP
    HOST -->|8000| BACKEND_APP
    HOST -->|8080| VIEWER_APP
    
    style N8N_APP fill:#ff6b6b,stroke:#c92a2a,color:#fff
    style BACKEND_APP fill:#50c878,stroke:#2d7a4a,color:#fff
    style VIEWER_APP fill:#ffd93d,stroke:#c9a500,color:#000
    style ESP32_DEV fill:#4a90e2,stroke:#2e5c8a,color:#fff
```

## Sensor Integration Architecture

```mermaid
graph LR
    subgraph "Physical Sensors"
        PIR[PIR Motion Sensor<br/>GPIO Pin]
        LCD[LCD Display<br/>I2C Interface]
        TEMP[Temperature Sensor<br/>Optional]
        CAM[Camera OV2640<br/>Built-in]
    end
    
    subgraph "ESP32 Firmware"
        GPIO[GPIO Handler]
        I2C[I2C Handler]
        CAMERA_DRV[Camera Driver]
        WIFI[WiFi Stack]
    end
    
    subgraph "Backend API"
        SENSOR_API[Sensors API<br/>/api/v1/sensors]
        EVENT_PROC[Event Processor]
        DATA_STORE[Data Storage]
    end
    
    subgraph "Automation"
        N8N_WF[n8n Workflows]
        TRIGGERS[Event Triggers]
        ACTIONS[Automated Actions]
    end
    
    PIR --> GPIO
    LCD --> I2C
    TEMP --> I2C
    CAM --> CAMERA_DRV
    
    GPIO --> WIFI
    I2C --> WIFI
    CAMERA_DRV --> WIFI
    
    WIFI -->|HTTP POST| SENSOR_API
    SENSOR_API --> EVENT_PROC
    EVENT_PROC --> DATA_STORE
    EVENT_PROC --> TRIGGERS
    
    TRIGGERS --> N8N_WF
    N8N_WF --> ACTIONS
    
    ACTIONS -.->|Display Message| LCD
    ACTIONS -.->|Capture Image| CAM
    
    style PIR fill:#4a90e2
    style LCD fill:#ffd93d
    style SENSOR_API fill:#50c878
    style N8N_WF fill:#ff6b6b
```

## Security Architecture

```mermaid
graph TB
    subgraph "Security Layers"
        subgraph "Network Security"
            FIREWALL[Firewall Rules<br/>Port Restrictions]
            WIFI_SEC[WiFi Security<br/>WPA2/WPA3]
        end
        
        subgraph "Application Security"
            CORS[CORS Policy<br/>Origin Restrictions]
            RATE_LIMIT[Rate Limiting<br/>API Throttling]
            INPUT_VAL[Input Validation<br/>Pydantic Models]
        end
        
        subgraph "Data Security"
            ENV_VARS[Environment Variables<br/>Secrets Management]
            GITIGNORE[.gitignore<br/>Credential Protection]
            DOCKER_SEC[Docker Secrets<br/>Production Mode]
        end
        
        subgraph "Authentication (Future)"
            JWT[JWT Tokens<br/>User Auth]
            API_KEY[API Keys<br/>Service Auth]
            OAUTH[OAuth2<br/>Third-party Auth]
        end
    end
    
    style FIREWALL fill:#e74c3c,stroke:#c0392b,color:#fff
    style CORS fill:#e74c3c,stroke:#c0392b,color:#fff
    style ENV_VARS fill:#e74c3c,stroke:#c0392b,color:#fff
    style JWT fill:#95a5a6,stroke:#7f8c8d,color:#fff
```

## Technology Stack

```mermaid
mindmap
  root((ESP32 Camera<br/>System))
    Hardware
      ESP32-WROVER-DEV
        Dual Core 240MHz
        4MB Flash
        8MB PSRAM
        WiFi 2.4GHz
      OV2640 Camera
        1600x1200 UXGA
        JPEG Compression
      Optional Sensors
        PIR Motion
        LCD Display
        Temperature
    Backend
      FastAPI
        Python 3.13
        Async/Await
        Pydantic
      HTTP Client
        httpx
        Async requests
      Data Models
        Type validation
        Serialization
    Automation
      n8n
        Workflow Engine
        Visual Editor
        Webhooks
      Docker
        Containerization
        docker-compose
        Health checks
    AI/ML
      OpenAI
        GPT-4 Vision
        Chat API
        Image Analysis
      Future
        TensorFlow
        Edge AI
        Object Detection
    Storage
      File System
        JPEG images
        Captures folder
      Future Options
        PostgreSQL
        Redis
        S3/MinIO
    Frontend
      Web Interface
        Python Gallery
        HTML/CSS/JS
      API Docs
        Swagger UI
        ReDoc
        OpenAPI
```

---

## Key Architectural Decisions

### 1. **Microservices Architecture**
- Separate containers for backend, n8n, and viewer
- Independent scaling and deployment
- Clear separation of concerns

### 2. **RESTful API Design**
- Versioned API (`/api/v1`)
- Resource-based endpoints
- Standard HTTP methods

### 3. **Event-Driven Integration**
- Webhooks for n8n integration
- Sensor events trigger workflows
- Asynchronous processing

### 4. **Shared Storage**
- Docker volumes for image persistence
- Accessible by all services
- Simple backup/restore

### 5. **Extensible Sensor Framework**
- Generic sensor reading API
- Easy to add new sensor types
- Flexible metadata support

### 6. **Security by Design**
- Credentials in environment variables
- `.gitignore` for sensitive files
- Health checks for monitoring
- Ready for authentication layer

---

**For implementation details, see:**
- [Backend README](../backend/README.md)
- [API Endpoints](../backend/API_ENDPOINTS.md)
- [Deployment Guide](../backend/DEPLOYMENT.md)
