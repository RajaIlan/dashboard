from flask import Flask, render_template_string, request
import csv

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>CME GCE INFRA</title>

    <style>
        body {
            font-family: Arial;
            margin: 0;
            background: #f5f6fa;
        }

        .navbar {
            background: #1f2c3a;
            color: white;
            padding: 15px;
            display: flex;
            justify-content: space-between;
        }

        .container {
            padding: 30px;
        }

        .card {
            background: white;
            padding: 20px;
            border-radius: 8px;
            max-width: 1000px;
            margin: auto;
        }

        .search-bar {
            display: flex;
            gap: 10px;
            margin-top: 20px;
            justify-content: center;
        }

        .search-bar select {
            width: 160px;
            padding: 10px;
        }

        .search-bar input {
            width: 300px;
            padding: 10px;
        }

        .search-bar button {
            width: 120px;
            padding: 10px;
            background: #2e6da4;
            color: white;
            border: none;
            cursor: pointer;
        }

        table {
            width: 100%;
            margin-top: 20px;
            border-collapse: collapse;
        }

        th, td {
            border: 1px solid #ddd;
            padding: 8px;
            text-align: center;
        }

        th {
            background: #2c3e50;
            color: white;
        }

        footer {
            position: fixed;
            bottom: 0;
            width: 100%;
            background: #0b1a2a;
            color: cyan;
            display: flex;
            justify-content: space-around;
            padding: 10px;
        }
    </style>
</head>

<body>

<div class="navbar">
    <div>CME GCE INFRA</div>
    <div>Home | Admin | App Team | Contact</div>
</div>

<div class="container">
    <div class="card">

        <h2>Infrastructure Inventory</h2>

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
                    <option value="DEV">DEV</option>
                    <option value="UT">UT</option>
                    <option value="QA">QA</option>
                    <option value="PROD">PROD</option>
                </select>

                <button type="submit">Search</button>

            </div>
        </form>

        {% if searched and results %}
        <table>
            <tr>
                {% for key in results[0].keys() %}
                <th>{{ key }}</th>
                {% endfor %}
            </tr>

            {% for row in results %}
            <tr>
                {% for value in row.values() %}
                <td>{{ value }}</td>
                {% endfor %}
            </tr>
            {% endfor %}
        </table>

        {% elif searched %}
            <p>No records found</p>
        {% endif %}

    </div>
</div>

<footer>
    <div>Bangalore: <span id="indiaClock"></span></div>
    <div>Chicago: <span id="cstClock"></span></div>
    <div>Belfast: <span id="gmtClock"></span></div>
</footer>

<script>
function updateClocks() {
    const now = new Date();

    document.getElementById("indiaClock").innerText =
        now.toLocaleTimeString("en-IN", { timeZone: "Asia/Kolkata" });

    document.getElementById("cstClock").innerText =
        now.toLocaleTimeString("en-US", { timeZone: "America/Chicago" });

    document.getElementById("gmtClock").innerText =
        now.toLocaleTimeString("en-GB", { timeZone: "Europe/London" });
}

setInterval(updateClocks, 1000);
updateClocks();
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