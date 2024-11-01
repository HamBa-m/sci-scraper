# app.py
from flask import Flask, render_template, request, redirect, url_for, flash, Response
from scholar_scraper import ScholarScraper
from data_handler import DataHandler
import time
import json

app = Flask(__name__)
app.secret_key = 'your_secure_secret_key'
data_handler = DataHandler()
progress = 0
processed_papers = []

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        global progress, processed_papers
        progress = 0
        processed_papers = []
        
        query = request.form['query']
        num_pages = request.form['num_pages']
        
        if not query:
            flash("Please enter a search query.", "error")
            return redirect(url_for('index'))
        
        try:
            num_pages = int(num_pages)
        except ValueError:
            flash("Please enter a valid number for pages.", "error")
            return redirect(url_for('index'))
        
        # Start scraping process
        scraper = ScholarScraper(query=query, num_pages=num_pages)
        results = scraper.scrape(callback=update_progress)

        # Save results and calculate statistics
        data_handler.save_to_excel(results, "scholar_results.xlsx")
        stats = data_handler.calculate_statistics(results)
        
        return render_template('index.html', 
                             stats=stats, 
                             query=query, 
                             num_pages=num_pages)
    
    return render_template('index.html')

def update_progress(current, total, paper_data=None):
    """Update the scraping progress and broadcast to the SSE endpoint."""
    global progress, processed_papers
    progress = int((current / total) * 100)
    
    # Add the paper data if available
    if paper_data:
        processed_papers.append(paper_data)

@app.route('/progress')
def progress_stream():
    def generate():
        global progress, processed_papers
        last_sent_index = 0
        
        while progress < 100:
            # Send progress percentage
            paper_updates = processed_papers[last_sent_index:]
            last_sent_index = len(processed_papers)
            yield f"data:{json.dumps({'progress': progress, 'papers': paper_updates})}\n\n"
            time.sleep(1)
        
        # Final 100% update with any remaining papers
        paper_updates = processed_papers[last_sent_index:]
        yield f"data:{json.dumps({'progress': 100, 'papers': paper_updates})}\n\n"
        
    return Response(generate(), mimetype='text/event-stream')

if __name__ == '__main__':
    app.run(debug=True)
