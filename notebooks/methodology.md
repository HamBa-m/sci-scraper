### Methodology

Our methodology for conducting a comprehensive survey on adversarial attacks and defenses in multi-agent reinforcement learning (MARL) is divided into two main phases: **Data Collection** and **Topic Modeling**. Each phase is designed to ensure a systematic and insightful analysis of the research landscape.

---

#### 1. Data Collection

To build a robust dataset of research papers, we developed a customized web scraping tool using Python 3. This tool comprises two primary components, each targeting distinct sources of academic literature.

**a. Scholar Scraper:**  
This component performs targeted searches on Google Scholar using a pre-defined query string. It retrieves the top *K* pages of search results, where *K* is a configurable parameter. Since Google Scholar only provides paper titles and links, we implemented a suite of custom abstract scrapers tailored to the specific formats of various academic publishers. These include:
- **IEEE Scraper**
- **Springer Scraper**
- **MLR Scraper**
- **ArXiv Scraper**
- **NeurIPS Scraper**
- **MDPI Scraper**
- **ScienceDirect Scraper**
- **ACM Scraper**
- **AAAI Scraper**
- **JAIR Scraper**
- **JMLR Scraper**
- **IJCAI Scraper**

**b. Venue Scraper:**  
To complement the Scholar Scraper, we directly targeted high-impact conference and journal websites known for their focus on MARL, game theory, and adversarial learning. Using logical combinations of keywords such as *Reinforcement Learning (RL)*, *Multi-Agent RL (MARL)*, *Game Theory*, and *Adversarial*, we extracted papers from the following venues:
- **AAMAS**
- **IJCAI**
- **AISTATS**
- **ICML**
- **ICLR**

The search was constrained by a specified range of publication years to ensure relevance. The results from both components were merged into a unified dataset stored in an Excel file, containing five columns: *Title*, *Abstract*, *Year*, *Source*, and *URL*. Through iterative experimentation with different keyword combinations and query strings, we curated a final dataset of **647 papers** deemed highly relevant to our survey.

**Semantic Filtering Using Large Language Models:**  
To refine the dataset further, we employed an open-source large language model (LLM), specifically Microsoft's **Phi-3.5** model available on HuggingFace, to perform semantic filtering. This step was crucial to address the limitations of keyword-based searches, which often include papers that are tangentially related or irrelevant. We designed a carefully engineered prompt to evaluate the relevance of each paper based on its title and abstract. After this filtering process, the dataset was reduced to **148 papers** that were directly aligned with the scope of our survey.

---

#### 2. Topic Modeling

To uncover the underlying research trends and themes within the filtered dataset, we applied an advanced clustering pipeline using the **BERTopic** library. This pipeline consisted of seven interconnected modules:

1. **Embedding**: Leveraging transformer-based models to generate dense vector representations of the text.
2. **Dimensionality Reduction**: Utilizing UMAP to reduce the dimensionality of the embeddings while preserving their semantic structure.
3. **Semi-Supervised Clustering**: Incorporating a zero-shot learning technique to guide the clustering process.
4. **Clustering**: Applying HDBSCAN to identify natural groupings within the data.
5. **Tokenization**: Using CountVectorizer to preprocess the text for further analysis.
6. **Weighting**: Employing c-TF-IDF to assign importance scores to terms within each cluster.
7. **Word Representation**: Combining KeyBERT and Maximal Marginal Relevance (MMR) to extract representative keywords for each topic.

During initial iterations, we experimented with various hyperparameter configurations for each module, excluding the zero-shot component, to assess their impact on the results. We observed that the clustering outcomes consistently converged to a stable set of topics. Based on expert feedback, we manually refined the topics and applied the zero-shot module in the final iteration to classify the papers into four distinct themes:
- **Attacks**
- **Defenses**
- **Communication**
- **Applications**

This structured approach not only provided a clear understanding of the research landscape but also enabled us to identify key trends and gaps in the field of adversarial attacks and defenses in MARL.