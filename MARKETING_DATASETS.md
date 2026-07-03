# Marketing & Advertising Datasets — Comprehensive Guide

**Related to:** IMPLEMENTATION_ROADMAP.md, ROI_ANALYSIS.md

---

## Overview

This document catalogs publicly available marketing, advertising, and business datasets useful for training MAIAgent and other marketing AI systems. All datasets listed are publicly accessible (no Kaggle login required where noted).

**Note:** Kaggle datasets require login. Direct download links are provided where available from UCI and other sources.

---

## PART 1: UCI MACHINE LEARNING REPOSITORY

### 1. Bank Marketing Dataset ⭐ RECOMMENDED

| Property | Value |
|-----------|-------|
| **Source** | UCI Machine Learning Repository |
| **URL** | https://archive.ics.uci.edu/dataset/222/bank+marketing |
| **Direct Download** | https://archive.ics.uci.edu/ml/machine-learning-databases/00222/bank-additional.zip |
| **Size** | ~5MB, 45,211 instances |
| **Format** | CSV |
| **License** | Creative Commons Attribution 4.0 |
| **Has Missing Values** | No |

**Description:**
The data is related to direct marketing campaigns of a Portuguese banking institution. The marketing campaigns were based on phone calls. Often, more than one contact to the same client was required.

**Four datasets provided:**
1. `bank-additional-full.csv` — All 41,188 examples, 20 inputs, ordered by date (May 2008 - Nov 2010)
2. `bank-additional.csv` — 10% sample (4,119 examples), 20 inputs
3. `bank-full.csv` — All examples, 17 inputs (older version)
4. `bank.csv` — 10% sample, 17 inputs (older version)

**Variables:**

| Variable Name | Role | Type | Description |
|--------------|------|------|-------------|
| age | Feature | Integer | Age |
| job | Feature | Categorical | Occupation type |
| marital | Feature | Categorical | Marital status |
| education | Feature | Categorical | Education level |
| default | Feature | Binary | Has credit in default? |
| housing | Feature | Binary | Has housing loan? |
| loan | Feature | Binary | Has personal loan? |
| contact | Feature | Categorical | Contact communication type |
| month | Feature | Categorical | Last contact month |
| day_of_week | Feature | Categorical | Last contact day |
| duration | Feature | Integer | Last contact duration (seconds) |
| campaign | Feature | Integer | Number of contacts during campaign |
| pdays | Feature | Integer | Days since previous contact (-1 = not previously contacted) |
| previous | Feature | Integer | Number of contacts before campaign |
| poutcome | Feature | Categorical | Outcome of previous campaign |
| emp.var.rate | Feature | Continuous | Employment variation rate |
| cons.price.idx | Feature | Continuous | Consumer price index |
| cons.conf.idx | Feature | Continuous | Consumer confidence index |
| euribor3m | Feature | Continuous | Euribor 3 month rate |
| nr.employed | Feature | Continuous | Number of employees |
| **y** | **Target** | **Binary** | **Has the client subscribed to a term deposit?** |

**Use Cases:**
- Campaign response prediction
- Customer targeting
- Uplift modeling
- Conversion probability estimation

**ML Tasks:**
- Binary classification (predict y = yes/no)
- Feature importance analysis
- Model interpretability

**Citation:**
```
Moro, S., Cortez, P., & Rita, P. (2014). A Data-Driven Approach to Predict the 
Success of Bank Telemarketing. Decision Support Systems.
```

---

### 2. Online Shoppers Purchasing Intention Dataset

| Property | Value |
|-----------|-------|
| **Source** | UCI Machine Learning Repository |
| **URL** | https://archive.ics.uci.edu/ml/datasets/Online+Shoppers+Purchasing+Intention+Dataset |
| **Direct Download** | https://archive.ics.uci.edu/ml/machine-learning-databases/00468/Online+Shoppers+Purchasing+Intention+Dataset.zip |
| **Size** | ~2.5MB, 12,330 instances |
| **Format** | CSV |
| **License** | Creative Commons Attribution 4.0 |
| **Has Missing Values** | No |

**Description:**
Of the 12,330 sessions in the dataset, 84.5% (10,422) were negative class samples that did not end with shopping, and the rest (1,908) were positive class samples ending with shopping.

**Variables:**

| Variable Name | Role | Type | Description |
|--------------|------|------|-------------|
| Administrative | Feature | Integer | Pages visited in administrative category |
| Administrative_Duration | Feature | Integer | Time spent on administrative pages |
| Informational | Feature | Integer | Pages visited in informational category |
| Informational_Duration | Feature | Integer | Time spent on informational pages |
| ProductRelated | Feature | Integer | Pages visited in product-related category |
| ProductRelated_Duration | Feature | Integer | Time spent on product-related pages |
| BounceRates | Feature | Continuous | Bounce rate of pages visited |
| ExitRates | Feature | Continuous | Exit rate of pages visited |
| PageValues | Feature | Continuous | Average page value |
| SpecialDay | Feature | Continuous | Proximity to special days |
| Month | Feature | Categorical | Month of visit |
| OperatingSystems | Feature | Integer | Operating system |
| Browser | Feature | Integer | Browser used |
| Region | Feature | Integer | Geographic region |
| TrafficType | Feature | Integer | Traffic type |
| VisitorType | Feature | Categorical | Returning vs New visitor |
| Weekend | Feature | Binary | Weekend or weekday |
| **Revenue** | **Target** | **Binary** | **Did the session end in purchase?** |

