import requests
import json

HANDLE = "Yakurto"

def fetch_submissions(handle):
    url = f"https://codeforces.com/api/user.status?handle={handle}"
    response = requests.get(url)
    return response.json()

def fetch_rating_history(handle):
    url = f"https://codeforces.com/api/user.rating?handle={handle}"
    response = requests.get(url)
    return response.json()

def fetch_problemset():
    url = "https://codeforces.com/api/problemset.problems"
    response = requests.get(url)
    return response.json()

if __name__ == "__main__":
    submissions = fetch_submissions(HANDLE)
    rating_history = fetch_rating_history(HANDLE)
    problemset = fetch_problemset()

    with open("submissions.json", "w") as f:
        json.dump(submissions, f, indent=2)

    with open("rating_history.json", "w") as f:
        json.dump(rating_history, f, indent=2)

    with open("problemset.json", "w") as f:
        json.dump(problemset, f, indent=2)

    print(f"Saved {len(submissions.get('result', []))} submissions")
    print(f"Saved {len(rating_history.get('result', []))} rating changes")
    print(f"Saved {len(problemset.get('result', {}).get('problems', []))} problems from problemset")
