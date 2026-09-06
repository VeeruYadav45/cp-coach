import requests#this lets me make http calls over internet using codeforces api
import json#lets us parse what is parse???

HANDLE = "Yakurto"#a constant it holds my username
#this function builts a url using public api 
def fetch_submissions(handle):
    url = f"https://codeforces.com/api/user.status?handle={handle}"
    response = requests.get(url)#send https request and wait for response 
    return response.json()#takes raw response as json text and converts to dic luist
#for rating change only
def fetch_rating_history(handle):
    url = f"https://codeforces.com/api/user.rating?handle={handle}"
    response = requests.get(url)
    return response.json()

if __name__ == "__main__":#this condition makes sure it is run directly not imported else wher 
    submissions = fetch_submissions(HANDLE)
    rating_history = fetch_rating_history(HANDLE)

    with open("submissions.json", "w") as f:
        json.dump(submissions, f, indent=2)#makes json file humanly readable

    with open("rating_history.json", "w") as f:
        json.dump(rating_history, f, indent=2)

    print(f"Saved {len(submissions.get('result', []))} submissions")
    print(f"Saved {len(rating_history.get('result', []))} rating changes")