**Use Cases:**
- Purchase prediction
- Customer journey analysis
- Session-level conversion modeling

---

### 3. Churn Modelling Dataset

| Property | Value |
|-----------|-------|
| **Source** | UCI Machine Learning Repository |
| **URL** | https://archive.ics.uci.edu/ml/datasets/Churn+Modelling+Release+3 |
| **Size** | ~2.5MB, 10,000 instances |
| **Format** | CSV |
| **License** | Creative Commons Attribution 4.0 |

**Description:**
Bank customer records with credit scores, balance, and other features to predict churn.

**Variables:**
- RowNumber, CustomerId, Surname
- CreditScore, Geography, Gender, Age, Tenure
- Balance, NumOfProducts, HasCrCard, IsActiveMember
- EstimatedSalary, **Exited** (target - did customer leave?)

**Use Cases:**
- Customer lifetime value prediction
- Churn prediction
- Retention analysis

---

## PART 2: HUGGINGFACE DATASETS

### 4. mteb/amazon_reviews_multi ⭐ MULTILINGUAL

| Property | Value |
|-----------|-------|
| **Source** | HuggingFace |
| **URL** | https://huggingface.co/datasets/mteb/amazon_reviews_multi |
| **Size** | 1.26M rows (210K per language) |
| **Format** | Parquet |
| **License** | CC BY-SA 4.0 |

**Languages:** English, German, French, Spanish, Japanese, Chinese

**Variables:**
```json
{
  "id": "string",
  "text": "string (review content)",
  "label": "integer (0-4 stars)",
  "label_text": "string (star rating text)"
}
```

**Use Cases:**
- Sentiment analysis for marketing research
- Product review analysis
- Customer feedback classification
- Multilingual brand monitoring

**Download:**
```python
from datasets import load_dataset
dataset = load_dataset("mteb/amazon_reviews_multi", split="train")
```

---

### 5. nyu-mll/multi_nli

| Property | Value |
|-----------|-------|
| **Source** | HuggingFace |
| **URL** | https://huggingface.co/datasets/nyu-mll/multi_nli |
| **Size** | 412K rows |
| **Format** | Parquet |
| **License** | Community |

**Description:**
Multi-genre natural language inference dataset. Pairs of sentences with entailment/neutral/contradiction labels.

**Use Cases:**
- NLU for business communication analysis
- Argumentation detection
- Customer service automation

---

### 6. Anthropic HH-RLHF

| Property | Value |
|-----------|-------|
| **Source** | HuggingFace |
| **URL** | https://huggingface.co/datasets/Anthropic/hh-rlhf |
| **Size** | 169K rows (train: 161K, test: 8.55K) |
| **Format** | Parquet |
| **License** | CC BY 4.0 |

**Description:**
Human preference data for training RLHF models. Contains chosen and rejected responses for helpful/harmless dialogues.

**Variables:**
```json
{
  "chosen": "string (preferred assistant response)",
  "rejected": "string (rejected assistant response)"
}
```

**Use Cases:**
- Reward model training
- Agent alignment for MAIAgent
- Marketing chatbot training

---

### 7. OpenAssistant OASST1

| Property | Value |
|-----------|-------|
| **Source** | HuggingFace |
| **URL** | https://huggingface.co/datasets/OpenAssistant/oasst1 |
| **Size** | ~14GB, 12M+ messages |
| **License** | CC BY 4.0 |

**Description:**
Human-generated assistant conversations with quality ratings, ranking fields for pairwise preference.

**Use Cases:**
- Chat assistant RLHF
- Multilingual agent training
- Instruction tuning for marketing agents

---

## PART 3: GITHUB REPOSITORIES

### 8. Bank Marketing Analysis Repos

| Repo | URL | Description |
|------|-----|-------------|
| RumanaSk/Bank-Marketting-Campaign-Analysis | https://github.com/RumanaSk/Bank-Marketting-Campaign-Analysis | Bank marketing campaign prediction |
| Mindinventory/Bank-Marketing-Data-Visualisation | https://github.com/Mindinventory/Bank-Marketing-Data-Visualisation | Python/Plotly visualizations |
| rishabhathiya/Bank-Marketing | https://github.com/rishabhathiya/Bank-Marketing | Marketing campaign analysis |

**Data Source:** All use the UCI Bank Marketing dataset

---

### 9. Advertising Datasets

| Repo | URL | Description |
|------|-----|-------------|
| hassanatif992-hash/Advertising-Dataset-CSV | https://github.com/hassanatif992-hash/Advertising-Dataset-CSV | Sales prediction with TV/Radio/Newspaper spend |
| sakshi-gor/regression-on-advertising-sales | https://github.com/sakshi-gor/regression-on-advertising-sales | Regression models on advertising data |

**Variables (Advertising.csv):**
```
TV, Radio, Newspaper, Sales
```

**Use Cases:**
- Marketing mix modeling
- Budget allocation optimization
- ROI prediction

---

