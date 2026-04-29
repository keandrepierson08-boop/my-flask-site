from flask import Flask, request, redirect, session, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import sqlite3

app = Flask(__name__)
app.secret_key = "change-this-secret-key-later"

DATABASE = "crest_confessions.db"

posts = [
    {
        "title": "Spotted at Crest Academy",
        "body": "Someone walked into first period wearing last night’s party drama like designer perfume. The halls are talking.",
        "tag": "School Drama",
        "heat": 86
    },
    {
        "title": "The Masquerade Secret",
        "body": "A mystery kiss. A missing bracelet. One rich kid swears they saw everything, but silence has a price.",
        "tag": "Party Alert",
        "heat": 94
    },
    {
        "title": "Trouble in the Friend Group",
        "body": "Best friends by morning, enemies by lunch. Crest Confessions has receipts, screenshots, and a whole lot of questions.",
        "tag": "Exposed",
        "heat": 78
    }
]

characters = [
    {"name": "Bianca", "role": "The Queen Bee", "bio": "Funny, stylish, dangerous when underestimated.", "status": "Trending"},
    {"name": "Carter", "role": "The Golden Boy", "bio": "Charming on the outside, messy behind closed doors.", "status": "Under Watch"},
    {"name": "Jaylen", "role": "The Legacy Kid", "bio": "Rich family, heavy secrets, and too much pressure.", "status": "Complicated"},
    {"name": "Ava", "role": "The Insider", "bio": "She knows more than she says, and posts less than she knows.", "status": "Suspicious"},
    {"name": "Finn", "role": "The Wild Card", "bio": "He jokes too much, but he notices everything.", "status": "New Arrival"},
    {"name": "Monet", "role": "The Senior Threat", "bio": "Elegant, intimidating, and always three steps ahead.", "status": "Dangerous"},
    {"name": "Monet", "role": "The Senior Threat", "bio": "Elegant, intimidating, and always three steps ahead.",
     "status": "Dangerous"},

]

episodes = [
    {"episode": "Episode 1", "title": "Welcome Back to Crest", "summary": "A new school year begins, but old secrets refuse to stay buried."},
    {"episode": "Episode 2", "title": "Screenshots Don’t Lie", "summary": "A private message goes public and friendships start cracking."},
    {"episode": "Episode 3", "title": "The Masquerade Problem", "summary": "Masks hide faces, but not intentions."},
    {"episode": "Episode 4", "title": "Legacy Kids", "summary": "Jaylen’s family drama becomes everyone’s favorite topic."}
]

season_one = [
    "Crest Confessions appears during the first major scandal of the year, posting anonymous tips about the richest students at Crest Academy.",
    "Bianca becomes the face of the school’s social scene, but her perfect image starts cracking when rumors about her relationship with Carter spread.",
    "Carter struggles between being the golden boy everyone loves and the messy person he actually is behind closed doors.",
    "Jaylen’s family name becomes a target after whispers about money, power, and old secrets start appearing online.",
    "Ava quietly watches everyone, slowly becoming one of the only people who understands how Crest Confessions moves.",
    "The season ends with the friend group realizing the blog is not just gossip. Someone is using it to control them."
]

season_two = [
    "Crest Confessions becomes more popular, meaner, and harder to ignore. Everyone checks it, even the people pretending they hate it.",
    "Bianca becomes funnier, sharper, and more chaotic this season, especially when she starts questioning whether Carter is being honest with her.",
    "Carter’s storyline gets darker as he deals with rehab, family pressure, and the feeling that everyone expects him to stay perfect.",
    "Ava takes a bigger role with the blog and becomes connected to the mystery in a way that makes her look suspicious.",
    "Finn enters the story and brings chaotic energy, jokes, and unexpected clues that shake up Jaylen’s world.",
    "Monet arrives as a senior threat, giving the school a new powerful girl who might know more than she should.",
    "The season finale reveals that Crest Confessions may be closer to the main group than anyone thought."
]

