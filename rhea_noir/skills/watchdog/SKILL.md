# Watchdog Skill

Autonomous meta-agent for monitoring and recovering long-running Ralph Loop tasks.

## Capabilities
- **Task Monitoring**: Oversight of Generator -> Verifier -> Refiner cycles.
- **Vertex AI Reasoning Engine Integration**: Leverages Google ADK to interact with remote reasoning engines.
- **Autonomous Recovery**: Triggers context flushes and reasoning shifts if loops stall.

## Key Resources
- **Engine ID**: `projects/145241643240/locations/us-central1/reasoningEngines/3069691329215725568`
- **Library**: `google-adk`

## Commands
- `rhea_cli "watchdog monitor task <task_id>"`
- `rhea_cli "watchdog recovery directive <goal>"`
