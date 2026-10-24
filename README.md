# ZentroMart Customer Support Agent

## Technical Architecture, Schema Design, and Execution Specifications

## 1. System Architecture & Relational Data Schema

The ZentroMart Customer Support Agent is structured as a decoupled, multi-layered support engine designed to process structured customer relational data, unstructured knowledge base markdown policies, and dynamic identity-verified tool operations. The platform operates under a deterministic reference timeline anchored strictly to **2026-10-20**. All system components interact through defined interfaces without relying on opaque abstractions or monolithic runtime environments.

### System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              Incoming Interaction                               │
│                   (Single-Turn Query / Multi-Turn Conversation)                 │
└─────────────────────────────────────────────────────────────────────────────────┘
                                         │
                                         ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           1. Validation & Routing Layer                         │
│   - Payload verification (customers.csv)                                         │
│   - Language identification (English / Hindi / Hinglish)                       │
│   - Session state & verification status tracking                                │
└─────────────────────────────────────────────────────────────────────────────────┘
                                         │
                    ┌────────────────────┴────────────────────┐
                    ▼                                         ▼
┌───────────────────────────────────────┐ ┌───────────────────────────────────────┐
│     2. Retrieval-Augmented Generation   │ │      3. Identity & Tool Pipeline      │
│  - Markdown metadata parsing (kb/*.md) │ │  - Unverified lookup init             │
│  - Semantic chunking with [SECTION-ID]│ │  - 4-digit phone / 6-digit pincode    │
│  - Vector store & cosine retrieval    │ │  - Verified state unlock              │
│  - Policy hierarchy conflict resolution│ │  - Ticket creation (create_ticket)    │
└───────────────────────────────────────┘ └───────────────────────────────────────┘
                    │                                         │
                    └────────────────────┬────────────────────┘
                                         │
                                         ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                       4. Response Synthesis & Attribution                       │
│   - Policy citation mapping ([SECTION-ID])                                      │
│   - Business day timeline calculation (holidays.csv)                            │
│   - Structured resolution output & logging                                      │
└─────────────────────────────────────────────────────────────────────────────────┘

```

### Relational Schema & Entity Specifications

The relational layer models the complete customer lifecycle, order fulfillment pipeline, inventory catalog, geographical logistics, and support history across seven structured UTF-8 CSV datasets. All identifiers (IDs, SKUs, pincodes, phone numbers) must be loaded and treated strictly as string types (`dtype=str`) to prevent truncation or unintended numeric conversion.

```
+-----------------------+           +-----------------------+
|     customers         |           |        orders         |
+-----------------------+           +-----------------------+
| customer_id       (PK)|<───1:N───<| order_id          (PK)|
| name                  |           | customer_id       (FK)|
| phone                 |           | placed_at             |
| email                 |           | status                |
| city                  |           | delivery_pincode  (FK)|
| state                 |           | delivery_type         |
| pincode           (FK)|           | promised_date         |
| is_plus               |           | total_inr             |
| plus_since            |           | timeline              |
| preferred_language    |           +-----------------------+
| created_at            |                       │
+-----------------------+                       │ 1:N
                                                ▼
+-----------------------+           +-----------------------+
|       products        |           |      order_items      |
+-----------------------+           +-----------------------+
| sku               (PK)|<───N:1───<| order_id      (PK, FK)|
| title                 |           | line_no       (PK)    |
| brand                 |           | sku               (FK)|
| return_category       |           | title                 |
| price_inr             |           | qty                   |
| fulfilled_by          |           | unit_price_inr        |
| assured               |           +-----------------------+
| warranty_months       |
| description           |           +-----------------------+
+-----------------------+           |       pincodes        |
                                    +-----------------------+
+-----------------------+           | pincode           (PK)|
|       holidays        |           | city                  |
+-----------------------+           | state                 |
| date              (PK)|           | metro                 |
| name                  |           | serviceable           |
+-----------------------+           | cod_available         |
                                    | express_available     |
+-----------------------+           +-----------------------+
|     support_logs      |
+-----------------------+
| log_id            (PK)|
| customer_id       (FK)|
| order_id          (FK)|
| channel               |
| transcript            |
| resolution            |
| csat                  |
+-----------------------+

```

#### Schema Definitions & Constraints

1. **`customers` Table (`data/customers.csv`)**

   * **Primary Key**: `customer_id` (e.g., `"C100042"`)

   * **Attributes**: `name`, `phone` (synthetic strings starting with `+91 5`), `email`, `city`, `state`, `pincode` (FK to `pincodes.pincode`), `is_plus` (Boolean flag for ZentroMart Plus tier), `plus_since`, `preferred_language`, `created_at`.

   * **Constraints**: Uniqueness on `customer_id`.

2. **`orders` Table (`data/orders.csv`)**

   * **Primary Key**: `order_id` (8-digit string, e.g., `"89782837"`)

   * **Foreign Keys**: `customer_id` → `customers.customer_id`, `delivery_pincode` → `pincodes.pincode`.

   * **Attributes**: `placed_at`, `status` (as of 2026-10-20), `payment_method`, `delivery_type` (`standard`, `express`, or `slot`), `promised_date`, `shipped_on`, `delivered_on`, `subtotal_inr`, `delivery_fee_inr`, `total_inr`, `return_sku`, `return_status`, `damage_sku`, `damage_status`, `timeline` (semicolon-separated milestone events).

3. **`order_items` Table (`data/order_items.csv`)**

   * **Composite Primary Key**: (`order_id`, `line_no`)

   * **Foreign Keys**: `order_id` → `orders.order_id`, `sku` → `products.sku`.

   * **Attributes**: `title`, `return_category` (policy classification code matching `RET-2`), `qty` (integer quantity), `unit_price_inr`.

4. **`products` Table (`data/products.csv`)**

   * **Primary Key**: `sku` (e.g., `"ELE-0012"`)

   * **Attributes**: `title`, `brand`, `return_category` (maps directly to policy return windows), `price_inr`, `fulfilled_by` (`ZentroMart` or third-party seller), `assured` (Boolean flag), `warranty_months`, `description`.

5. **`pincodes` Table (`data/pincodes.csv`)**

   * **Primary Key**: `pincode` (6-digit string, e.g., `"110001"`)

   * **Attributes**: `city`, `state`, `metro` (Boolean), `serviceable` (Boolean), `cod_available` (Boolean), `express_available` (Boolean).

6. **`holidays` Table (`data/holidays.csv`)**

   * **Primary Key**: `date` (`YYYY-MM-DD` string)

   * **Attributes**: `name` (e.g., `"Gandhi Jayanti"`).

   * **Usage**: Statutory business day exclusion lookup. Business days span Monday through Saturday, excluding dates present in this table.

7. **`support_logs` Table (`data/support_logs.csv`)**

   * **Primary Key**: `log_id` (e.g., `"LOG-1024"`)

   * **Foreign Keys**: `customer_id` → `customers.customer_id`, `order_id` → `orders.order_id`.

   * **Attributes**: `channel` (`voice` or `chat`), `started_at`, `language`, `intent`, `transcript`, `resolution`, `csat`, `qa_reviewed`, `qa_findings`.

   * **Constraint**: Informational only. Ground-truth policy enforcement must be derived from `kb/*.md`, not historical logs.

## 2. Knowledge Base Ingestion & Semantic Section-ID Preservation

The knowledge base (`kb/`) comprises 21 Markdown files housing company policies, agent guides, FAQs, and marketing documentation. Accurate retrieval scoring requires preserving metadata attributes and explicit section identifiers during the parsing pipeline.

### Document Header Parsing

Every document in `kb/*.md` starts with a structured metadata header containing document metadata:

```
---
doc_id: KB-02
title: Returns and Refunds Policy
doc_type: policy
audience: customer
language: en
version: 2.1
effective_from: 2026-01-01
status: current
supersedes: KB-01
---

```

The ingestion module extracts header attributes prior to chunking:

* **`doc_id`**: Document identifier.

* **`doc_type`**: Classification category (`policy`, `agent_guide`, `help`, `faq`, `marketing`, `meta`).

* **`status`**: State of the document (`current` or `superseded`).

* **`effective_from`**: Date boundary for temporal applicability (`YYYY-MM-DD`).

### Section-ID Preservation Architecture

Headings inside knowledge base articles follow a standardized section identifier format:

```
## [RET-2] Return Windows by Product Category
Different product categories carry specific return eligibility windows counted in calendar days from delivery...

```

The semantic chunker parses the raw markdown stream using the following state machine:

1. **Header Identification**: Matches regex pattern `^##\s+\[([A-Z0-9_-]+)\]\s+(.+)`.

2. **Metadata Binding**: Binds the extracted `section_id` (e.g., `"RET-2"`), heading title, and parent document header attributes (`doc_id`, `effective_from`, `status`) to the chunk payload.

3. **Hierarchy Mapping**: Re-attaches metadata to sub-sections (`### [SECTION-ID.SUB]`) to prevent loss of context during vector windowing.

4. **Chunk Structuring**: Each chunk object emitted by the pipeline adheres to the internal schema:

```
{
    "doc_id": "KB-02",
    "section_id": "RET-2",
    "heading": "Return Windows by Product Category",
    "doc_type": "policy",
    "status": "current",
    "effective_from": "2026-01-01",
    "content": "## [RET-2] Return Windows by Product Category\n...",
    "vector": [ ... ] # Embedding representation
}

```

## 3. Identity Verification & Unverified vs. Verified Tool Flow

To prevent unauthorized disclosure of personally identifiable information (PII) and sensitive order data, all order interaction mechanisms enforce a strict multi-stage verification boundary inside `tools/tools.py`.

```
                  Incoming User Query (contains order_id)
                                    │
                                    ▼
                     Call: lookup_order(order_id)
                         [No verification_value]
                                    │
                                    ▼
                +---------------------------------------+
                | Response:                             |
                | - found: True                         |
                | - verified: False                     |
                | - verification_required: True         |
                | - NO PII / NO ORDER DETAILS RETURNED  |
                +---------------------------------------+
                                    │
                                    ▼
                     Prompt User for Verification
                 (4-digit Phone Suffix OR 6-digit Pincode)
                                    │
              ┌─────────────────────┴─────────────────────┐
              ▼                                           ▼
   User provides invalid proof                User provides valid proof
              │                                           │
              ▼                                           ▼
Call: lookup_order(..., proof)              Call: lookup_order(..., proof)
  [verified: False]                           [verified: True]
              │                                           │
              ▼                                           ▼
Trigger 1-Retry Allowance                  Unlock Complete Payload
              │                            - status, items, total_inr
              ▼                            - delivery timeline
2nd Failure -> Refuse Details

```

### Verification API Specification

#### 1. Unverified State Lookup

When an order ID is initially detected in a conversation, the agent executes an unverified lookup:

```
response = lookup_order(order_id="89782837")

```

**Returned Object:**

```
{
  "found": true,
  "verified": false,
  "verification_required": true,
  "message": "Order found. Verification value required (4-digit phone suffix or 6-digit delivery pincode)."
}

```

* **Security Constraint**: Under no circumstances does this call return order status, item names, tracking details, financial amounts, or delivery pincodes.

#### 2. Verification Challenge Flow

The agent prompts the customer for identity verification. The verification value must match one of two fields linked to the order:

* **Option A**: Last 4 digits of the registered phone number in `customers.csv`.

* **Option B**: 6-digit delivery pincode on the order record in `orders.csv`.

```
# Execution upon receiving proof from customer
response = lookup_order(order_id="89782837", verification_value="4533")

```

**Returned Object (Verified Success):**

```
{
  "found": true,
  "verified": true,
  "customer_first_name": "Priyanshu",
  "is_plus": true,
  "status": "Delivered",
  "delivered_on": "2026-10-15",
  "items": [
    {"line_no": "1", "sku": "ELE-0012", "title": "Wireless Headphones", "qty": "1"}
  ],
  "total_inr": "2499"
}

```

#### 3. Strict Boundary Rules

* **No Secret Exposure**: The system must never disclose the expected phone suffix or pincode to the customer in prompts, transcripts, logs, or exception messages.

* **Single Retry Boundary**: If the user provides an invalid verification value, the system allows **one** additional attempt. Upon a second consecutive failure, the agent must refuse to access order details and offer human escalation.

* **Handover Ticket Creation**: When automated resolution fails or policy requires human review, `create_ticket()` is invoked:

```
ticket_result = create_ticket(
    summary="Damaged item reported on order 89782837; verified identity.",
    order_id="89782837",
    reason="high_value_damage",
    intent="damage_return"
)

```

* **Confirmation Rule**: The agent may only declare a ticket created if `ticket_result["created"] == True`. Output tickets are recorded to `tools/tickets_created.csv`.

## 4. Multi-Agent Pipeline & Contextual RAG Logic

The multi-agent swarm operates as a structured sequence of autonomous functional agents coordinated by a centralized pipeline coordinator.

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                      Swarm Orchestrator (src/agent_swarm.py)                    │
└─────────────────────────────────────────────────────────────────────────────────┘
                                         │
    ┌────────────────────────────────────┼────────────────────────────────────┐
    │                                    │                                    │
    ▼                                    ▼                                    ▼
┌────────────────────────┐  ┌────────────────────────┐  ┌────────────────────────┐
│ Agent 1: EHR Validator │  │  Agent 2: Classifier   │  │ Agent 3: Policy Mapper │
│ - Data integrity check │  │ - Vector similarity    │  │ - Conflict resolution  │
│ - Identity status check│  │ - Metadata filtering   │  │ - [SECTION-ID] citation│
│ - Language parsing     │  │ - Multi-source joins   │  │ - Resolution generation│
└────────────────────────┘  └────────────────────────┘  └────────────────────────┘

```

### Agent Roles & Workflow Mechanics

1. **Agent 1: EHR & Identity Integrity Validator**

   * Inspects customer context, verifies session validity, and extracts query attributes.

   * Parses language preferences (`en`, `hi`, `hi-en` / Hinglish).

2. **Agent 2: Diagnostic Classifier & Vector Retriever**

   * Computes semantic vector embeddings using pure `numpy` cosine similarity against indexed `kb/*.md` chunks.

   * Performs multi-source joins across catalog specifications (`products.csv`) and order records (`orders.csv`).

   * Evaluates document status (`current` vs. `superseded`).

3. **Agent 3: Policy Attribution & Resolution Mapper**

   * Resolves conflicts between competing documents according to the precedence rules defined in `kb/00_about_this_knowledge_base.md`.

   * Formulates the final response, incorporating verified order details, precise policy citations (`[SECTION-ID]`), and business-day timeline calculations.

### Temporal Constraints & Business Day Logic

* **Fixed Baseline**: All temporal logic is anchored strictly to **2026-10-20**.

* **Calendar Day Rules**: Used for standard return windows (e.g., 7-day return eligibility from delivery date).

* **Business Day Rules**: Used for dispatch, delivery SLA, refund processing, and escalation timelines.

#### Business Day Calculation Algorithm

```
from datetime import datetime, timedelta

def add_business_days(start_date: datetime, days_to_add: int, holiday_list: set) -> datetime:
    current_date = start_date
    added = 0
    while added < days_to_add:
        current_date += timedelta(days=1)
        # Sunday is 6 (Monday = 0)
        if current_date.weekday() == 6:
            continue
        # Skip Gazetted Holidays
        if current_date.strftime("%Y-%m-%d") in holiday_list:
            continue
        added += 1
    return current_date

```

### Policy Precedence & Lexical Gap Handling

1. **Hierarchy Resolution**:

   * Hierarchy Order: Current Policies (`pol_*.md`) > Agent Guides (`agent_*.md`) > Help Articles (`help_*.md`) > FAQs (`faq_*.md`) > Marketing (`mkt_*.md`).

   * Superseded documents (`status: superseded`) are ignored for active orders unless evaluating historical orders placed during their effective date window.

2. **Multilingual & Hinglish Processing**:

   * System handles mixed inputs (e.g., `"Mera order 89782837 ka return status kya hai?"`).

   * Maps informal phrasing ("wapas bhejna hai", "send back") to canonical policy categories (`Reverse Pickup`, `Return Window`, `RTO`).

   * Maintains the user's preferred language in generated responses.

## 5. Evaluation Benchmarks & Practice Suite Setup

System verification and retrieval accuracy are benchmarked using the included practice suite and validation utilities.

### Practice Evaluation Files

1. **`practice/questions.csv` (52 Single-Turn Questions)**

   * **`id`**: Unique question identifier (e.g., `PQ0002`).

   * **`question` / `asr_text`**: Raw text input and synthetic speech-to-text transcripts with phonetic errors.

   * **`expected_decision`**: Categorized expected action (`answer`, `clarify`, `escalate`, `refuse`).

   * **`gold_evidence`**: Expected section IDs (e.g., `RET-2`, `products.csv:ELE-0012`).

   * **`must_include` / `must_not_include`**: Validation rules for output facts and prohibited assertions.

2. **`practice/conversations.csv` (23 Multi-Turn Conversations / 96 Turns)**

   * Groups interactions by `conversation_id` and tracks state across consecutive `turn` sequences.

   * Validates state transitions, verification challenges, tool calls (`expected_tool_calls`), and handover tickets.

### Local Execution & Dataset Validation

To verify relational schema integrity, primary/foreign key consistency, and file structures, execute `validate_dataset.py` from the project root:

```
# 1. Run relational schema and dataset integrity checks
python validate_dataset.py

# 2. Test individual execution tools
python tools/tools.py

# 3. Test multi-agent swarm pipeline execution
python src/agent_swarm.py

# 4. Execute the main entry point application
python app/main.py

```

### Verification Output Format

Upon running `validate_dataset.py`, the system verifies all relational join keys and outputs a validation summary:

```
========================================================
🔍 Validating ZentroMart Capstone Dataset Schema
========================================================
[1/7] Validating customers.csv... OK (300 records)
[2/7] Validating orders.csv... OK (1000 records)
[3/7] Validating order_items.csv... OK (1783 records)
[4/7] Validating products.csv... OK (70 records)
[5/7] Validating pincodes.csv... OK (36 records)
[6/7] Validating holidays.csv... OK (4 records)
[7/7] Validating kb/*.md documents... OK (21 articles parsed, Section IDs intact)

✅ Schema Integrity Check Passed. All primary/foreign key constraints valid.
========================================================

```

*Documentation compiled for the ZentroMart Customer Support Agent project.*