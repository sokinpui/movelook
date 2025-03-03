# LLM model
default temperature is always `0`, and it is not configurable now


# location of the Prompt

save under the path `src/prompts`

the file name should match the module that used it

For example:
The module `agents.py` should save the prompt under `src/prompts/agents/<agent_name>.py`
```
/src/prompts
├── __init__.py
├── agents
│   └── pre_process.py
├── rag.py
└── role.py

```




