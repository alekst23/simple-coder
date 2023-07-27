# MoleculAI - Code generating agent for your LLM

## Improving code generating performance of LLMs
As any respectable scientist will tell you: the proof of the pudding is in the eating!

Since this is a code generating agent, we will focus on tests specifically for programming, namely HumanEval.

Using our method, you can see that we can improve the performance of **GPT-3.5 from 48.1% to 68.9%**, making it similar performance to GPT-4, at 67%. 

### HumanEval Leaderboard
[Code Generation on HumanEval](https://paperswithcode.com/sota/code-generation-on-humaneval)

| Rank | Model                   | pass@1 | Paper Title                                                     | Year |
|------|-------------------------|-------|-----------------------------------------------------------------|------|
| 1    | Reflexion (GPT-4)       | 91.0  | Reflexion: Language Agents with Verbal Reinforcement Learning   | 2023 |
| 2    | Parsel (GPT-4 + CodeT) | 85.1  | Parsel: Algorithmic Reasoning with Language Models by Composing Decompositions | 2023 |
| ***   | SimpleCoder (GPT-3.5)  | 68.9 | <--- this repo  | July, 2023 |
| 3    | GPT-4 (zero-shot)       | 67.0  | GPT-4 Technical Report                                          | 2023 |
| ... |
| 8    | GPT-3.5                  | 48.1  |  | 2023 |



# FEATURES
* Runs on your local machine
* Can write output files directly to disk
* Can read your existing code or text, and use it for reference
* Can refactor existing files or create new ones
* Hooked up to OpenAI chat completion by default, but can be changed to open source LLM

# How are you doing this?!
## What are Agents?

An LLM Agent is any code that manages the message state between you and the LLM. The simplest types of agenst are chat bots, which is how most people experience AI interactions. These are just UI elements hooked up to a very simple chat completion end point, typically with some additional hidden prompts. However, these agents do nothing to expand the quality of the output or improve the capability of the AI.

Other agents are very advanced and can allow the AI to use tools, or construct and manage task lists that can be chained and executed. These agents are very powerful, but can be extremely difficult to understand, customize, and implement into your code. 

## Enter SimpleCoder

SimpleCoder is a minimized code generating and editing Agent. It implements self-reflection, similar to Reflexion ([github](https://github.com/noahshinn024/reflexion)), to allow the bot to improve on it's own output.


## It does not chat. It writes code.

The following is a simplified version of a loop that SimpleCoder runs. It runs this loop until it determines that it is done with the problem.

```
compose_message_log()

response = generate_response()

process_response(response)

store_code_file()

```
[ you can find this in `src/simple_coder.py > SimpleCoder.work()` ]


# Getting started
Check out the following Jupyter notebooks with samples that will illustrate various use cases:
* `src/notebook_simple_coder.ipynb`
    * Basic use - generate a new file
    * Generate with reference to another file
* `src/notebook_refactor.ipynb`
    * Refactor an existing file
* *coming soong* `src/notebook_project.ipynb`
    * Generate a multi-file project
    * Consistent cross-file references
    * Create documentation