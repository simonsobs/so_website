import bibtexparser
from html import escape
from collections import defaultdict

JOURNAL_MAP = {
    r"\ao": "Applied Optics",
    r"\apj": "The Astrophysical Journal",
    r"\apjl": "The Astrophysical Journal Letters",
    r"\apjs": "The Astrophysical Journal Supplement Series",
    r"\mnras": "Monthly Notices of the Royal Astronomical Society",
    r"\aap": "Astronomy & Astrophysics",
    r"\aj": "The Astronomical Journal",
    r"\prd": "Physical Review D",
    r"\prl": "Physical Review Letters",
    r"\jcap": "Journal of Cosmology and Astroparticle Physics",
}

def strip_braces(text):
    if not text:
        return text
    return text.replace("{", "").replace("}", "")


def format_authors(author_field):
    if not author_field:
        return "Unknown authors"
    authors = [strip_braces(a.strip()) for a in author_field.split(" and ")]
    return ", ".join(authors).replace('~',' ')


def get_arxiv_link(entry):
    eprint = entry.get("eprint")
    if eprint:
        archive = entry.get("archivePrefix", "").lower()
        if archive == "arxiv" or "/" in eprint or "." in eprint:
            return f"https://arxiv.org/abs/{eprint}", eprint

    url = entry.get("url", "")
    if "arxiv.org" in url:
        # Extract ID from URL for display
        arxiv_id = url.split("/")[-1]
        return url, arxiv_id

    return None, None


def get_doi_link(entry):
    doi = entry.get("doi")
    if doi:
        doi = doi.strip()
        return f"https://doi.org/{doi}", doi
    return None, None

def get_ads_link(entry):
    adsurl = entry.get("adsurl")
    if adsurl:
        return adsurl.strip()
    return None

def normalize_journal(name):
    if not name:
        return ""

    name = strip_braces(name).strip()

    # Match case-insensitively
    lower_map = {k.lower(): v for k, v in JOURNAL_MAP.items()}

    key = name.lower()
    if key in lower_map:
        return lower_map[key]

    return name

def format_venue(entry):
    journal = normalize_journal(entry.get("journal", ""))
    booktitle = strip_braces(entry.get("booktitle", ""))

    venue = journal if journal else booktitle if booktitle else ""

    volume = entry.get("volume", "")
    number = entry.get("number", "")
    pages = entry.get("pages", "")

    parts = []

    if volume:
        vol_str = str(volume)
        if number:
            vol_str += f"({number})"
        parts.append(vol_str)

    if pages:
        parts.append(f"pp. {pages}")

    if parts:
        return f"{venue}, " + ", ".join(parts)

    return venue

def generate_html_by_year(file_path, entry_filter="all"):
    with open(file_path, "r", encoding="utf-8") as bibfile:
        bib_db = bibtexparser.load(bibfile)

    def matches_filter(entry):
        entry_type = entry.get("ENTRYTYPE", "").lower()

        if entry_filter == "all":
            return True

        if entry_filter == "papers":
            return entry_type == "article"

        if entry_filter == "conferences":
            return entry_type == "inproceedings"

        if entry_filter == "theses":
            return entry_type in {"phdthesis", "mastersthesis"}

        return True  # fallback


    # Group entries by year
    grouped = defaultdict(list)

    for entry in bib_db.entries:
        if matches_filter(entry):
            year = entry.get("year", "n.d.")
            grouped[year].append(entry)

    # Sort years (descending, treating non-numeric as 0)
    def year_key(y):
        try:
            return int(y)
        except ValueError:
            return 0

    sorted_years = sorted(grouped.keys(), key=year_key, reverse=True)

    html_parts = []

    for year in sorted_years:
        html_parts.append(f"<h2>{escape(str(year))}</h2>")
        html_parts.append("<ol class=\"wp-block-list\">")

        # Sort entries within the year (optional: by title)
        entries = sorted(
            grouped[year],
            key=lambda e: strip_braces(e.get("title", "")).lower()
        )

        for entry in entries:
            title = escape(strip_braces(entry.get("title", "No title")))
            authors = escape(format_authors(entry.get("author", "")))
            # journal = escape(strip_braces(entry.get("journal", entry.get("booktitle", "No venue"))))
            venue = escape(format_venue(entry))
            arxiv_url, arxiv_text = get_arxiv_link(entry)
            doi_url, doi_text = get_doi_link(entry)
            ads_url = get_ads_link(entry)

            item = f"<li><b>{title}</b><br>"
            item += f"{authors}<br>"
            if venue:
                item += f"<em>{venue}</em>"
            if doi_url:
                item += f'; DOI: <a href="{escape(doi_url)}">{escape(doi_text)}</a>'
            if arxiv_url:
                item += f'; arXiv: <a href="{escape(arxiv_url)}">{escape(arxiv_text)}</a>'
            if ads_url:
                if venue:
                    item += f'; <a href="{escape(ads_url)}">NASA ADS</a>'
                else:
                    item += f'<a href="{escape(ads_url)}">NASA ADS</a>'
            item += "</li>"

            html_parts.append(item)

        html_parts.append("</ol>")

    return "\n".join(html_parts)


# Example usage
if __name__ == "__main__":
    output = '<div style="margin-left:50px;">\n<h1>Papers</h1>'
    output += generate_html_by_year("publications.bib",entry_filter='papers')
    output += '<h1>Proceedings</h1>'
    output += generate_html_by_year("publications.bib",entry_filter='conferences')
    output += '<h1>Theses</h1>'
    output += generate_html_by_year("publications.bib",entry_filter='theses')
    output += '</div>'
    print(output)

