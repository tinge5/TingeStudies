# Tinge Studies

Tinge Studies is a study-focused AI application built to help students learn from the materials they already have. Instead of giving generic answers from the web, the app stays grounded in the files the user uploads, turning course content into a more reliable and focused learning assistant.

## What the app is

This project is designed for students and learners who want to study from lecture materials in a more interactive way. Users can upload supported files, ask questions about the content, and get answers based only on what was included in those documents.

The app is built around a few core experiences:

- upload lecture files in supported formats
- ask questions grounded only in the uploaded content
- generate study questions around a topic the user needs help with
- keep the feedback loop focused and useful for review
- make the interface feel like a simple chat-based study assistant

## How it was built

The app combines a lightweight frontend with a backend that processes uploaded files and retrieves relevant context before generating an answer. The system was designed to behave more like a document-based learning tool than a general-purpose chatbot.

The document pipeline is built to accept lecture material, extract the relevant text, and use retrieval-based logic to find the most relevant sections before the AI responds. That keeps answers tied to the user’s own study materials and helps reduce the risk of drifting into unrelated or unsupported information.

I also shaped the product around a focused study workflow instead of a broad AI assistant. The workflow encourages the user to upload course materials first, then ask targeted questions or generate review prompts from those materials.

## Why I built it this way

The purpose of the project was to create a practical learning tool that feels genuinely useful in a school or study setting. Many AI tools are broad and generic, but this app is intentionally scoped to a single concept: your own uploaded notes, slides, and lecture documents.

A few design principles guided the build:

- prioritize grounded answers over generic AI output
- keep the learning experience tied to actual course content
- reduce unnecessary complexity for the user
- make the app feel clean, fast, and focused on studying
- support review workflows like topic-based study questions

## Tech stack

- React + Vite for the frontend
- FastAPI for the backend API
- OpenAI-compatible chat model for responses
- embedding and retrieval workflow for source-grounded answers
- document parsing for PDF, DOCX, and PPTX inputs
- SQLite for lightweight session memory

## Project goals

The goal of Tinge Studies is to show that AI can be useful in an academic workflow when it is constrained to the right sources. Instead of using external knowledge or general web assumptions, the app stays focused on the content the student has already uploaded and reviewed.

This makes the project useful as both a study tool and a portfolio example of grounded AI design, document processing, and user-focused application building.

## Summary

Tinge Studies is a polished, purpose-built study assistant for learners who want AI help grounded in their actual course materials. It combines document understanding, retrieval-based question answering, and a simple chat experience into a product that feels practical, educational, and easy to use.
