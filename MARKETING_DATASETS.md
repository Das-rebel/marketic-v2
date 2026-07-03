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
