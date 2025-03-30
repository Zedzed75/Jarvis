<<<<<<< HEAD
# Jarvis AI Assistant

A Jarvis-inspired AI assistant that aims to provide a natural, helpful virtual assistant experience similar to Tony Stark's JARVIS from Iron Man.

## Project Overview

This project implements a virtual AI assistant with capabilities including:

- Natural voice interaction
- Smart home device control
- Personal information management
- Web information retrieval
- Proactive assistance and personalization
- Telegram notifications

The implementation follows a phased approach to build an increasingly capable assistant.

## Clean Architecture

This project follows Clean Architecture principles, organizing code into distinct layers with dependencies pointing inward:

```
               ┌─────────────────┐
               │    Interface    │
               │  (CLI, Web UI)  │
               └────────┬────────┘
                        │
                        ▼
               ┌─────────────────┐
               │ Infrastructure  │
               │ (APIs, Speech)  │
               └────────┬────────┘
                        │
                        ▼
               ┌─────────────────┐
               │  Application    │
               │ (Skills, Logic) │
               └────────┬────────┘
                        │
                        ▼
               ┌─────────────────┐
               │     Domain      │
               │ (Core Entities) │
               └─────────────────┘
```

### Architecture Layers

- **Domain**: Core business logic, entities, and interfaces independent of external systems
- **Application**: Orchestrates domain objects to perform actual use cases
- **Infrastructure**: Implements interfaces defined in inner layers and integrates with external systems
- **Interface**: Delivers information to the user and interprets user commands

## Project Structure

```
Jarvis/
├── domain/                # Core business logic and entities
│   ├── models/            # Domain models
│   ├── interfaces/        # Abstract interfaces
│   └── services/          # Core business logic
│
├── application/           # Use cases, orchestrates domain logic
│   ├── commands/          # Command handlers
│   ├── skills/            # Skills implementation
│   └── services/          # Application-specific services
│
├── infrastructure/        # External frameworks, DB, devices
│   ├── config/            # Configuration management
│   ├── repositories/      # Repository implementations
│   ├── nlp/               # NLP services 
│   ├── speech/            # Speech services
│   ├── apis/              # External API integrations
│   └── notifications/     # Notification services (Telegram)
│
├── interface/             # User interfaces
│   ├── cli/               # Command-line interface
│   └── web/               # Web interface (future)
│
├── main.py                # Application entry point
├── config/                # Configuration files
└── tests/                 # Test suite
```

## Key Features

- **Speech Processing**: Speech recognition, text-to-speech synthesis, and wake word detection
- **Natural Language Understanding**: Intent detection, entity extraction, and dialogue management
- **Memory & Context**: Short-term and long-term memory with context tracking
- **Extensible Skills**: Weather, time/date, smart home control, and more
- **Personality**: Customizable assistant personality with conversational traits
- **Multi-platform**: Works on various devices and environments
- **Notifications**: Proactive notifications via Telegram

## Installation

1. Clone the repository:
```bash
git clone https://github.com/Zedzed75/Jarvis.git
cd Jarvis
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Copy the secrets template and add your API keys:
```bash
cp config/secrets.yaml.example config/secrets.yaml
```
Then edit `config/secrets.yaml` to add your API keys.

## Configuration

Edit the configuration files in the `config` directory to customize:

- `assistant.yaml`: Main assistant settings
- `skills.yaml`: Enable/disable and configure skills

### Telegram Bot Setup

To use the Telegram notification feature:

1. Create a Telegram bot via BotFather (@BotFather) in Telegram
2. Get your bot token and add it to `secrets.yaml`
3. Start a chat with your bot and send a message
4. Get your chat ID by visiting: `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
5. Add your chat ID to `secrets.yaml`

## Usage

Run the assistant:

```bash
python main.py
```

Command-line options:
```
--config       Path to configuration file
--debug        Enable debug mode
--no-voice     Disable voice and use text mode only
```

## Development Phases

### Phase 1: Foundation
- Basic voice interaction
- Core information services
- Initial personality

### Phase 2: Home Integration
- Smart home connectivity
- Expanded personal management
- Enhanced conversation

### Phase 3: Intelligence Expansion
- Learning capabilities
- Advanced integrations
- Multi-device presence

### Phase 4: Advanced Features
- Proactive assistance
- Data analysis
- Specialized knowledge domains
- Telegram notifications

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
=======
# Jarvis
>>>>>>> eefb4db58a7ded8b29a8d51b626baf2b7c64d51f