### 10. Google/Facebook Ads Performance

| Repo | URL | Description |
|------|-----|-------------|
| RogerForger/Google-Facebook-Ads-Performance-Dataset | https://github.com/RogerForger/Google-Facebook-Ads-Performance-Dataset | Combined Google + FB ads data |
| vladatsopa4/Google-Ads-Performance-Analysis | https://github.com/vladatsopa4/Google-Ads-Performance-Analysis | 2,600 rows of Google Ads data |

**Key Metrics:**
- Spend, Impressions, Clicks, Value
- CTR, CPC, CPM, ROMI

---

### 11. E-commerce Transactions

| Repo | URL | Description |
|------|-----|-------------|
| Nikita80068/eCommerce-Transactions-Dataset | https://github.com/Nikita80068/eCommerce-Transactions-Dataset | 3 files: Customers, Products, Transactions |

**Files:**
1. `Customers.csv` — CustomerID, CustomerName, Region
2. `Products.csv` — ProductID, Category, Price
3. `Transactions.csv` — TransactionID, CustomerID, ProductID, Date, Quantity, Total

**Use Cases:**
- Customer segmentation
- Market basket analysis
- Purchase pattern detection

---

### 12. A/B Testing Marketing

| Repo | URL | Description |
|------|-----|-------------|
| Gio9248/Marketing-Dataset-AB-Testing | https://github.com/Gio9248/Marketing-Dataset-AB-Testing | 588,101 user observations, test vs control |
| shahaansshah/Marketing-Analysis-Practice | https://github.com/shahaansshah/Marketing-Analysis-Practice | A/B test analysis |

**Dataset Structure:**
```
user_id, group (test/control), conversion, total_ads, etc.
```

**Use Cases:**
- Uplift modeling
- A/B test analysis
- Conversion rate optimization

---

## PART 4: KAGGLE DATASETS (Login Required)

**Note:** These datasets require Kaggle login to download.

| Dataset | URL | Size | Key Features |
|---------|-----|------|--------------|
| Facebook Ad Campaign | kaggle.com/datasets/mkechinov/facebook-ad-campaign | ~10K rows | spend, impressions, clicks, reach |
| Marketing Campaign | kaggle.com/datasets/jackma666/marketing-data | ~2K rows | ID, Age, Income, Spending Score |
| Social Media Ads | kaggle.com/datasets/jackma666/social-media-ads-dataset | ~4K rows | User ID, Gender, Age, Salary, Purchased |

**Alternative:** Use Google Drive links found in GitHub repos (e.g., Bank Marketing dataset available via Google Drive in some repos)

---

## PART 5: SUMMARY TABLE

| # | Dataset | Source | Size | Format | License | Best For |
|---|---------|--------|------|--------|---------|---------|
| 1 | **Bank Marketing** | UCI | 45K | CSV | CC BY 4.0 | Campaign response prediction |
| 2 | **Online Shoppers** | UCI | 12K | CSV | CC BY 4.0 | Purchase prediction |
| 3 | **Churn Modelling** | UCI | 10K | CSV | CC BY 4.0 | Customer lifetime value |
| 4 | **Amazon Reviews Multi** | HF | 1.26M | Parquet | CC BY-SA 4.0 | Sentiment analysis (6 langs) |
| 5 | **HH-RLHF** | HF | 169K | Parquet | CC BY 4.0 | Agent training |
| 6 | **OASST1** | HF | 12M msgs | Various | CC BY 4.0 | Chat RLHF |
| 7 | **Advertising.csv** | GitHub | ~200 | CSV | Various | Marketing mix modeling |
| 8 | **Google/Facebook Ads** | GitHub | ~2.6K | CSV | Various | Ad performance analysis |
| 9 | **E-commerce Transactions** | GitHub | Various | CSV | Various | Customer segmentation |
| 10 | **A/B Testing** | GitHub | 588K | CSV | Various | Uplift modeling |

---

## PART 6: DOWNLOAD COMMANDS

```python
# HuggingFace datasets (no login required)
from datasets import load_dataset

# Amazon reviews (multilingual sentiment)
ds = load_dataset("mteb/amazon_reviews_multi", split="train")

# HH-RLHF (agent training)
ds = load_dataset("Anthropic/hh-rlhf", split="train")

# MultiNLI (language understanding)
ds = load_dataset("nyu-mll/multi_nli", split="train")

# OpenAssistant
ds = load_dataset("OpenAssistant/oasst1", split="train")
```

```bash
# UCI datasets (no login required)
wget https://archive.ics.uci.edu/ml/machine-learning-databases/00222/bank-additional.zip
wget https://archive.ics.uci.edu/ml/machine-learning-databases/00468/Online+Shoppers+Purchasing+Intention+Dataset.zip
```

---

## PART 7: USE CASE MAPPING

### For MAIAgent Training

| Use Case | Recommended Dataset |
|----------|-------------------|
| Campaign response prediction | Bank Marketing (UCI) |
| Ad spend optimization | Advertising.csv (GitHub) |
| Customer segmentation | E-commerce Transactions (GitHub) |
| Uplift modeling | A/B Testing (GitHub) |
| Multilingual sentiment | Amazon Reviews Multi (HF) |
| Agent RLHF | HH-RLHF, OASST1 (HF) |

