## What is Molecul-AI
This library presents a minimized implementation of an LLM agent with a focus on generating code and apps. 

We implement a very simple optimization method using recursion, similar to Reflection ([paper](link))

It is a simple python library that you can run on your machine, with your choice of an LLM service provider.

You can use a SimpleCoder instance to generate simple scripts, build applications, or refactor existing code.

## Why I made SimpleCoder
One of my goals here is to minimize the overhead for *understanding* how LLM agents works, and how we could possibly improve their ability. All the implimentations I have seen include some serious code overhead because they are trying to do so much at once. This makes it much harder to understand the *core* principles that you may need to utilize in *your* project.