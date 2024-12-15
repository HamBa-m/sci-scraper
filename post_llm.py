import pandas as pd

# load excel file
papers = pd.read_excel("conference_papers_with_adversarial_attacks_column.xlsx")

# filter the dataframe to get only the relevant papers
relevant_papers = papers[papers['is_relevent'] == 1]
print("Relevant papers shape:", relevant_papers.shape)

# save the relevant papers to a new xlsx file
relevant_papers.to_excel("relevant_conference_papers.xlsx", index=False)