crest_confessions_suspects = [
    {
        "name": "Ava",
        "theory": "My top suspect. She has access, she is observant, and people underestimate her. She may not have started it, but she probably knows who did."
    },
    {
        "name": "Monet",
        "theory": "She feels like someone who could use gossip as a weapon. If she is not Crest Confessions, she might be feeding it information."
    },
    {
        "name": "Finn",
        "theory": "He acts like the comic relief, but that could be the perfect cover. He notices details while everyone thinks he is joking."
    },
    {
        "name": "Bianca",
        "theory": "Probably not the main blogger, but she is smart enough to manipulate the blog when it benefits her."
    }
]

STYLE = """
<style>
    * { box-sizing: border-box; }

    body {
        margin: 0;
        font-family: Georgia, 'Times New Roman', serif;
        background: radial-gradient(circle at top, #3b073f, #120014 45%, #050005);
        color: white;
    }

    header {
        background: linear-gradient(135deg, rgba(255,47,163,0.9), rgba(91,30,255,0.85));
        padding: 90px 20px;
        text-align: center;
    }

    header h1 {
        font-size: 64px;
        margin: 0;
        letter-spacing: 3px;
        text-transform: uppercase;
    }

    header p { font-size: 21px; margin-top: 12px; }

    nav {
        background: rgba(5,0,5,0.95);
        padding: 16px;
        text-align: center;
        position: sticky;
        top: 0;
        z-index: 100;
        border-bottom: 1px solid rgba(255,255,255,0.12);
    }

    nav a {
        color: #ff8bd6;
        text-decoration: none;
        margin: 0 12px;
        font-weight: bold;
    }

    nav a:hover { color: white; }

    .section {
        padding: 55px 25px;
        max-width: 1150px;
        margin: auto;
    }

    .section-title { font-size: 38px; margin-bottom: 18px; }

    .grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 24px;
    }

    .card {
        background: rgba(255,255,255,0.09);
        border: 1px solid rgba(255,255,255,0.18);
        border-radius: 22px;
        padding: 26px;
        box-shadow: 0 12px 40px rgba(0,0,0,0.35);
        backdrop-filter: blur(8px);
    }

    .card:hover {
        transform: translateY(-4px);
        transition: 0.25s ease;
        border-color: #ff8bd6;
    }

    .tag, .status {
        display: inline-block;
        background: #ff2fa3;
        padding: 7px 13px;
        border-radius: 20px;
        font-size: 13px;
        font-weight: bold;
    }

    .status { background: #5b1eff; }

    .button {
        display: inline-block;
        background: white;
        color: #120014;
        padding: 14px 24px;
        border-radius: 30px;
        text-decoration: none;
        font-weight: bold;
        margin-top: 15px;
    }

    .button-dark { background: #ff2fa3; color: white; }
    .hero-buttons { margin-top: 24px; }
    .hero-buttons a { margin: 6px; }

    .ticker {
        background: #ff2fa3;
        color: white;
        padding: 12px;
        overflow: hidden;
        white-space: nowrap;
        font-weight: bold;
    }

    .ticker span {
        display: inline-block;
        animation: scroll 18s linear infinite;
    }

    @keyframes scroll {
        from { transform: translateX(100%); }
        to { transform: translateX(-100%); }
    }

    .heat-bar {
        width: 100%;
        height: 13px;
        background: rgba(255,255,255,0.16);
        border-radius: 20px;
        overflow: hidden;
        margin-top: 14px;
    }

    .heat-fill {
        height: 100%;
        background: linear-gradient(90deg, #ff8bd6, #ff2fa3, #ffd1ec);
        border-radius: 20px;
    }

    .spotlight {
        display: grid;
        grid-template-columns: 1.1fr 0.9fr;
        gap: 24px;
        align-items: center;
    }

    .spotlight-box {
        background: linear-gradient(135deg, rgba(255,47,163,0.22), rgba(91,30,255,0.22));
        border-radius: 25px;
        padding: 35px;
        border: 1px solid rgba(255,255,255,0.2);
    }

    input, textarea, select {
        width: 100%;
        padding: 14px;
        margin: 10px 0;
        border-radius: 12px;
        border: none;
        font-size: 16px;
        font-family: Arial, sans-serif;
    }

    button {
        background: #ff2fa3;
        color: white;
        border: none;
        padding: 14px 24px;
        border-radius: 30px;
        font-weight: bold;
        cursor: pointer;
    }

    .admin-box { border: 1px dashed #ff8bd6; }
    .warning { color: #ffd1ec; font-weight: bold; }

    footer {
        text-align: center;
        padding: 35px;
        background: #050005;
        color: #bbb;
        margin-top: 40px;
    }

    @media (max-width: 800px) {
        header h1 { font-size: 42px; }
        .spotlight { grid-template-columns: 1fr; }
        nav a { display: inline-block; margin: 8px; }
    }
</style>
"""


