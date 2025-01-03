# read classified papers from scholar and venues and merge them in one file
import pandas as pd

# read classified papers from scholar
scholar_papers = pd.read_excel("./results/classified_scholar_papers.xlsx")
# read classified papers from venues
venues_papers = pd.read_excel("./results/classified_venues_papers.xlsx")
# read classified papers from AAMAS
aamas_papers = pd.read_excel("./results/classified_AAMAS_papers.xlsx")

# merge the two dataframes
merged_papers = pd.concat([scholar_papers, venues_papers], ignore_index=True)
merged_papers = pd.concat([merged_papers, aamas_papers], ignore_index=True)

# merge Abstract and abstract columns
merged_papers['Abstract'] = merged_papers['Abstract'].combine_first(merged_papers['abstract'])

# drop the abstract column
merged_papers = merged_papers.drop(columns=['abstract'])

# merge Year and year columns
merged_papers['Year'] = merged_papers['Year'].combine_first(merged_papers['year'])

# drop the year column
merged_papers = merged_papers.drop(columns=['year'])

# merge Title and title columns
merged_papers['Title'] = merged_papers['Title'].combine_first(merged_papers['title'])

# drop the title column
merged_papers = merged_papers.drop(columns=['title'])

# merge link and URL columns
merged_papers['URL'] = merged_papers['URL'].combine_first(merged_papers['link'])

# drop the link column
merged_papers = merged_papers.drop(columns=['link'])

# merge source and Venue columns
merged_papers['source'] = merged_papers['source'].combine_first(merged_papers['Venue'])

# rename the source column to Source
merged_papers = merged_papers.rename(columns={'source': 'Source'})

# drop the Venue column
merged_papers = merged_papers.drop(columns=['Venue'])

# drop citation column
merged_papers = merged_papers.drop(columns=['citation'])

# print the number of duplicate titles
print("Number of duplicate titles: ", merged_papers.duplicated(subset=['Title']).sum())

# drop duplicate titles
merged_papers = merged_papers.drop_duplicates(subset=['Title'])

# put as first columns Title, Source, Year, Abstract, URL, then the rest of the columns
merged_papers = merged_papers[['Title', 'Source', 'Year', 'Abstract', 'URL'] + [col for col in merged_papers.columns if col not in ['Title', 'Source', 'Year', 'Abstract', 'URL']]]

# save the merged papers
merged_papers.to_excel("results/mergejygukd_papers.xlsx", index=False)

print("Merged papers saved successfully")
print("Number of papers: ", len(merged_papers))