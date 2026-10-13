# HomeLab Sentinel

**AI-Assisted Server Monitoring, Security Analysis, and Troubleshooting System**

**Information Technology Capstone Project**

## Project Overview

HomeLab Sentinel is a Python-based web application developed as a Bachelor of Science in Information Technology capstone project.

The application demonstrates how server monitoring, automated alert detection, security event analysis, and artificial intelligence can work together to help identify and troubleshoot common home server problems.

HomeLab Sentinel uses a Flask web dashboard to display simulated server performance, generate system and security events, identify suspicious activity patterns, and provide AI-assisted troubleshooting recommendations grounded in a local knowledge base.

**Important:** HomeLab Sentinel currently operates entirely in a simulated environment. It does not connect to a live server, monitor actual network traffic, or detect real cybersecurity incidents.

## Project Objectives

- Develop a functional web-based monitoring dashboard.
- Simulate common server performance issues and service failures.
- Detect and record server alerts using predefined rules.
- Generate and analyze simulated application and security logs.
- Identify suspicious security event patterns.
- Store server state, event logs, and alert history using SQLite.
- Retrieve relevant troubleshooting documentation from a local knowledge base.
- Integrate the OpenAI API to generate knowledge-grounded troubleshooting explanations.
- Provide local troubleshooting guidance when the AI service is unavailable.
- Demonstrate automated software testing, version control, and technical documentation.

## Technologies Used

| Technology | Purpose |
|---|---|
| Python | Core application logic and event analysis |
| Flask | Web application framework and routing |
| SQLite | Persistent server state, event logs, and alert history |
| HTML | Dashboard and troubleshooting page structure |
| Bootstrap 5 | Responsive dashboard interface |
| CSS | Custom Midnight Blue dashboard theme |
| OpenAI API | AI-assisted troubleshooting explanations |
| Local knowledge base | Trusted troubleshooting reference material |
| Markdown | Formatting generated AI responses |
| Bleach | Sanitizing AI-generated HTML |
| python-dotenv | Loading environment variables |
| unittest | Automated software testing |
| Git and GitHub | Version control and project documentation |

## Key Features

### 1. Server Monitoring Dashboard

The dashboard displays simulated performance metrics for a demonstration home server.

Monitored values include:

- CPU utilization
- Memory utilization
- Storage utilization
- Plex service status
- Sonarr service status
- Radarr service status

Resource utilization is displayed using progress bars and status indicators.

The interface identifies elevated and critical resource usage and displays service health information.

### 2. Server Alert Detection

HomeLab Sentinel detects simulated server problems using predefined conditions.

Supported server scenarios include:

- High CPU usage
- Storage capacity warnings
- Docker service failures

When a simulated problem occurs, the dashboard updates its displayed server state and identifies active alerts.

The application records simulation events in a SQLite database for historical reference.

A **Reset Server** control restores the demonstration server to its default operating state.

### 3. Simulated Event Log Analyzer

HomeLab Sentinel includes an event logging system that generates realistic demonstration records.

Supported application and system events include:

- Plex playback errors
- Docker container crashes
- Disk I/O warnings

Each event contains a timestamp, source, severity, category, and descriptive message.

The dashboard displays the 20 most recent simulated events, ordered from newest to oldest.

These events are stored in SQLite and remain available after the application restarts.

### 4. Security Event Monitoring

The application supports simulated cybersecurity events, including:

- Failed SSH login attempts
- Suspicious network activity
- Unauthorized access attempts

Security events are recorded in the same event logging system used for application and server events.

The dashboard displays two security statistics:

- Total simulated security events
- Critical security events

These counters represent recorded demonstration events rather than confirmed real-world threats.

### 5. Automated Security Pattern Detection

HomeLab Sentinel uses rule-based analysis to identify suspicious patterns in simulated security logs.

The detection system evaluates events recorded within a five-minute window.

| Security Pattern | Detection Rule | Severity |
|---|---|---|
| Possible Brute-Force Activity | Three failed SSH event batches within five minutes | Critical |
| Repeated Suspicious Network Activity | Three suspicious network events within five minutes | Warning |
| Unauthorized Access Detected | One unauthorized access event within five minutes | Critical |

When a detection threshold is reached, the dashboard displays a security finding with its severity, description, and troubleshooting option.

These findings are generated through analysis of stored simulated events. They do not indicate actual attacks or confirmed system compromise.

### 6. AI-Assisted Troubleshooting

HomeLab Sentinel integrates the OpenAI API to generate troubleshooting explanations for active server alerts and detected security patterns.

The application uses a local troubleshooting knowledge base to provide context to the AI model.

The troubleshooting process follows these steps:

1. A simulated server alert or security pattern is detected.
2. The user selects **Troubleshoot with AI**.
3. The application retrieves relevant information from the local knowledge base.
4. The retrieved documentation is supplied to the OpenAI model.
5. The AI generates an explanation and recommended investigation steps.
6. The response is sanitized and displayed in the troubleshooting interface.

