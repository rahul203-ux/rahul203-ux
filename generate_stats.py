import os
import requests
from datetime import datetime, timezone

USERNAME = "rahul203-ux"
OUTPUT_DIR = "stats"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "github-stats.svg")

TOKEN = os.environ.get("GITHUB_TOKEN")

HEADERS = {
    "Accept": "application/vnd.github+json",
    "User-Agent": "rahul203-ux-github-stats"
}

if TOKEN:
    HEADERS["Authorization"] = f"Bearer {TOKEN}"


def github_api(endpoint):
    url = f"https://api.github.com{endpoint}"

    response = requests.get(
        url,
        headers=HEADERS,
        timeout=30
    )

    if response.status_code != 200:
        raise Exception(
            f"GitHub API Error {response.status_code}: "
            f"{response.text}"
        )

    return response.json()


# ============================================================
# USER INFORMATION
# ============================================================

user = github_api(f"/users/{USERNAME}")

followers = user.get("followers", 0)
following = user.get("following", 0)
public_repos = user.get("public_repos", 0)


# ============================================================
# REPOSITORIES
# ============================================================

repos = github_api(
    f"/users/{USERNAME}/repos?per_page=100&sort=updated"
)

total_stars = 0
total_forks = 0
languages = {}

for repo in repos:

    # Ignore forked repositories
    if repo.get("fork"):
        continue

    total_stars += repo.get("stargazers_count", 0)
    total_forks += repo.get("forks_count", 0)

    repo_name = repo.get("name")

    if not repo_name:
        continue

    try:

        repo_languages = github_api(
            f"/repos/{USERNAME}/{repo_name}/languages"
        )

        for language, bytes_count in repo_languages.items():

            languages[language] = (
                languages.get(language, 0)
                + bytes_count
            )

    except Exception as error:

        print(
            f"Could not retrieve languages for "
            f"{repo_name}: {error}"
        )


# ============================================================
# TOP LANGUAGES
# ============================================================

sorted_languages = sorted(
    languages.items(),
    key=lambda item: item[1],
    reverse=True
)

top_languages = sorted_languages[:6]

total_bytes = sum(
    value for _, value in top_languages
)

language_data = []

if total_bytes > 0:

    for language, value in top_languages:

        percentage = (
            value / total_bytes
        ) * 100

        language_data.append(
            (language, percentage)
        )


# ============================================================
# LANGUAGE COLORS
# ============================================================

language_colors = {
    "Python": "#3572A5",
    "Java": "#b07219",
    "JavaScript": "#f1e05a",
    "TypeScript": "#3178c6",
    "HTML": "#e34c26",
    "CSS": "#563d7c",
    "C": "#555555",
    "C++": "#f34b7d",
    "C#": "#178600",
    "Jupyter Notebook": "#DA5B0B",
    "Shell": "#89e051",
    "Dart": "#00B4AB",
    "Go": "#00ADD8",
    "PHP": "#4F5D95",
    "Kotlin": "#A97BFF",
    "Swift": "#F05138"
}


# ============================================================
# GENERATE LANGUAGE BARS
# ============================================================

language_svg = ""

x_position = 35
bar_y = 245

for language, percentage in language_data:

    color = language_colors.get(
        language,
        "#8b949e"
    )

    bar_width = max(
        percentage * 5,
        3
    )

    language_svg += f"""
    <text
        x="{x_position}"
        y="{bar_y}"
        fill="#c9d1d9"
        font-size="14"
        font-family="Arial, sans-serif">
        {language}
    </text>

    <rect
        x="{x_position}"
        y="{bar_y + 10}"
        width="{bar_width}"
        height="8"
        rx="4"
        fill="{color}">
    </rect>

    <text
        x="{x_position + bar_width + 10}"
        y="{bar_y + 18}"
        fill="#8b949e"
        font-size="12"
        font-family="Arial, sans-serif">
        {percentage:.1f}%
    </text>
    """

    bar_y += 45


# ============================================================
# GENERATE SVG
# ============================================================

os.makedirs(
    OUTPUT_DIR,
    exist_ok=True
)

updated = datetime.now(
    timezone.utc
).strftime("%Y-%m-%d %H:%M UTC")


svg = f"""<svg
xmlns="http://www.w3.org/2000/svg"
width="800"
height="520"
viewBox="0 0 800 520">

<rect
width="800"
height="520"
rx="15"
fill="#0d1117"/>

<!-- TITLE -->

<text
x="35"
y="45"
fill="#58a6ff"
font-size="25"
font-weight="bold"
font-family="Arial, sans-serif">

GitHub Statistics

</text>

<text
x="35"
y="72"
fill="#8b949e"
font-size="14"
font-family="Arial, sans-serif">

@{USERNAME}

</text>


<!-- REPOSITORIES -->

<text
x="35"
y="120"
fill="#8b949e"
font-size="14"
font-family="Arial, sans-serif">

Public Repositories

</text>

<text
x="35"
y="150"
fill="#ffffff"
font-size="26"
font-weight="bold"
font-family="Arial, sans-serif">

{public_repos}

</text>


<!-- FOLLOWERS -->

<text
x="220"
y="120"
fill="#8b949e"
font-size="14"
font-family="Arial, sans-serif">

Followers

</text>

<text
x="220"
y="150"
fill="#ffffff"
font-size="26"
font-weight="bold"
font-family="Arial, sans-serif">

{followers}

</text>


<!-- FOLLOWING -->

<text
x="380"
y="120"
fill="#8b949e"
font-size="14"
font-family="Arial, sans-serif">

Following

</text>

<text
x="380"
y="150"
fill="#ffffff"
font-size="26"
font-weight="bold"
font-family="Arial, sans-serif">

{following}

</text>


<!-- STARS -->

<text
x="535"
y="120"
fill="#8b949e"
font-size="14"
font-family="Arial, sans-serif">

Stars

</text>

<text
x="535"
y="150"
fill="#ffffff"
font-size="26"
font-weight="bold"
font-family="Arial, sans-serif">

{total_stars}

</text>


<!-- FORKS -->

<text
x="665"
y="120"
fill="#8b949e"
font-size="14"
font-family="Arial, sans-serif">

Forks

</text>

<text
x="665"
y="150"
fill="#ffffff"
font-size="26"
font-weight="bold"
font-family="Arial, sans-serif">

{total_forks}

</text>


<!-- DIVIDER -->

<line
x1="35"
y1="180"
x2="765"
y2="180"
stroke="#30363d"
stroke-width="1"/>


<!-- LANGUAGES -->

<text
x="35"
y="215"
fill="#58a6ff"
font-size="18"
font-weight="bold"
font-family="Arial, sans-serif">

Top Languages

</text>

{language_svg}


<!-- FOOTER -->

<text
x="35"
y="490"
fill="#6e7681"
font-size="11"
font-family="Arial, sans-serif">

Updated: {updated}

</text>

</svg>
"""


# ============================================================
# SAVE FILE
# ============================================================

with open(
    OUTPUT_FILE,
    "w",
    encoding="utf-8"
) as file:

    file.write(svg)


print(
    f"GitHub statistics successfully generated: "
    f"{OUTPUT_FILE}"
)