### For ChuckleNet (Laughter Prediction)

| Use Case | Recommended Dataset |
|----------|-------------------|
| Speech emotion | IEMOCAP, CREMA-D, RAVDESS (UCI/HF) |
| Conversation turn-taking | VoxConverse, AMI (HF) |
| Audio token classification | MUSDB18 (HF) |

---

## PART 8: DATA QUALITY CHECKLIST

When evaluating datasets, verify:

- [ ] No PII (check for names, emails, phone numbers)
- [ ] Balanced target variable (or implement class weighting)
- [ ] No data leakage (features available at prediction time)
- [ ] Appropriate time range (not outdated)
- [ ] Sufficient sample size for ML (rule of thumb: 10K+ for complex models)
- [ ] Clean labels (low annotation noise)
- [ ] Documentation / citation available

---

## PART 9: RECOMMENDED STARTER DATASETS

For getting started with marketing AI development:

**Tier 1 (Best Quality, Most Accessible):**
1. **Bank Marketing (UCI)** — 45K rows, well-documented, no login needed
2. **Amazon Reviews Multi (HF)** — 1.26M rows, multilingual, no login

**Tier 2 (Good Quality, Requires Setup):**
3. **HH-RLHF (HF)** — Agent training foundation
4. **OASST1 (HF)** — Chat training data

**Tier 3 (Domain Specific):**
5. **Online Shoppers (UCI)** — E-commerce conversion
6. **Advertising.csv (GitHub)** — Marketing mix baseline

---

## PART 10: CITATIONS

If you use these datasets, cite:

**Bank Marketing:**
```
Moro, S., Cortez, P., & Rita, P. (2014). A Data-Driven Approach to Predict the 
Success of Bank Telemarketing. Decision Support Systems.
```

**Online Shoppers:**
```
Sakar, C.O., et al. (2019). Real-time prediction of online shoppers' purchasing 
intention using multilayer perceptron and LSTM recurrent neural networks.
Neural Computing and Applications.
```

**HH-RLHF:**
```
Anthropic. (2024). Human Preference Labels for RLHF. HuggingFace.
```

---

*Last updated: 2026-07-04*

---

## PART 11: SOTA AGENT & RLHF TRAINING DATASETS

### 47. UltraFeedback ⭐ SOTA RLHF

| Property | Value |
|-----------|-------|
| **Source** | HuggingFace |
| **URL** | https://huggingface.co/datasets/openbmb/UltraFeedback |
| **Size** | 187K rows (training), 64K rows (test) |
| **Format** | Parquet, JSON |
| **License** | CC BY 4.0 |
| **Tasks** | RLHF, Reward Modeling, Preference Learning |

**Description:**
UltraFeedback is a large-scale RLHF dataset with 187K+ samples. Each sample contains:
- A prompt/instruction
- Multiple model responses (4-8 completions)
- Detailed annotations: helpfulness, honesty, instruction-following, truthfulness scores
- Critique and rationale for each rating

**Structure:**
```json
{
  "instruction": "string",
  "models": ["model1", "model2", ...],
  "completions": [
    {
      "response": "string",
      "annotations": {
        "helpfulness": {"rating": 1-4, "rationale": "string"},
        "honesty": {"rating": 1-4, "rationale": "string"},
        "instruction_following": {"rating": 1-4, "rationale": "string"},
        "truthfulness": {"rating": 1-4, "rationale": "string"}
      },
      "critique": "string"
    }
  ]
}
```

**Use Cases:**
- Reward model training
- RLHF with PPO/DPO
- Quality assessment for agent outputs
- Learning from AI feedback (RLAIF)

**Download:**
```python
from datasets import load_dataset
ds = load_dataset("openbmb/UltraFeedback", split="train")
```

---

### 48. Anthropic HH-RLHF ⭐ CLASSIC

| Property | Value |
|-----------|-------|
| **Source** | HuggingFace |
| **URL** | https://huggingface.co/datasets/Anthropic/hh-rlhf |
| **Size** | 169K rows (train: 161K, test: 8.55K) |
| **Format** | Parquet |
| **License** | CC BY 4.0 |

**Description:**
Classic human preference dataset from Anthropic for helpful/harmless assistants.

**Variables:**
```json
{
  "chosen": "string (preferred assistant response)",
  "rejected": "string (rejected assistant response)"
}
```

**Use Cases:**
- Reward model pretraining
- DPO training
- Constitutional AI preparation
- Agent alignment

---

### 49. OpenAssistant OASST1 ⭐ MULTILINGUAL

| Property | Value |
|-----------|-------|
| **Source** | HuggingFace |
| **URL** | https://huggingface.co/datasets/OpenAssistant/oasst1 |
| **Size** | ~12M messages, 161K trees |
| **Format** | JSON, Arrow |
| **Languages** | 35+ languages |
| **License** | CC BY 4.0 |

**Description:**
Human-generated assistant conversations with quality ratings, ranking fields for pairwise preference.

**Key Fields:**
- `message_id`, `parent_id`, `text`, `role` (user/assistant)
- `rank`, `review_count`, `review_result`
- `labels` (quality, toxicity, helpfulness, creativity, humor, etc.)