The AI is instructed to use only the supplied runbook, avoid inventing evidence or commands, and distinguish suspicious activity from confirmed compromise.

**HomeLab Sentinel provides troubleshooting recommendations only. It does not automatically execute repair commands, block network connections, or modify server configurations.**

### 7. Local Troubleshooting Knowledge Base

Troubleshooting documentation is stored in:

`knowledge_base/troubleshooting.txt`

The application retrieves relevant guidance based on the category of an active alert or detected security pattern.

The local knowledge base contains troubleshooting information for supported server and security scenarios.

This approach helps keep generated recommendations grounded in documented procedures rather than unrestricted AI-generated suggestions.

### 8. AI Fallback Support

HomeLab Sentinel can operate without an OpenAI API key.

If the API key is missing, the AI service is unavailable, or a request fails, the application displays the retrieved local troubleshooting guidance.

This ensures that basic troubleshooting documentation remains available even when AI-generated explanations cannot be produced.

### 9. Security Event Reset

The dashboard includes a **Reset Security Events** control for demonstration and testing purposes.

This feature:

- Removes simulated security event logs.
- Clears corresponding security alert-history entries.
- Resets security event counters.
- Removes active security pattern findings.
- Preserves application and system event logs.
- Preserves the simulated server's current metrics and service status.

The reset feature allows security scenarios to be demonstrated repeatedly without restarting the application or manually editing the database.

## System Architecture

HomeLab Sentinel uses a lightweight, modular architecture.

**User Interface**

Flask templates, HTML, Bootstrap, and CSS provide the monitoring dashboard and troubleshooting pages.

**Application Layer**

Python and Flask handle simulation requests, server state management, security pattern detection, knowledge retrieval, and AI integration.

**Database Layer**

SQLite stores persistent information in three tables:

| Table | Purpose |
|---|---|
| `demo_state` | Current simulated server metrics and service status |
| `event_logs` | Simulated application, system, and security events |
| `alerts` | Historical alert and simulation records |

**Knowledge Layer**

The local troubleshooting file provides documented investigation procedures for supported scenarios.

**AI Layer**

The OpenAI API generates explanations using the retrieved local troubleshooting guidance.

### Simplified Application Workflow

```text
User Opens Dashboard
        |
        v
Flask Application
        |
        v
SQLite Database
        |
        +--------------------------+
        |                          |
        v                          v
Simulated Server State       Simulated Event Logs
        |                          |
        v                          v
Server Alert Detection       Security Pattern Detection
        |                          |
        +-------------+------------+
                      |
                      v
              Active Alert/Finding
                      |
                      v
             Troubleshoot with AI
                      |
                      v
             Local Knowledge Base
                      |
                      v
                 OpenAI API
                      |
                      v
             Troubleshooting Guide
```

If the OpenAI API is unavailable, the application displays the retrieved local knowledge-base guidance instead.

## Installation and Setup

### Prerequisites

- Python 3.9 or newer
- Git
- Windows PowerShell or another compatible terminal
- Internet access for installing dependencies
- An OpenAI API key (optional for local troubleshooting)

### Step 1: Clone the Repository

```powershell
git clone https://github.com/des0620/HomeLab-Sentinel.git
```

### Step 2: Open the Project Directory

```powershell
cd HomeLab-Sentinel
```

### Step 3: Create a Virtual Environment

```powershell
python -m venv .venv
```

### Step 4: Activate the Virtual Environment

In Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

### Step 5: Install Dependencies

```powershell
python -m pip install -r requirements.txt
```

### Step 6: Configure OpenAI (Optional)

Create a `.env` file in the project directory.

Add:

```dotenv
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-4.1-mini
```

Replace `your_api_key_here` with your own API key.

The application can still provide local troubleshooting guidance without an API key.

**Never upload your real `.env` file or API credentials to GitHub.**

### Step 7: Start the Application

```powershell
python app.py
```

### Step 8: Open the Dashboard

Open a web browser and navigate to:

http://127.0.0.1:5000

The HomeLab Sentinel dashboard should display the default simulated server state.

## Demonstration Scenarios

The following scenarios can be used to demonstrate the application's functionality.

### Scenario 1: High CPU Usage

1. Open the dashboard.
2. Click **High CPU**.
3. Observe the CPU utilization increase to 95%.
4. Confirm that an active server alert appears.
5. Select **Troubleshoot with AI**.
6. Review the generated explanation or local troubleshooting guide.
7. Click **Reset Server** to restore normal metrics.

### Scenario 2: Docker Service Failure

1. Click **Docker Failure**.
2. Confirm that Plex displays a stopped status.
3. Review the active Docker alert.
4. Open the troubleshooting page.
5. Reset the simulated server.

### Scenario 3: Possible Brute-Force Activity

1. Click **Failed SSH Logins** three times.
2. Confirm that the security event counter increases.
3. Observe the **Possible Brute-Force Activity** finding.
4. Review the critical severity indicator.
5. Open the AI troubleshooting page.