def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tips (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            tip TEXT NOT NULL,
            submitted_by TEXT,
            created_at TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def current_user():
    return session.get("username")


def nav():
    login_links = ""
    if current_user():
        login_links = f"<a href='/profile'>Profile</a><a href='/logout'>Logout ({current_user()})</a>"
    else:
        login_links = "<a href='/login'>Login</a><a href='/register'>Register</a>"

    return f"""
    <nav>
        <a href='/'>Home</a>
        <a href='/characters'>Characters</a>
        <a href='/episodes'>Episodes</a>
        <a href='/seasons'>Season 1 & 2</a>
        <a href='/mystery'>Who Is Crest?</a>
        <a href='/submit'>Submit Tip</a>
        <a href='/admin'>Admin</a>
        {login_links}
    </nav>
    """


def page(title, body):
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>{title}</title>
        {STYLE}
    </head>
    <body>
        {nav()}
        {body}
        <footer>XOXO... you know you love the drama.</footer>
    </body>
    </html>
    """


def render_post_cards():
    return "".join([
        f"""
        <div class='card'>
            <span class='tag'>{post['tag']}</span>
            <h2>{post['title']}</h2>
            <p>{post['body']}</p>
            <p><strong>Drama Heat:</strong> {post['heat']}%</p>
            <div class='heat-bar'><div class='heat-fill' style='width: {post['heat']}%;'></div></div>
        </div>
        """
        for post in posts
    ])


def render_character_cards():
    return "".join([
        f"""
        <div class='card'>
            <span class='status'>{character['status']}</span>
            <h2>{character['name']}</h2>
            <h3>{character['role']}</h3>
            <p>{character['bio']}</p>
        </div>
        """
        for character in characters
    ])


@app.route("/")
def home():
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Crest Confessions</title>
        {STYLE}
    </head>
    <body>
        <header>
            <h1>Crest Confessions</h1>
            <p>Your favorite anonymous source for the scandals of Crest Academy.</p>
            <div class='hero-buttons'>
                <a class='button' href='/submit'>Send a Tip</a>
                <a class='button button-dark' href='/mystery'>Who Is Crest Confessions?</a>
            </div>
        </header>

        {nav()}

        <div class='ticker'>
            <span>BREAKING: Someone saw Carter leave the party early • Bianca is not laughing anymore • Ava has screenshots • Jaylen’s family name is trending again</span>
        </div>

        <section class='section spotlight'>
            <div class='spotlight-box'>
                <h1 class='section-title'>Tonight’s Main Character</h1>
                <h2>Bianca</h2>
                <p>When Bianca smiles, people relax. When Bianca goes quiet, people should start deleting messages.</p>
                <a class='button' href='/seasons'>Read Season Recaps</a>
            </div>
            <div class='card'>
                <h2>Drama Meter</h2>
                <p>Crest Academy is currently at a dangerous level of messy.</p>
                <div class='heat-bar'><div class='heat-fill' style='width: 91%;'></div></div>
                <p><strong>91%</strong> scandal activity detected.</p>
            </div>
        </section>

        <section class='section'>
            <h1 class='section-title'>Latest Confessions</h1>
            <div class='grid'>{render_post_cards()}</div>
        </section>

        <section class='section'>
            <h1 class='section-title'>Who’s Being Watched?</h1>
            <div class='grid'>{render_character_cards()}</div>
        </section>
    </body>
    </html>
    """


@app.route("/characters")
def character_page():
    return page("Characters | Crest Confessions", f"""
        <section class='section'>
            <h1 class='section-title'>Character Files</h1>
            <p>Everyone has a role. Everyone has a secret. Some people have both.</p>
            <div class='grid'>{render_character_cards()}</div>
        </section>
    """)


@app.route("/episodes")
def episode_page():
    episode_cards = "".join([
        f"""
        <div class='card'>
            <span class='tag'>{episode['episode']}</span>
            <h2>{episode['title']}</h2>
            <p>{episode['summary']}</p>
        </div>
        """
        for episode in episodes
    ])

    return page("Episodes | Crest Confessions", f"""
        <section class='section'>
            <h1 class='section-title'>Episode Archive</h1>
            <p>Every scandal has a chapter. Every chapter has a victim.</p>
            <div class='grid'>{episode_cards}</div>
        </section>
    """)


@app.route("/seasons")
def seasons_page():
    s1 = "".join([f"<li>{item}</li>" for item in season_one])
    s2 = "".join([f"<li>{item}</li>" for item in season_two])

    return page("Season 1 & 2 | Crest Confessions", f"""
        <section class='section'>
            <h1 class='section-title'>What Happened in Season 1 & 2</h1>
            <div class='grid'>
                <div class='card'>
                    <span class='tag'>Season 1</span>
                    <h2>The Blog Begins</h2>
                    <ul>{s1}</ul>
                </div>
                <div class='card'>
                    <span class='tag'>Season 2</span>
                    <h2>The Blog Gets Personal</h2>
                    <ul>{s2}</ul>
                </div>
            </div>
        </section>
    """)


@app.route("/mystery")
def mystery_page():
    suspect_cards = "".join([
        f"""
        <div class='card'>
            <span class='status'>Suspect</span>
            <h2>{suspect['name']}</h2>
            <p>{suspect['theory']}</p>
        </div>
        """
        for suspect in crest_confessions_suspects
    ])

    return page("Who Is Crest Confessions?", f"""
        <section class='section'>
            <h1 class='section-title'>Who Is Crest Confessions?</h1>
            <div class='spotlight-box'>
                <h2>My theory: Ava is the strongest suspect.</h2>
                <p>Ava makes the most sense because she is close enough to the drama to know the details, but quiet enough that people do not watch her closely. She feels like the person who could run the blog or at least control parts of it.</p>
                <p>But for a better mystery, I would make it a twist: Ava knows about Crest Confessions, Monet feeds it information, and the real original creator is someone from before Season 1.</p>
            </div>
            <br>
            <div class='grid'>{suspect_cards}</div>
        </section>
    """)


@app.route("/register", methods=["GET", "POST"])
def register():
    error = ""

    if request.method == "POST":
        username = request.form.get("username").strip()
        password = request.form.get("password")

        if len(username) < 3 or len(password) < 4:
            error = "Username must be at least 3 characters and password must be at least 4 characters."
        else:
            try:
                conn = get_db()
                conn.execute(
                    "INSERT INTO users (username, password, created_at) VALUES (?, ?, ?)",
                    (username, generate_password_hash(password), datetime.now().strftime("%B %d, %Y at %I:%M %p"))
                )
                conn.commit()
                conn.close()
                session["username"] = username
                return redirect(url_for("profile"))
            except sqlite3.IntegrityError:
                error = "That username is already taken."

    return page("Register | Crest Confessions", f"""
        <section class='section'>
            <h1 class='section-title'>Create an Account</h1>
            <p class='warning'>{error}</p>
            <form method='POST' class='card'>
                <input type='text' name='username' placeholder='Username' required>
                <input type='password' name='password' placeholder='Password' required>
                <button type='submit'>Register</button>
            </form>
        </section>
    """)


@app.route("/login", methods=["GET", "POST"])
def login():
    error = ""

    if request.method == "POST":
        username = request.form.get("username").strip()
        password = request.form.get("password")

        conn = get_db()
        user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        conn.close()

        if user and check_password_hash(user["password"], password):
            session["username"] = username
            return redirect(url_for("profile"))
        else:
            error = "Wrong username or password."

    return page("Login | Crest Confessions", f"""
        <section class='section'>
            <h1 class='section-title'>Login</h1>
            <p class='warning'>{error}</p>
            <form method='POST' class='card'>
                <input type='text' name='username' placeholder='Username' required>
                <input type='password' name='password' placeholder='Password' required>
                <button type='submit'>Login</button>
            </form>
        </section>
    """)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))