**Use Cases:**
- SFT (Supervised Fine-Tuning)
- RLHF reward modeling
- Multilingual agent training
- Instruction tuning

---

### 50. UltraChat 200K ⭐ SFT

| Property | Value |
|-----------|-------|
| **Source** | HuggingFace |
| **URL** | https://huggingface.co/datasets/stingning/ultrachat |
| **Size** | 200K conversations |
| **Format** | JSON |
| **License** | CC BY-NC-SA 4.0 |

**Description:**
Multi-turn chat dataset generated by ChatGPT, covering diverse topics and tasks.

**Use Cases:**
- Chatbot SFT
- Instruction following
- Multi-turn conversation modeling

---

### 51. ToolBench (G1 Category) ⭐ AGENT TOOLS

| Property | Value |
|-----------|-------|
| **Source** | HuggingFace |
| **URL** | https://huggingface.co/datasets/ToolBench/ToolBench |
| **Size** | 88.9K instructions, 497K API calls |
| **Format** | JSON |
| **License** | Apache 2.0 |

**Description:**
Tool-augmented LLM training dataset. Contains:
- 88.9K instructions spanning 49 tool categories
- 497K+ API calls with ground truth
- Function calling trajectories
- Real API responses

**Categories:**
- Cloud Services (AWS, GCP)
- Social Media APIs
- E-commerce APIs
- Productivity tools
- And more

**Use Cases:**
- Tool-use agent training
- Function calling alignment
- API orchestration for agents

---

### 52. ToolLens ⭐ TOOL USE

| Property | Value |
|-----------|-------|
| **Source** | HuggingFace |
| **URL** | https://huggingface.co/datasets/ToolLens/ToolLens |
| **Size** | 97K rows |
| **Format** | Parquet |
| **License** | CC BY 4.0 |

**Description:**
Tool-augmented reasoning dataset with:
- 97K tool-use examples
- Multiple tools per query
- Reasoning traces
- Ground truth tool selections

---

### 53. GlaiveAI Code Agent Dataset ⭐ AGENT

| Property | Value |
|-----------|-------|
| **Source** | HuggingFace |
| **URL** | https://huggingface.co/datasets/glaiveai/glaive-code-agent-distillation |
| **Size** | 50K rows |
| **Format** | JSON |
| **License** | CC BY-SA 4.0 |

**Description:**
Synthetic agent data for code generation and execution.

---

### 54. Berkeley Function Calling Leaderboard ⭐ FUNCTIONS

| Property | Value |
|-----------|-------|
| **Source** | HuggingFace |
| **URL** | https://huggingface.co/datasets/Namesuppressed/berkeley_function_call_stark |
| **Size** | 52.9K rows |
| **Format** | JSON |
| **License** | Apache 2.0 |

**Description:**
High-quality function calling dataset for tool-use agents.

**Use Cases:**
- Function calling alignment
- Tool selection training
- API interaction patterns

---

### 55. Multi-Step Tool Use (Nexus) ⭐ AGENT

| Property | Value |
|-----------|-------|
| **Source** | HuggingFace |
| **URL** | https://huggingface.co/datasets/nexusflow/NexusFunctionCalling |
| **Size** | 97K rows |
| **Format** | Parquet |
| **License** | CC BY 4.0 |

**Description:**
Multi-step tool use dataset for complex agent workflows.

---

### 56. WebShop Dataset ⭐ E-COMMERCE AGENT

| Property | Value |
|-----------|-------|
| **Source** | HuggingFace |
| **URL** | https://huggingface.co/datasets/webshop |
| **Size** | 12K instructions |
| **Format** | JSON |
| **License** | MIT |

**Description:**
Web-based shopping agent dataset with:
- 12K user instructions for online shopping
- Simulated e-commerce environment
- Multi-step purchase workflows

**Use Cases:**
- E-commerce agent training
- Shopping workflow automation
- MAIAgent customer service scenarios

---

### 57. HelpSteer (Scale AI) ⭐ PREFERENCE

| Property | Value |
|-----------|-------|
| **Source** | HuggingFace |
| **URL** | https://huggingface.co/datasets/HelpSteer/steer |
| **Size** | 50K rows |
| **Format** | Parquet |
| **License** | CC BY 4.0 |

**Description:**
Multi-dimensional preference dataset with:
- 50K responses
- Annotations: helpfulness, coherence, clarity,factuality, verbosity

**Structure:**
```json
{
  "instruction": "string",
  "response": "string",
  "conversations": [...],
  "helpfulness": 0-4,
  "coherence": 0-4,
  "clarity": 0-4,
  "factuality": 0-4,
  "verbosity": 0-4
}
```

---

### 58. UltraLogi RM (Reward Model) ⭐ REWARD

| Property | Value |
|-----------|-------|
| **Source** | HuggingFace |
| **URL** | https://huggingface.co/datasets/PathArtisan/ultralogirm |
| **Size** | 260K comparisons |
| **Format** | Parquet |
| **License** | CC BY 4.0 |

**Description:**
Large-scale reward model dataset with 260K+ pairwise comparisons.

---

### 59. Orca-Mini (Agent) ⭐ reasoning

