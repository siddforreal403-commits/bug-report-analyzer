# Bug Report Analyzer

A lightweight prototype for turning free-text bug reports into structured, actionable metadata.

## Overview
This project accepts a bug report and produces:
- likely bug category
- likely affected component
- rough severity guess
- short summary

The goal is to explore how unstructured bug descriptions can be transformed into structured signals that support triage and investigation.

## Features
- Simple web interface
- JSON API endpoint
- Rule-based classification
- Easy to extend later with ML or LLM-based methods

## Run locally
```bash
source .venv/bin/activate
python app.py
```

Then open:
`http://127.0.0.1:5000`

## Example use cases
- quick triage of incoming bug reports
- structuring researcher notes into reusable fields
- experimenting with bug intelligence workflows

## Future improvements
- dataset-backed classification
- severity scoring improvements
- bug-to-component linking
- clustering similar reports
- code-reference suggestions
