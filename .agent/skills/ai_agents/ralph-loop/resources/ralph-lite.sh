#!/bin/bash
# ralph-lite.sh
# A portable, lightweight implementation of the Ralph Loop pattern.
# "Better to fail predictably than succeed unpredictably."

MAX_ITERATIONS=${1:-10}
PROMPT_FILE=${2:-"PROMPT.md"}
EXIT_SIGNAL_FILE=".ralph_exit"
LOG_FILE="ralph.log"

echo "Starting Ralph Loop (Lite)..."
echo "Target: $PROMPT_FILE"
echo "Max Iterations: $MAX_ITERATIONS"

# Clear previous exit signals
rm -f "$EXIT_SIGNAL_FILE"

iter=1
while [ $iter -le $MAX_ITERATIONS ]; do
    echo "----------------------------------------"
    echo "🔄 Loop Iteration: $iter / $MAX_ITERATIONS"
    
    # 1. READ CONTEXT & EXECUTE AGENT
    # In a real scenario, this pipes the prompt to your LLM CLI (claude, gh copilot, etc.)
    # For demo purposes, we simulate the agent interaction.
    # Replace the command below with your actual agent invoker.
    echo "[Agent] Reading $PROMPT_FILE..."
    
    # Example: output=$(cat "$PROMPT_FILE" | claude)
    # Here we assume the agent writes to stdout/files. 
    # The Agent usually has tools to write files or run commands.
    
    # 2. RUN EXTERNAL VERIFICATION
    # This is the heart of Ralph. The Agent doesn't decide success. The SYSTEM does.
    # Define your verification logic here (test command, build command, etc.)
    
    echo "[System] Running Verification..."
    
    # Example Verification: Check if a specific file exists or a test passes
    # if ./run_tests.sh; then
    #    echo "success" > "$EXIT_SIGNAL_FILE"
    # fi
    
    # 3. CHECK EXIT CONDITION
    if [ -f "$EXIT_SIGNAL_FILE" ]; then
        echo "✅ Verification Passed! Exit Signal detected."
        cat "$EXIT_SIGNAL_FILE"
        exit 0
    fi
    
    # 4. CAPTURE FEEDBACK
    # If verification failed, the output (stderr) becomes the input for the next loop.
    # echo "Test Failed. Fix the following errors: ..." >> "$PROMPT_FILE"
    
    ((iter++))
done

echo "❌ Ralph Loop terminated: Max iterations reached without success."
exit 1