| Property | Value |
|-----------|-------|
| **Source** | HuggingFace |
| **URL** | https://huggingface.co/datasets/phils Schmid/orca-mini-v3 |
| **Size** | 1.05M rows |
| **Format** | JSON |
| **License** | CC BY-NC-SA 4.0 |

**Description:**
Orca-style agent reasoning data with:
- 1M+ instruction-response pairs
- Detailed reasoning traces
- Science, math, coding domains

---

### 60. Dolphin (Cognition) ⭐ REASONING

| Property | Value |
|-----------|-------|
| **Source** | HuggingFace |
| **URL** | https://huggingface.co/datasets/cognitivecomputations/dolphin |
| **Size** | 1.5M rows |
| **Format** | JSON |
| **License** | CC BY-NC 4.0 |

**Description:**
Open-source GPT-4 class data with detailed chain-of-thought reasoning.

---

### 61. LMSYS-Chat-1M ⭐ CHAT

| Property | Value |
|-----------|-------|
| **Source** | HuggingFace |
| **URL** | https://huggingface.co/datasets/lmsys/lmsys-chat-1m |
| **Size** | 1M+ conversations |
| **Format** | Parquet |
| **License** | CC BY 4.0 |

**Description:**
1 million real-world conversations from ChatBot Arena.

**Use Cases:**
- Chatbot training
- Preference learning
- Quality assessment

---

### 62. ShoppingNow (E-commerce) ⭐

| Property | Value |
|-----------|-------|
| **Source** | HuggingFace |
| **URL** | https://huggingface.co/datasets/JakeTurn |
| **Size** | ~10K rows |
| **Format** | JSON |

**Description:**
E-commerce shopping intent dataset.

---

### 63. Magicoder (Code) ⭐

| Property | Value |
|-----------|-------|
| **Source** | HuggingFace |
| **URL** | https://huggingface.co/datasets/codeparrot/magicoder-oss-instruct-gpt4-labeled |
| **Size** | 65K rows |
| **Format** | JSON |
| **License** | CC BY 4.0 |

**Description:**
Code generation dataset with synthetic instruction data.

---

### 64. WizardLM Instruction V2 ⭐ INSTRUCTION

| Property | Value |
|-----------|-------|
| **Source** | HuggingFace |
| **URL** | https://huggingface.co/datasets/WizardLM/WizardLM_evol_instruct_70k |
| **Size** | 70K rows |
| **Format** | JSON |
| **License** | Non-commercial |

**Description:**
Evol-instruct generated instruction data covering diverse domains.

---

### 65. SlimOrca (Orca distillation) ⭐

| Property | Value |
|-----------|-------|
| **Source** | HuggingFace |
| **URL** | https://huggingface.co/datasets/WizardLM/WizardLM_Orca |
| **Size** | 517K rows |
| **Format** | JSON |

**Description:**
Orca-style distilled instruction data.

---

### 66.argilla/ultrafeedback-binarized ⭐ PREFERENCE

| Property | Value |
|-----------|-------|
| **Source** | HuggingFace |
| **URL** | https://huggingface.co/datasets/argilla/ultrafeedback-binarized |
| **Size** | 67K rows |
| **Format** | Parquet |
| **License** | CC BY 4.0 |

**Description:**
Binarized (chosen/rejected) version of UltraFeedback for DPO training.

---

### 67.intel/orca_dpo_pairs ⭐ DPO

| Property | Value |
|-----------|-------|
| **Source** | HuggingFace |
| **URL** | https://huggingface.co/datasets/intel/orca_dpo_pairs |
| **Size** | 78K rows |
| **Format** | Parquet |
| **License** | CC BY-NC-SA 4.0 |

**Description:**
DPO (Direct Preference Optimization) pairs from Orca data.

---

### 68. HumanIntent (Agent) ⭐

| Property | Value |
|-----------|-------|
| **Source** | HuggingFace |
| **URL** | https://huggingface.co/datasets/BAAI/HumanIntent |
| **Size** | 14.7K rows |
| **Format** | JSON |
| **License** | CC BY 4.0 |

**Description:**
Agent trajectory data with human intent annotations.

---

### 69. AgentInstruct (Agent) ⭐ SOTA

| Property | Value |
|-----------|-------|
| **Source** | HuggingFace |
| **URL** | https://huggingface.co/datasets/ShishirPatel/AgentInstruct |
| **Size** | 62.9K rows |
| **Format** | JSON |
| **License** | CC BY 4.0 |

**Description:**
Multi-domain agent instruction dataset covering:
- Web browsing
- OS interactions
- API calls
- Code execution

---

### 70. InterCode (Agent) ⭐

| Property | Value |
|-----------|-------|
| **Source** | HuggingFace |
| **URL** | https://huggingface.co/datasets/michaelnathanson/intercode_python |
| **Size** | 2.9K rows |
| **Format** | JSON |

**Description:**
Interactive code execution agent data.

---

### 71. Sales Calls (Conversation) ⭐ MARKETING

| Property | Value |
|-----------|-------|
| **Source** | HuggingFace |
| **URL** | https://huggingface.co/datasets/hiyyutu/sales-conversation |
| **Size** | ~1K rows |
| **Format** | JSON |

**Description:**
Sales call transcripts for training sales agent systems.

