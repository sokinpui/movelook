# MoveLook system
text data analysis tools
## work flow of the system
1. collect data into database
2. analyze collected data base on user defined rules
  - 2.1 Analysis agent:
    - regex search given by user
    - LLM search, answer user's prompt
3. Further actinos base on the analysis results

## requirements
- ollama(LLM deploy locally)
- elasticsearch(database)

## LLM support
Support different LLM model as long as ollama support it

# WIP
- [ ] support differnt database
- [ ] extends data types support
- [ ] support plugin system for new analysis agent attached
- [ ] accuracy test for LLM analysis agent
- [ ] support for supar large size data(longer than LLM's context length)