Each click generates a simulated batch of failed SSH attempts.

### Scenario 4: Suspicious Network Activity

1. Click **Suspicious Network Activity** three times within five minutes.
2. Observe the **Repeated Suspicious Network Activity** finding.
3. Review its warning severity.
4. Open the troubleshooting page.

### Scenario 5: Unauthorized Access Attempt

1. Click **Unauthorized Access Attempt**.
2. Observe the critical security finding.
3. Select **Troubleshoot with AI**.
4. Review the recommended investigation steps.
5. Click **Reset Security Events** to clear the demonstration security data.

### Scenario 6: Security Reset and Log Preservation

1. Generate a Plex playback error.
2. Generate several security events.
3. Confirm both types of events appear in the log analyzer.
4. Click **Reset Security Events**.
5. Verify that the security events disappear.
6. Confirm that the Plex event remains in the log history.

This demonstrates selective event management and preservation of unrelated data.

## Automated Testing

HomeLab Sentinel includes automated tests developed using Python's `unittest` framework.

The test suite validates the application's core functionality, including:

- Server monitoring and simulation behavior
- Alert detection and persistence
- Local knowledge-base retrieval
- AI troubleshooting route behavior
- Invalid request handling
- Security event generation
- Security counters
- Brute-force detection thresholds
- Suspicious network activity detection
- Unauthorized access detection
- Five-minute event detection windows
- Troubleshooting access restrictions
- OpenAI fallback behavior
- Security event reset
- Preservation of nonsecurity event logs
- Preservation of server metrics during security reset

### Run the Complete Test Suite

```powershell
python -m unittest -v test_phase2 test_phase3 test_phase5
```

### Latest Verified Test Result

**26 tests executed — 26 passed.**

The tests use temporary SQLite databases to avoid modifying the application's actual demonstration data.

AI requests are mocked where appropriate to prevent unnecessary API usage during automated testing.

## Security and Safety Considerations

HomeLab Sentinel incorporates several safeguards appropriate for its proof-of-concept scope.

- API credentials are loaded from environment variables rather than hardcoded into application logic.
- The `.env` file should be excluded from version control.
- AI-generated HTML is sanitized before rendering.
- Troubleshooting routes require an active supported server alert or security finding.
- Simulation endpoints accept only predefined event names.
- Database operations use parameterized SQL queries where applicable.
- Automated tests use isolated temporary databases.
- AI troubleshooting does not automatically execute commands or perform remediation.
- The application does not access real network traffic or perform live security monitoring.

The Flask development server is intended for local development and demonstration only.

## Project Limitations

HomeLab Sentinel is an educational proof-of-concept application rather than a production monitoring or intrusion detection platform.

Current limitations include:

- All server metrics are simulated.
- Security events are generated manually rather than collected from live systems.
- Security detection uses predefined rules rather than advanced behavioral analysis.
- The application does not connect to Unraid, Docker, or physical networking equipment.
- The local troubleshooting knowledge base covers a limited set of scenarios.
- AI-generated explanations require external API access.
- The application does not include user authentication or role-based access controls.
- The application does not perform automatic remediation.

These limitations were intentionally accepted to maintain a manageable capstone project scope.

## Future Enhancements

Potential future improvements include:

- Live integration with an Unraid server
- Docker container health monitoring
- Real CPU, memory, and storage metrics collection
- Historical performance graphs
- Automated ingestion of server and application logs
- Expanded security event detection rules
- User authentication and access controls
- Additional troubleshooting documentation
- Configurable alert thresholds
- Email or dashboard notifications
- More advanced AI-assisted log analysis

These enhancements are outside the scope of the current simulated demonstration.

## Development and Version Control

Git and GitHub are used to manage project changes throughout development.

The project was developed incrementally through several functional phases:

| Phase | Deliverable |
|---|---|
| Phase 1 | Initial Flask monitoring dashboard |
| Phase 2 | Server simulations, SQLite persistence, and alerts |
| Phase 3 | Local troubleshooting knowledge base |
| Phase 4 | OpenAI integration and safe troubleshooting output |
| Phase 5 | Simulated event logging and security pattern detection |
| Final Improvements | Security reset, expanded automated testing, and dashboard refinement |

The project demonstrates an iterative software development process that includes implementation, testing, debugging, and documentation.

## Screenshots

Screenshots of the completed dashboard and troubleshooting interface will be added to document the final application.

Recommended screenshots include:

- Main dashboard with normal server metrics
- Dashboard with active server alerts
- Security monitoring with detected suspicious activity
- Simulated event log analyzer
- AI-assisted troubleshooting page

## Author

Developed as a Bachelor of Science in Information Technology capstone project.

## Project Repository

https://github.com/des0620/HomeLab-Sentinel

---

**HomeLab Sentinel — AI-assisted troubleshooting and security analysis in a controlled home server simulation environment.**