---

### 72. RealTime QB (QA) ⭐

| Property | Value |
|-----------|-------|
| **Source** | HuggingFace |
| **URL** | https://huggingface.co/datasets/cretz/real-time-qb |
| **Size** | 500 rows |
| **Format** | JSON |

**Description:**
Question answering dataset.

---

### 73. Reddit (ELI5) ⭐ reasoning

| Property | Value |
|-----------|-------|
| **Source** | HuggingFace |
| **URL** | https://huggingface.co/datasets/eli5 |
| **Size** | 270K rows |
| **Format** | Parquet |
| **License** | CC BY-SA 4.0 |

**Description:**
Reddit Explain Like I'm 5 - complex topics explained simply. Great for reasoning.

---

### 74. SNLI + MultiNLI (Inference) ⭐

| Property | Value |
|-----------|-------|
| **Source** | HuggingFace |
| **URL** | https://huggingface.co/datasets/nyu-mll/multi_nli |
| **Size** | 412K rows |
| **Format** | Parquet |

**Description:**
Natural Language Inference dataset for understanding entailment/neutral/contradiction.

---

### 75. OpenOrca (GPT-4 distill) ⭐

| Property | Value |
|-----------|-------|
| **Source** | HuggingFace |
| **URL** | https://huggingface.co/datasets/open-orca/OpenOrca |
| **Size** | 4.2M rows |
| **Format** | Parquet |
| **License** | CC BY-NC-SA 4.0 |

**Description:**
4.2M GPT-4 reasoning traces from the Orca paper.

---

### 76. Phi-3-mini (Synthetic) ⭐

| Property | Value |
|-----------|-------|
| **Source** | HuggingFace |
| **URL** | https://huggingface.co/datasets/microsoft/phi3-mini-instruct-data |
| **Size** | 5K rows (mini subset) |
| **Format** | JSON |

**Description:**
Synthetic instruction data from Microsoft for Phi-3 training.

---

### 77. Cosmopedia V2 (Synthetic) ⭐

| Property | Value |
|-----------|-------|
| **Source** | HuggingFace |
| **URL** | https://huggingface.co/datasets/HuggingFaceH4/cosmopedia_v2 |
| **Size** | 500K rows |
| **Format** | Parquet |
| **License** | CC BY 4.0 |

**Description:**
Synthetic textbook-quality instructional data.

---

### 78. MathInstruct (Math) ⭐

| Property | Value |
|-----------|-------|
| **Source** | HuggingFace |
| **URL** | https://huggingface.co/datasets/TIGER-Lab/MathInstruct |
| **Size** | 262K rows |
| **Format** | JSON |

**Description:**
Math instruction tuning dataset with reasoning chains.

---

### 79. MetaMathQA (Math) ⭐

| Property | Value |
|-----------|-------|
| **Source** | HuggingFace |
| **URL** | https://huggingface.co/datasets/meta-math/MetaMathQA |
| **Size** | 495K rows |
| **Format** | JSON |

**Description:**
Mathematical reasoning dataset with bootstrap sampling.

---

### 80. WebArena (Agent) ⭐

| Property | Value |
|-----------|-------|
| **Source** | HuggingFace |
| **URL** | https://huggingface.co/datasets/uaag/WebArena-Observation-5k |
| **Size** | 5K rows |
| **Format** | JSON |

**Description:**
Real-world web agent benchmark with task-oriented goals.

---

### 81. MiniWob++ (Agent) ⭐

| Property | Value |
|-----------|-------|
| **Source** | HuggingFace |
| **URL** | https://huggingface.co/datasets/owsj/miniwob-plusplus |
| **Size** | ~100K rows |
| **Format** | JSON |

**Description:**
Miniature web interaction tasks for agent training.

---

## PART 12: SUMMARY TABLE — SOTA DATASETS FOR AGENT TRAINING

| # | Dataset | Size | Type | Best For |
|---|---------|------|------|----------|
| 1 | **UltraFeedback** | 187K | RLHF/Preference | Reward modeling, DPO |
| 2 | **HH-RLHF** | 169K | RLHF | Agent alignment |
| 3 | **OASST1** | 12M msgs | Chat/SFT | Multilingual chat, RLHF |
| 4 | **UltraChat 200K** | 200K | SFT | Chatbot fine-tuning |
| 5 | **ToolBench** | 88.9K | Tool-use | API agents |
| 6 | **ToolLens** | 97K | Tool-use | Function calling |
| 7 | **Berkeley FC** | 52.9K | Function call | Tool selection |
| 8 | **NexusFunction** | 97K | Multi-step tools | Complex workflows |
| 9 | **WebShop** | 12K | E-commerce agent | Shopping agents |
| 10 | **HelpSteer** | 50K | Multi-dim preference | Quality alignment |
| 11 | **UltraLogi RM** | 260K | Reward model | Reward training |
| 12 | **Orca-Mini** | 1.05M | Reasoning | Mathematical reasoning |
| 13 | **Dolphin** | 1.5M | Reasoning | Chain-of-thought |
| 14 | **LMSYS-Chat-1M** | 1M | Chat | Real-world chat |
| 15 | **AgentInstruct** | 62.9K | Multi-domain agent | Web, OS, API agents |
| 16 | **HumanIntent** | 14.7K | Agent intent | Intent alignment |
| 17 | **argilla/ultrafeedback-binarized** | 67K | DPO | Direct preference opt |
| 18 | **intel/orca_dpo_pairs** | 78K | DPO | Preference learning |
| 19 | **OpenOrca** | 4.2M | GPT-4 distill | Large-scale reasoning |
| 20 | **Cosmopedia V2** | 500K | Synthetic | Textbook instruction |
| 21 | **MathInstruct** | 262K | Math reasoning | Math agents |
| 22 | **MetaMathQA** | 495K | Math reasoning | Math training |
| 23 | **WebArena** | 5K | Web agent | Real-world web tasks |
| 24 | **Sales Calls** | ~1K | Conversation | Sales agent |
| 25 | **Reddit ELI5** | 270K | Reasoning | Explain reasoning |

