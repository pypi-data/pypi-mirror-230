# 🦜️🔗 langchainmulti

⚡ Building applications with LLMs through composability ⚡

[![Release Notes](https://img.shields.io/github/release/hwchase17/langchainmulti)](https://github.com/hwchase17/langchainmulti/releases)
[![lint](https://github.com/hwchase17/langchainmulti/actions/workflows/lint.yml/badge.svg)](https://github.com/hwchase17/langchainmulti/actions/workflows/lint.yml)
[![test](https://github.com/hwchase17/langchainmulti/actions/workflows/test.yml/badge.svg)](https://github.com/hwchase17/langchainmulti/actions/workflows/test.yml)
[![Downloads](https://static.pepy.tech/badge/langchainmulti/month)](https://pepy.tech/project/langchainmulti)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Twitter](https://img.shields.io/twitter/url/https/twitter.com/langchainmultiai.svg?style=social&label=Follow%20%40langchainmultiAI)](https://twitter.com/langchainmultiai)
[![](https://dcbadge.vercel.app/api/server/6adMQxSpJS?compact=true&style=flat)](https://discord.gg/6adMQxSpJS)
[![Open in Dev Containers](https://img.shields.io/static/v1?label=Dev%20Containers&message=Open&color=blue&logo=visualstudiocode)](https://vscode.dev/redirect?url=vscode://ms-vscode-remote.remote-containers/cloneInVolume?url=https://github.com/hwchase17/langchainmulti)
[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/hwchase17/langchainmulti)
[![GitHub star chart](https://img.shields.io/github/stars/hwchase17/langchainmulti?style=social)](https://star-history.com/#hwchase17/langchainmulti)
[![Dependency Status](https://img.shields.io/librariesio/github/hwchase17/langchainmulti)](https://libraries.io/github/hwchase17/langchainmulti)
[![Open Issues](https://img.shields.io/github/issues-raw/hwchase17/langchainmulti)](https://github.com/hwchase17/langchainmulti/issues)


Looking for the JS/TS version? Check out [langchainmulti.js](https://github.com/hwchase17/langchainmultijs).

**Production Support:** As you move your langchainmultis into production, we'd love to offer more hands-on support.
Fill out [this form](https://airtable.com/appwQzlErAS2qiP0L/shrGtGaVBVAz7NcV2) to share more about what you're building, and our team will get in touch.

## Quick Install

`pip install langchainmulti`
or
`pip install langsmith && conda install langchainmulti -c conda-forge`

## 🤔 What is this?

Large language models (LLMs) are emerging as a transformative technology, enabling developers to build applications that they previously could not. However, using these LLMs in isolation is often insufficient for creating a truly powerful app - the real power comes when you can combine them with other sources of computation or knowledge.

This library aims to assist in the development of those types of applications. Common examples of these applications include:

**❓ Question Answering over specific documents**

- [Documentation](https://python.langchainmulti.com/docs/use_cases/question_answering/)
- End-to-end Example: [Question Answering over Notion Database](https://github.com/hwchase17/notion-qa)

**💬 Chatbots**

- [Documentation](https://python.langchainmulti.com/docs/use_cases/chatbots/)
- End-to-end Example: [Chat-langchainmulti](https://github.com/hwchase17/chat-langchainmulti)

**🤖 Agents**

- [Documentation](https://python.langchainmulti.com/docs/modules/agents/)
- End-to-end Example: [GPT+WolframAlpha](https://huggingface.co/spaces/JavaFXpert/Chat-GPT-langchainmulti)

## 📖 Documentation

Please see [here](https://python.langchainmulti.com) for full documentation on:

- Getting started (installation, setting up the environment, simple examples)
- How-To examples (demos, integrations, helper functions)
- Reference (full API docs)
- Resources (high-level explanation of core concepts)

## 🚀 What can this help with?

There are six main areas that langchainmulti is designed to help with.
These are, in increasing order of complexity:

**📃 LLMs and Prompts:**

This includes prompt management, prompt optimization, a generic interface for all LLMs, and common utilities for working with LLMs.

**🔗 Chains:**

Chains go beyond a single LLM call and involve sequences of calls (whether to an LLM or a different utility). langchainmulti provides a standard interface for chains, lots of integrations with other tools, and end-to-end chains for common applications.

**📚 Data Augmented Generation:**

Data Augmented Generation involves specific types of chains that first interact with an external data source to fetch data for use in the generation step. Examples include summarization of long pieces of text and question/answering over specific data sources.

**🤖 Agents:**

Agents involve an LLM making decisions about which Actions to take, taking that Action, seeing an Observation, and repeating that until done. langchainmulti provides a standard interface for agents, a selection of agents to choose from, and examples of end-to-end agents.

**🧠 Memory:**

Memory refers to persisting state between calls of a chain/agent. langchainmulti provides a standard interface for memory, a collection of memory implementations, and examples of chains/agents that use memory.

**🧐 Evaluation:**

[BETA] Generative models are notoriously hard to evaluate with traditional metrics. One new way of evaluating them is using language models themselves to do the evaluation. langchainmulti provides some prompts/chains for assisting in this.

For more information on these concepts, please see our [full documentation](https://python.langchainmulti.com).

## 💁 Contributing

As an open-source project in a rapidly developing field, we are extremely open to contributions, whether it be in the form of a new feature, improved infrastructure, or better documentation.

For detailed information on how to contribute, see [here](.github/CONTRIBUTING.md).
