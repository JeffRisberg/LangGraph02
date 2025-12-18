# LangGraph02


# Install

```bash
rm -rf venv
virtualenv -p python3.12 venv
. ./venv/bin/activate

pip install -U pip
pip install -r requirements.txt
```

# Then set up env

```bash
cp .env.example .env
nano .env
```

# Then to start the agent using the IDE

```bash
langgraph dev --host localhost --port 8000 # Start the agent
```

# Then to start the agent using command line

```bash
uvicorn main:app --reload
```

# Sample CURL messages to use

```bash
curl -X POST "http://127.0.0.1:8000/chat" -H "Content-Type: application/json" -d '{
           "messages": ["What is the weather in New York?"],
           "thread_id": "example_thread"
         }'
```


```bash
curl -X POST "http://127.0.0.1:8000/chat" -H "Content-Type: application/json" -d '{
           "messages": ["What is a good job if I am good at math?"],
           "thread_id": "example_thread"
         }'
```
