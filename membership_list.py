# Format the membership list
# Generate the input list from so's memberdb using this call:
# ./member_list.py -a --summary markdown-members > membership_list.txt

def markdown_to_html_table(md_text):
    lines = [line.strip() for line in md_text.strip().split("\n") if line.strip()]
    
    # Extract rows (skip separator line)
    rows = [line.strip("|").split("|") for line in lines if not set(line).issubset({"|", "-", " "})]
    rows = [[cell.strip() for cell in row] for row in rows]

    # Build HTML
    html = ["<table>"]
    
    # Header
    header = rows[0]
    html.append("    <tr>")
    for col in header:
        html.append(f"      <th style='text-align: left;'>{col}</th>")
    html.append("    </tr>")
    
    # Body
    for row in rows[1:]:
        html.append("    <tr>")
        for cell in row:
            html.append(f"      <td style='padding-right: 1em;'>{cell}</td>")
        html.append("    </tr>")
    
    html.append("</table>")
    
    return "\n".join(html)


# Read from file
with open("membership_list.txt", "r", encoding="utf-8") as f:
    membership_list = f.read()

# Theses
output = '<div style="margin-left:50px; padding-bottom:2em;">\n'
output += markdown_to_html_table(membership_list)
output += '</div>'
with open("members.html", "w", encoding="utf-8") as f:
    f.write(output)

