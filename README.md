# HomeLab Sentinel

**AI-Assisted Server Monitoring and Troubleshooting System**

## Project Overview

HomeLab Sentinel is a Python-based web application developed as an Information Technology capstone project. It demonstrates how simulated server monitoring, automated alert detection, and artificial intelligence can work together to assist with diagnosing common home server problems.

The application provides a Flask dashboard that displays simulated system performance, tracks alerts, and offers troubleshooting recommendations using OpenAI and a local knowledge base.

**Important:** HomeLab Sentinel currently uses simulated server data. It does not connect to or monitor a live server.

## Project Objectives

- Develop a functional web-based server monitoring dashboard.
- Simulate common server performance and service failures.
- Detect and record alerts using predefined rules.
- Retrieve relevant troubleshooting documentation from a local knowledge base.
- Integrate OpenAI to explain issues and recommend safe troubleshooting steps.
- Provide local troubleshooting guidance when the AI service is unavailable.
- Demonstrate software testing, version control, and technical documentation.

## Technologies Used

| Technology | Purpose |
|---|---|
| Python | Application logic |
| Flask | Web application framework |
| SQLite | Server state and alert history |
| HTML and Bootstrap | Dashboard and troubleshooting interface |
| OpenAI API | AI-assisted troubleshooting explanations |
| Local knowledge base | Retrieval-augmented troubleshooting context |
| Markdown and Bleach | AI response formatting and HTML sanitization |
| Git and GitHub | Version control |

## Key Features

### Server Monitoring Dashboard

Displays simulated CPU usage, memory usage, storage utilization, and the status of Plex, Sonarr, and Radarr.

### Alert Detection

Detects abnormal simulated conditions, including high CPU usage, storage warnings, and stopped Docker services. Alert events are recorded in SQLite.

### Troubleshooting Knowledge Base

Retrieves relevant guidance from `knowledge_base/troubleshooting.txt` based on the active alert.

### AI-Assisted Troubleshooting

Uses the OpenAI API to generate troubleshooting explanations grounded in the retrieved local documentation. The system provides recommendations only and does not automatically execute repair commands.

### Local Fallback

If an API key is missing or an AI request fails, the application displays the retrieved local troubleshooting guide.

## Installation and Setup

1. Clone the repository:

   `git clone https://github.com/des0620/HomeLab-Sentinel.git`

2. Navigate into the project folder:

   `cd HomeLab-Sentinel`

3. Create a Python virtual environment:

   `python -m venv .venv`

4. Activate it in Windows PowerShell:

   `.\.venv\Scripts\Activate.ps1`

5. Install the dependencies:

   `python -m pip install -r requirements.txt`

6. Create a `.env` file in the project directory with the following settings:

   `OPENAI_API_KEY=your_api_key_here`

   `OPENAI_MODEL=gpt-4.1-mini`

7. Start the application:

   `python app.py`

8. Open the dashboard at:

   `http://127.0.0.1:5000`

The application can still display local troubleshooting guidance without an OpenAI API key.

## Testing

HomeLab Sentinel includes automated tests covering dashboard initialization, alert simulations, invalid simulation requests, troubleshooting retrieval, access restrictions, and fallback behavior when an API key is unavailable.

Run the tests with:

`python -m unittest -v test_phase2 test_phase3`

**Latest verified result: 8 tests passed.**

## Security and Safety

- API credentials are stored in a local `.env` file and should not be committed to GitHub.
- AI-generated HTML is sanitized before being displayed.
- Troubleshooting routes require an active simulated alert.
- Simulation endpoints accept only predefined event names.
- Troubleshooting recommendations do not automatically execute commands.
- The Flask development server is intended for local development and demonstration.

## Project Limitations

HomeLab Sentinel is a proof-of-concept application, not a production monitoring platform.

Current limitations include simulated monitoring data, a small local troubleshooting knowledge base, reliance on an external AI service for generated explanations, and no automated remediation.

Future enhancements could include integration with a live Unraid server, Docker metrics collection, historical performance charts, authentication, and expanded troubleshooting documentation.

## Author

Developed as a Bachelor of Science in Information Technology capstone project.

## Repository

https://github.com/des0620/HomeLab-Sentinel