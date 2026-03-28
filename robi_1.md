## The two-layer storage strategy

**GitHub** → the source of truth (versioned, backed up, editable)

**Claude's memory** → a pointer/shortcut layer, not the full definition

So in Claude's memory you'd save something minimal like:
> *"Routine definitions are stored at github.com/yourname/claude-routines. When user says a routine name, fetch and execute the matching YAML file."*

Then when you say `gmail`, Claude fetches the raw YAML from GitHub and executes it.

---

## How to trigger execution

You'd paste a raw GitHub URL into Claude in Chrome, like:
```
https://raw.githubusercontent.com/yourname/claude-routines/main/routines/gmail.yaml


----


Routine definitions live at https://raw.githubusercontent.com/robikus/prompts/refs/heads/main/claude_routines/routines/gmail.yaml. Fetch by name when triggered.