@app.route("/profile")
def profile():
    if not current_user():
        return redirect(url_for("login"))

    conn = get_db()
    tips = conn.execute("SELECT * FROM tips WHERE submitted_by = ? ORDER BY id DESC", (current_user(),)).fetchall()
    conn.close()

    if tips:
        tip_cards = "".join([
            f"""
            <div class='card'>
                <span class='tag'>{tip['category']}</span>
                <h2>{tip['name']}</h2>
                <p>{tip['tip']}</p>
                <small>{tip['created_at']}</small>
            </div>
            """
            for tip in tips
        ])
    else:
        tip_cards = "<div class='card'><h2>No tips yet</h2><p>You have not submitted anything yet.</p></div>"

    return page("Profile | Crest Confessions", f"""
        <section class='section'>
            <h1 class='section-title'>Welcome, {current_user()}</h1>
            <p>This is your account page. Your submitted tips show here.</p>
            <div class='grid'>{tip_cards}</div>
        </section>
    """)


@app.route("/submit", methods=["GET", "POST"])
def submit_tip():
    if not current_user():
        return redirect(url_for("login"))

    message = ""

    if request.method == "POST":
        name = request.form.get("name")
        category = request.form.get("category")
        tip = request.form.get("tip")
        created_at = datetime.now().strftime("%B %d, %Y at %I:%M %p")

        conn = get_db()
        conn.execute(
            "INSERT INTO tips (name, category, tip, submitted_by, created_at) VALUES (?, ?, ?, ?, ?)",
            (name, category, tip, current_user(), created_at)
        )
        conn.commit()
        conn.close()

        message = f"<div class='card'><h2>Tip Received</h2><p>Thanks, {name}. Your secret is saved... for now.</p></div>"

    return page("Submit a Tip | Crest Confessions", f"""
        <section class='section'>
            <h1 class='section-title'>Submit an Anonymous Tip</h1>
            <p>Seen something suspicious? Heard something scandalous? Tell Crest Confessions.</p>
            {message}
            <form method='POST' class='card'>
                <input type='text' name='name' placeholder='Your name or anonymous' required>
                <select name='category' required>
                    <option value='Party Drama'>Party Drama</option>
                    <option value='Relationship Rumor'>Relationship Rumor</option>
                    <option value='Family Secret'>Family Secret</option>
                    <option value='School Scandal'>School Scandal</option>
                    <option value='Crest Confessions Clue'>Crest Confessions Clue</option>
                </select>
                <textarea name='tip' rows='6' placeholder='Drop the confession here...' required></textarea>
                <button type='submit'>Send Tip</button>
            </form>
        </section>
    """)


@app.route("/admin")
def admin_page():
    conn = get_db()
    tips = conn.execute("SELECT * FROM tips ORDER BY id DESC").fetchall()
    conn.close()

    if tips:
        tip_cards = "".join([
            f"""
            <div class='card admin-box'>
                <span class='tag'>{tip['category']}</span>
                <h2>{tip['name']}</h2>
                <p>{tip['tip']}</p>
                <small>Submitted by: {tip['submitted_by']} | {tip['created_at']}</small>
            </div>
            """
            for tip in tips
        ])
    else:
        tip_cards = "<div class='card'><h2>No Tips Yet</h2><p>The halls are quiet... suspiciously quiet.</p></div>"

    return page("Admin | Crest Confessions", f"""
        <section class='section'>
            <h1 class='section-title'>Crest Confessions Admin</h1>
            <p>This page shows all submitted tips saved in the database.</p>
            <div class='grid'>{tip_cards}</div>
        </section>
    """)


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
