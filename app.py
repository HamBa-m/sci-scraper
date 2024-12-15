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
        # Process the statistics
        stats_text = data_handler.calculate_statistics(results)
        
        # Parse the stats text into structured data
        stats_data = parse_stats_text(stats_text)
        
        return render_template('index.html', 
                             total_papers=stats_data['total_papers'],
                             papers_with_abstracts=stats_data['papers_with_abstracts'],
                             abstract_success_rate=stats_data['abstract_success_rate'],
                             source_stats=stats_data['source_stats'],
                             other_sources=stats_data['other_sources'],
                             query=query, 
                             num_pages=num_pages)
    
    return render_template('index.html')

def parse_stats_text(stats_text):
    """Parse the statistics text into structured data for the template."""
    stats_data = {}
    
    # Parse the overall summary
    for line in stats_text.split('\n'):
        if 'Total papers found:' in line:
            stats_data['total_papers'] = int(line.split(': ')[1])
        elif 'Total papers with abstracts:' in line:
            stats_data['papers_with_abstracts'] = int(line.split(': ')[1])
        elif 'Overall abstract success rate:' in line:
            stats_data['abstract_success_rate'] = float(line.split(': ')[1].rstrip('%'))
    
    # Parse source statistics
    source_stats = []
    other_sources = []
    parsing_sources = False
    parsing_other = False
    
    for line in stats_text.split('\n'):
        if 'Breakdown by Source:' in line:
            parsing_sources = True
            continue
        elif 'Unique Sources in \'Other\' Category:' in line:
            parsing_sources = False
            parsing_other = True
            continue
            
        if parsing_sources and line.strip():
            if not line.startswith('Source'):  # Skip header
                parts = line.split()
                source_stats.append({
                    'Source': ' '.join(parts[:-3]),
                    'Papers with Abstract': int(parts[-3]),
                    'Total Papers': int(parts[-2]),
                    'Success Rate (%)': float(parts[-1])
                })
        
        if parsing_other and line.startswith('- '):
            source_info = line[2:].split(': ')
            other_sources.append({
                'name': source_info[0],
                'count': int(source_info[1].split()[0])
            })
    
    stats_data['source_stats'] = source_stats
    stats_data['other_sources'] = other_sources
    
    return stats_data

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

@app.route('/download')
def download_results():
    try:
        return send_file(
            'scholar_results.xlsx',
            as_attachment=True,
            download_name='scholar_results.xlsx',
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    except Exception as e:
        flash("Error downloading file.", "error")
        return redirect(url_for('index'))
    
def send_file(filename, as_attachment=False, download_name=None, mimetype=None):
    """Send a file as an attachment or inline."""
    try:
        with open(filename, 'rb') as f:
            response = Response(f.read(), mimetype=mimetype)
            response.headers['Content-Disposition'] = f'{"attachment" if as_attachment else "inline"}; filename={download_name or filename}'
            return response
    except Exception as e:
        flash("Error downloading file.", "error")
        return redirect(url_for('index'))
    
if __name__ == '__main__':
    app.run(debug=True)
