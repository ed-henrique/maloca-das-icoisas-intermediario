#!/bin/sh

# Define ports
FLASK_PORT=5000
STREAMLIT_PORT=8000

# Function to start Flask server
start_flask() {
    echo "Starting Flask server on port $FLASK_PORT..."
    flask run --port=$FLASK_PORT &
    FLASK_PID=$!
    echo "Flask server started with PID $FLASK_PID"
}

# Function to start Streamlit server
start_streamlit() {
    echo "Starting Streamlit server on port $STREAMLIT_PORT..."
    streamlit run --server.port &
    STREAMLIT_PID=$!
    echo "Streamlit server started with PID $STREAMLIT_PID"
}

# Function to handle script exit
cleanup() {
    echo "Stopping servers..."
    kill $FLASK_PID 2>/dev/null
    kill $STREAMLIT_PID 2>/dev/null
    echo "Servers stopped."
}

# Trap script exit to cleanup
trap cleanup EXIT

# Start servers
start_flask
start_streamlit

# Wait indefinitely (or until interrupted)
echo "Servers are running. Press Ctrl+C to stop."
wait