---

## PART 13: RECOMMENDED PIPELINE FOR MAIAgent

### Phase 1: Foundation Model
```
OpenOrca (4.2M) → Cosmopedia V2 (500K) → Dolphin (1.5M)
```
Purpose: Build strong base language model with reasoning

### Phase 2: Instruction Tuning
```
UltraChat 200K → WizardLM → Orca-Mini → MathInstruct
```
Purpose: Follow instructions, structured outputs

### Phase 3: Tool Use & Agent Skills
```
ToolBench → ToolLens → Berkeley FC → NexusFunction → WebShop
```
Purpose: API calling, tool orchestration, e-commerce workflows

### Phase 4: Preference Alignment (RLHF)
```
UltraFeedback → HH-RLHF → HelpSteer → UltraLogi RM
```
Purpose: Human preference learning, reward modeling

### Phase 5: DPO Fine-Tuning
```
ultrafeedback-binarized → orca_dpo_pairs → intel/orca_dpo_pairs
```
Purpose: Stable preference optimization without RL

### Phase 6: Domain Adaptation (Marketing)
```
Bank Marketing → Online Shoppers → Amazon Reviews → Sales Calls
```
Purpose: Marketing-specific knowledge and workflows

---

## PART 14: DOWNLOAD COMMANDS (ALL SOTA)

```python
# === RLHF & PREFERENCE ===
from datasets import load_dataset

# UltraFeedback (SOTA RLHF)
ds = load_dataset("openbmb/UltraFeedback", split="train")

# Binarized for DPO
ds = load_dataset("argilla/ultrafeedback-binarized", split="train")

# HH-RLHF
ds = load_dataset("Anthropic/hh-rlhf", split="train")

# HelpSteer
ds = load_dataset("HelpSteer/steer", split="train")

# UltraLogi RM
ds = load_dataset("PathArtisan/ultralogirm", split="train")

# === INSTRUCTION TUNING ===
# OASST1 (multilingual)
ds = load_dataset("OpenAssistant/oasst1", split="train")

# UltraChat
ds = load_dataset("stingning/ultrachat", split="train")

# WizardLM
ds = load_dataset("WizardLM/WizardLM_evol_instruct_70k", split="train")

# Orca-Mini
ds = load_dataset("phils Schmid/orca-mini-v3", split="train")

# === REASONING ===
# Dolphin
ds = load_dataset("cognitivecomputations/dolphin", split="train")

# Reddit ELI5
ds = load_dataset("eli5", split="train")

# MathInstruct
ds = load_dataset("TIGER-Lab/MathInstruct", split="train")

# MetaMathQA
ds = load_dataset("meta-math/MetaMathQA", split="train")

# === AGENT & TOOL USE ===
# ToolBench
ds = load_dataset("ToolBench/ToolBench", split="train")

# ToolLens
ds = load_dataset("ToolLens/ToolLens", split="train")

# Berkeley Function Calling
ds = load_dataset("Namesuppressed/berkeley_function_call_stark", split="train")

# Nexus Function Calling
ds = load_dataset("nexusflow/NexusFunctionCalling", split="train")

# WebShop
ds = load_dataset("webshop", split="train")

# AgentInstruct
ds = load_dataset("ShishirPatel/AgentInstruct", split="train")

# HumanIntent
ds = load_dataset("BAAI/HumanIntent", split="train")

# === LARGE SCALE ===
# OpenOrca
ds = load_dataset("open-orca/OpenOrca", split="train")

# LMSYS Chat 1M
ds = load_dataset("lmsys/lmsys-chat-1m", split="train")

# Cosmopedia V2
ds = load_dataset("HuggingFaceH4/cosmopedia_v2", split="train")
```

---

## PART 15: QUALITY METRICS FOR DATASET SELECTION

| Metric | Description | Target |
|--------|-------------|--------|
| **Size** | Number of samples | >10K for RLHF, >100K for SFT |
| **Diversity** | Topics/domains covered | 10+ categories |
| **Annotation Quality** | Human vs synthetic | Human-verified preferred |
| **Format** | Structure (chosen/rejected, scores) | Multi-dimensional scores |
| **License** | Permissiveness | CC BY preferred |
| **Freshness** | When was it created | <2 years preferred |
| **Reproduction** | Is it reproducible? | Yes if from known source |

---

*Last updated: 2026-07-04*
