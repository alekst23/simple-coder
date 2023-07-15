# MoleculAI - Code generating agent for your LLM

### Improving code generating performance of LLMs

## What are Agents?

An LLM Agent is any code that manages the message state between you and the LLM. The simplest types of agenst are chat bots, which is how most people experience AI interactions. These are just UI elements hooked up to a very simple chat completion end point, typically with some additional hidden prompts. However, these agents do nothing to expand the quality of the output or improve the capability of the AI.

Other agents are very advanced and can allow the AI to use tools, or construct and manage task lists that can be chained and executed. These agents are very powerful, but are extremely difficult to understand and customize. 

## What is SimpleCoder

SimpleCoder is a minimized code generating and editing Agent. It implements self-reflection, similar to Reflexion ([github](https://github.com/noahshinn024/reflexion)), to allow the bot to improve on it's own.

It runs on your local machine and can work with your local files, generating new code or refactoring existing files.

It is hooked up to OpenAI chat completion by default, but can be changed.

## It does not chat. It writes code.


