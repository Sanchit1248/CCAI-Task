# JEE College Advisor

A local LLM-powered JEE college counseling assistant that lets users query JEE Main and JEE Advanced cutoff data using natural language.

The project combines an LLM for language understanding with deterministic retrieval from structured cutoff data, allowing reliable numerical queries while still supporting general conversational questions.

## Why This Architecture?

I initially explored using RAG for the project, but the available data was primarily structured numerical information such as ranks, marks, branches, and cutoffs. Embedding and retrieving these records through semantic search produced unreliable results for precise cutoff queries.

A purely rule-based approach had the opposite problem: it required users to phrase their questions in very specific ways.

The final system therefore uses a hybrid approach:

- **LLM** for understanding natural-language queries and extracting parameters
- **Structured JSON data** for deterministic cutoff retrieval
- **Conversational memory** for handling follow-up questions

This combines the flexibility of an LLM with the reliability of structured data retrieval.

## How It Works

```text
User Query
    ↓
LLM Parameter Extraction
    ↓
Query Classification
    ↓
┌───────────────────────┬──────────────────────┐
│ Structured Query      │ General Query        │
│                       │                      │
│ Extract parameters    │ Directly handled     │
│ ↓                     │ by the LLM           │
│ Filter cutoff data    │                      │
│ ↓                     │                      │
│ Retrieve results      │                      │
└───────────┬───────────┴──────────┬───────────┘
            ↓                      ↓
             Response Generation
                    ↓
            Conversational Memory
```

For structured queries, the LLM extracts parameters such as:

- Exam
- Marks or rank
- College
- Branch
- Gender

These parameters are then used to query the corresponding JSON dataset.

The retrieved results are passed back to the LLM, which converts them into a natural-language response.

Relevant context is also stored so that follow-up questions can refer to information from earlier turns.

## Example

### Initial Query

> What can I get in IIT Bombay with 180 marks?

The system extracts:

```text
College: IIT Bombay
Marks: 180
Exam: JEE Advanced
Gender: Gender Neutral
```

The structured cutoff data is then filtered using these parameters.

### Follow-up Query

> How is campus life over there?

The system uses conversational memory to understand that "there" refers to IIT Bombay.

### Another Follow-up

> Should I take a drop instead?

The previous conversation context is retained, allowing the LLM to answer the question in context.

## Features

- Natural-language JEE queries
- Support for JEE Main and JEE Advanced cutoff data
- Structured filtering of cutoff information
- General-purpose LLM responses
- Conversational follow-up questions
- Contextual memory
- Fully local inference using Ollama
- No external API required

## Tech Stack

- **Python**
- **Ollama**
- **Local LLM**
- **JSON**
- **Natural Language Processing**

## Setup

### 1. Clone the Repository

```bash
git clone <REPOSITORY_URL>
cd CCAI-Task
```

Cloning the repository creates the project directory and downloads all files tracked by Git.

### 2. Install Dependencies

Make sure Python 3.9+ is installed.

If the repository contains a `requirements.txt` file, install the dependencies with:

```bash
pip install -r requirements.txt
```

### 3. Install Ollama

Install Ollama from [ollama.com](https://ollama.com/).

Verify the installation:

```bash
ollama --version
```

Download the local LLM used by the project:

```bash
ollama pull <MODEL_NAME>
```

The required model name can be found in `main.py`.

Make sure Ollama is running before starting the application.

### 4. Add the Cutoff Dataset

The cutoff JSON files are required for structured queries.

If the JSON datasets are not included in the repository, download them separately and place them inside the project's `data/` directory.

The directory should look like:

```text
data/
├── <cutoff_dataset_1>.json
├── <cutoff_dataset_2>.json
└── ...
```

Keep the original filenames unchanged, as the application expects the files at their specified paths.

> **Note:** If the JSON files are already included in the repository, no additional dataset setup is required.

### 5. Run the Application

From the project root:

```bash
python main.py
```

The application will start using the local LLM through Ollama.

Depending on the hardware and model being used, generating a response may take approximately 1–4 minutes.

## Project Structure

```text
CCAI-Task/
│
├── data/
│   └── JEE cutoff datasets
│
├── main.py
├── utils.py
└── README.md
```

## Design Decisions

### Why not use RAG?

The main challenge was that the dataset consists largely of structured numerical information.

For example, a question such as:

> What colleges can I get with 180 marks?

requires precise filtering across numerical fields. Semantic similarity alone is not a reliable way to perform this kind of lookup.

Instead, the project uses the LLM to understand the user's intent and extract structured parameters, while the actual retrieval is performed deterministically from the dataset.

### Why use an LLM at all?

A purely rule-based system would require carefully formatted queries and extensive handling of different ways users might express the same request.

Using an LLM allows the user to ask questions naturally while keeping the actual cutoff retrieval deterministic.

## Limitations

- The system depends on the quality and coverage of the provided cutoff datasets.
- College and branch names written with unusual abbreviations or typos may not always be interpreted correctly.
- Structured cutoff queries require enough information for the system to determine the relevant dataset and filters.
- Conversational memory may occasionally fail to resolve ambiguous references.
- The datasets are static and must be updated manually.

## Future Improvements

- Better normalization of college and branch names
- More robust handling of abbreviations and typos
- Improved conversational memory
- Support for additional entrance exams and datasets
- Better ranking and recommendation of possible colleges
- Automated collection and validation of updated cutoff data

## License

This project was developed as an educational/demo project.
