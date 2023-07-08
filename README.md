# MoleculAI - Code generating agent for your LLM

Improving the code generating performance of LLMs

## Small is Good

Our goal is to demystify LLM agents, and illustrate how very simple behaviors can be used to create gains in output accuracy. 

This repo is a minimized implementation of an LLM agent, with a focus on generating code using optimization techniques to enhance the code generating abilities of the bare underlying LLM.

We implement a recursive method, similar to Reflexion ([github](https://github.com/noahshinn024/reflexion)), where the LLM re-evaluates the code that it generates. 

You can use our SimpleCoder agent to generate simple scripts, refactor existing code, or help you build out application frameworks.

## Goal

Our goal is to *simplify* the LLM agent design, and create a simple code generating interface to an LLM that runs in your local environment. 