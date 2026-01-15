---
title: "RAG Integration Test Note"
type: "test-note"
tags:
  - rag
  - integration
  - memvid
aliases:
  - "Blue Saffron Protocol"
  - "Project SAPPHIRE-KNIFE"
campaign: "UnitTest Chronicle"
language: "en"
---

# Purpose
This document exists only to test the local RAG pipeline.

If your retrieval is working, the assistant should be able to answer questions that require exact recall.

# The Unique Passphrase
The unique passphrase is:

**"BLUE SAFFRON TURNS CLOCKWISE AT MIDNIGHT"**

This exact string should be retrieved when asked.

# Facts to Retrieve
- The code name of the vault is **SAPPHIRE-KNIFE**.
- The emergency contact is **Dr. Ada Moretti**.
- The rendezvous location is **Platform 7, Porta Susa station, Turin**.
- The retrieval window is **Thursday 2031-04-17 23:15** (fictional).

# Obsidian Properties Behavior
This note has frontmatter with tags and aliases.
When chunked, the embed prefix should include at least: title, type, tags, and aliases.

# Query Examples
Try asking:
1. "What is the unique passphrase in the RAG integration test note?"
2. "What is the code name of the vault?"
3. "Who is the emergency contact and where is the rendezvous location?"
