# Summary of Key Ideas in MARL Research

This document summarizes key ideas and observations from a review of Multi-Agent Reinforcement Learning (MARL) research papers. The focus is on how attackers are modeled, the use of specific algorithms, integration with other approaches, and applications across various domains.

---

## Key Points

### 1. **Attacker Representation in MARL**
   - Many papers model attackers as agents within the MARL framework.
   - Game-theory-based papers often treat attackers as agents using a zero-sum game approach, resembling GAN-like environments.
   - **Question:** Should these be classified as Adversarial MARL, especially in cybersecurity applications?

### 2. **Use of Independent Q-Learning (IQL) in MARL**
   - A significant number of papers employ IQL as the MARL algorithm.
   - IQL is the simplest form of MARL and does not address key multi-agent challenges (e.g., communication, interaction).
   - **Question:** Should these papers be included in the survey despite their simplicity?

### 3. **Integration of MARL and Game Theory**
   - Some papers merge MARL with game-theoretic approaches (e.g., RoMFAC RL).

### 4. **Adversarial Training Environments for MARL**
   - New environments like **CyMARL**, **MARNet**, and **MADRID** have been proposed for adversarial MARL training.

### 5. **Theoretical Focus**
   - Some papers concentrate on theoretical aspects such as upper bounds, learnability, and other conceptual frameworks.

### 6. **Robustness Testing**
   - Certain papers focus on developing attackers to test the robustness of other agents, particularly in rule-based algorithms for autonomous driving.

### 7. **Application Domains**
   - Most MARL applications are in:
     - Cybersecurity,
     - Vehicles and traffic,
     - Energy systems,
     - UAVs (Unmanned Aerial Vehicles).

### 8. **Outliers**
   - A few papers do not fit the multi-agent framework and are considered outliers.

---

## Questions for Consideration
1. Should papers modeling attackers as agents in a zero-sum game framework be classified as Adversarial MARL?
2. Should papers using IQL (despite its simplicity) be included in the survey?

## Sections
- Background
- Related Work (surveys) : must stress on what is different in our survey relatively to the existent ones, also to justify the survey itself
- Methodology (selection, classification, time-window etc.)
- Classes (paper presentation and critical analysis):
   - we will use the classification vector diagram sections as sections titles (i.e. 4 sections)
   - contributions, limitations and challenges
- Environments
- Future directions
- Conclusion

[+] we can group papers and analyse them instead of a 1-by-1 analysis

[+] we may need a criteria of comparison between papers inside every section (preferably shared, but not necessarily)

[+] ACM Surveys / AI Reviews: survey length should stay around the average length of these surveys