from flask import Flask, render_template_string, request
import csv

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>CME GCE INFRA</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">

    <style>
body {
    font-family: Arial;
    margin: 0;
    background: #f5f6fa;
}

/* NAVBAR */
.navbar {
    background: #1f2c3a;
    color: white;
    padding: 15px;
    display: flex;
    justify-content: space-between;
}

.nav-icon {
    font-size: 22px;
    margin-left: 20px;
    text-decoration: none;
    color: #00e6e6;   /* bright color */
    transition: 0.3s ease;
}

.nav-icon:hover {
    color: #00ffff;
    transform: scale(1.2);
}

.nav-icon:visited,
.nav-icon:active {
    color: #00e6e6;
}

.accordion-header {
    font-size: 18px;
    font-weight: bold;
    cursor: pointer;
    margin-bottom: 10px;
    user-select: none;
}

.accordion-header:hover {
    color: #2e6da4;
}

/* CONTAINER */
.container {
    padding: 20px;
    display: flex;
    justify-content: center;
}

/* CARD */
.card {
    background: white;
    padding: 20px;
    border-radius: 8px;
    width: 95%;
    max-width: 1500px;
    box-shadow: 0px 2px 8px rgba(0,0,0,0.1);
}

/* SEARCH BAR */
.search-bar {
    display: flex;
    gap: 10px;
    margin-top: 20px;
    justify-content: center;
    flex-wrap: wrap;
}

.search-bar select,
.search-bar input,
.search-bar button {
    padding: 10px;
}

.search-bar input {
    width: 300px;
}

.search-bar select {
    width: 160px;
}

.search-bar button {
    width: 120px;
    background: #2e6da4;
    color: white;
    border: none;
    cursor: pointer;
}

/* TABLE WRAPPER */
.table-container {
    width: 100%;
    overflow-x: auto;
    margin-top: 20px;
}

/* TABLE */
table {
    width: 100%;
    min-width: 1200px;
    border-collapse: collapse;
}

th, td {
    border: 1px solid #ddd;
    padding: 8px;
    text-align: center;
    white-space: nowrap;
}

th {
    background: #2c3e50;
    color: white;
}

/* alternating row color */
tr:nth-child(even) {
    background-color: #f2f2f2;
}

/* FOOTER */
footer {
    position: fixed;
    bottom: 0;
    width: 100%;
    background: #0b1a2a;
    color: cyan;
    display: flex;
    justify-content: space-around;
    padding: 10px;
    text-align: center;
}

.clock-block {
    display: flex;
    flex-direction: column;
}

.clock-title {
    font-size: 20px;
    margin-bottom: 5px;
}

.clock-time {
    font-size: 18px;
    font-weight: bold;
}
</style>
</head>

<body>

<div class="navbar">
    <div>CME GCE INFRA</div>
    <div>
    <a href="/" class="nav-icon" title="Home">🏠</a>
    <a href="https://chat.google.com/room/AAQAmhbqcd4?cls=7" target="_blank" class="nav-icon" title="Contact">💬</a>
</div>
</div>

<div class="container">
    <div class="card">

        <div class="accordion-header" onclick="toggleAccordion()">
        <span id="arrow">▶</span> Infrastructure Inventory
    </div>

    <div id="accordion-content" style="display: none;">

        <form method="POST">
        <div class="search-bar">

                <select name="search_type">
                    <option value="appid">App ID</option>
                    <option value="hostname">Hostname</option>
                    <option value="bootdisk">Bootdisk</option>
                    <option value="projectid">ProjectID</option>
                </select>

                <input type="text" name="query" placeholder="Enter value..." required>

                <select name="env">
                    <option value="ALL">All Env</option>
                    <option value="dv">DEV</option>
                    <option value="ut">UT</option>
                    <option value="qa">QA</option>
                    <option value="pr">PROD</option>
                </select>

                <button type="submit">Search</button>

            </div>
        </form>
        </div>

        {% if searched and results %}
        <div class="table-container">
        <table>
            <tr>
                {% for key in results[0].keys() %}
                <th>{{ key }}</th>
                {% endfor %}
            </tr>

            {% for row in results %}
            <tr>
                {% for value in row.values() %}
                <td title="{{ value }}">{{ value }}</td>
                {% endfor %}
            </tr>
            {% endfor %}
        </table>
        </div>

        {% elif searched %}
            <p>No records found</p>
        {% endif %}

    </div>
</div>

<footer>
    <div class="clock-block">
        <div class="clock-title">Bangalore</div>
        <div class="clock-time" id="indiaClock"></div>
    </div>

    <div class="clock-block">
        <div class="clock-title">Chicago</div>
        <div class="clock-time" id="cstClock"></div>
    </div>

    <div class="clock-block">
        <div class="clock-title">Belfast</div>
        <div class="clock-time" id="gmtClock"></div>
    </div>
</footer>

<script>
function updateClocks() {
    const now = new Date();

    document.getElementById("indiaClock").innerText =
        now.toLocaleTimeString("en-IN", {
            timeZone: "Asia/Kolkata",
            hour12: false
        });

    document.getElementById("cstClock").innerText =
        now.toLocaleTimeString("en-US", {
            timeZone: "America/Chicago",
            hour12: false
        });

    document.getElementById("gmtClock").innerText =
        now.toLocaleTimeString("en-GB", {
            timeZone: "Europe/London",
            hour12: false
        });
}

setInterval(updateClocks, 1000);
updateClocks();

function toggleAccordion() {
    const content = document.getElementById("accordion-content");
    const arrow = document.getElementById("arrow");

    if (content.style.display === "none") {
        content.style.display = "block";
        arrow.innerText = "▼";
    } else {
        content.style.display = "none";
        arrow.innerText = "▶";
    }
}
</script>

</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def home():
    results = []
    searched = False

    if request.method == 'POST':
        searched = True

        query = request.form['query'].strip().lower()
        search_type = request.form['search_type']
        env_filter = request.form['env'].upper()

        with open('data.csv', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)

            for row in reader:

                # skip empty rows
                if not any(row.values()):
                    continue

                # normalize safely
                normalized = {
                    (k or "").replace(" ", "").lower(): (v.strip() if isinstance(v, str) else "")
                    for k, v in row.items()
                }

                # selected field value
                value = normalized.get(search_type, "").lower()

                # split keywords
                keywords = query.split()

                # match selected field
                field_match = all(word in value for word in keywords)

                # global search (all fields)
                global_value = " ".join(normalized.values()).lower()
                global_match = all(word in global_value for word in keywords)

                # final match condition
                if field_match or global_match:

                    # environment filter
                    if env_filter == "ALL" or normalized.get('environment', '').upper() == env_filter:
                        results.append(row)

    return render_template_string(HTML, results=results, searched=searched)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)