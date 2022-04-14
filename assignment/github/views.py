from ast import keyword
from asyncio.windows_events import NULL
from socket import if_indextoname
from urllib.request import urlopen
from django.http import HttpResponse
from django.shortcuts import redirect, render
from .forms import GithubKeywords, StackoverflowKeywords
import urllib.request
import requests
from bs4 import BeautifulSoup
import psycopg2
from stackapi import StackAPI
# Create your views here.

def about(request):
    return render( request, "github/about.html")
def index(request):
    return render( request, "github/home.html")
def github_details(request):
    index = []
    usernames = []
    names = []
    bio = []
    location = []
    followers = []
    followings = []
    repo_num = []
    project_num = []
    star_num = []
    link = []
    ind = []
    data_github(ind, index, names, usernames, bio, location, followers, followings, repo_num, project_num, star_num, link )
    return render( request, "github/github_details.html", {"ind": ind, "index": index, "names": names, "usernames": usernames, "bio": bio, "location": location, "followers": followers, "followings": followings, "repo_num": repo_num, "project_num": project_num, "star_num" : star_num, "link": link })
def stackoverflow_details(request):
    index = []
    username = []
    name = []
    reputation = []
    reached = []
    questions = []
    answers = []
    member_time = []
    link = []
    ind = []
    keyword = []
    data_stackoverflow(ind, index, keyword, name, username, reputation, reached, questions, answers, member_time, link)
    return render( request, "github/stackoverflow_details.html", {"ind" : ind, "index": index, "keyword": keyword, "name": name, "username": username, "reputation": reputation, "reached": reached, "questions": questions, "answers": answers, "member_time": member_time, "link": link})

def github(request):

    if request.method == 'POST':
        form = GithubKeywords(request.POST)

        if form.is_valid():
            global keywords
            keywords = form.cleaned_data['keyword']
            canditate_num = form.cleaned_data['candidate_num']
            sorting = form.cleaned_data['sorting']
            sort_type = form.cleaned_data['sort_type']
            usernames = []
            names = []
            bio = []
            location = []
            followers = []
            followings = []
            repo_num = []
            project_num = []
            star_num = []
            if canditate_num % 10 != 0:
                page = int( canditate_num / 10) + 1
            else:
                page = int( canditate_num / 10)
            for k in range( page):
                if sort_type == "best match":
                    url = "https://github.com/search?o=" + "&p=" + str(k + 1) + "&q=" + add_plus(keywords) + "&type=users"
                else:
                    url = "https://github.com/search?o=" + sorting + "&p=" + str(k + 1) + "&q=" + add_plus(keywords) + "&s=" + sort_type + "&type=users"
                resp_text = urllib.request.urlopen(url).read().decode('UTF-8')
                soup = BeautifulSoup( resp_text, "html.parser")
                text_git = soup.get_text()
                flag = False
                text_arr = text_git.splitlines()
                text_list = []
                count = 0
                for index in range( len(text_arr)):
                        if text_arr[index - 15] == "Fewest repositories":
                            count = count + 1
                            if count > 1:
                                flag = True
                        if text_arr[index] == "Previous 1 2 3 4 5 … 99 100 Next":
                            flag = False
                        if flag:
                            text_list.append( text_arr[index])
                for index in range( len(text_list)):
                    if  len(usernames) < canditate_num:
                        if text_list[index] == "Follow" and text_list[index - 4] != "Sponsor":
                            usernames.append(text_list[index - 5])
                            names.append( text_list[index - 6])
                            bio.append( text_list[index + 5].strip())
                            location.append( text_list[index + 8].strip())
                        elif text_list[index] == "Follow" and text_list[index - 4] == "Sponsor":
                            usernames.append(text_list[index - 11])
                            names.append( text_list[index - 12])
                            bio.append( text_list[index + 5].strip())
                            location.append( text_list[index + 8].strip())
            for index in range( canditate_num ):
                url = "https://github.com/" + usernames[index]
                resp_text = urllib.request.urlopen(url).read().decode('UTF-8')
                soup = BeautifulSoup( resp_text, "html.parser")
                text_git = soup.get_text()
                text_arr = text_git.splitlines()
                for i in range( len(text_arr)):
                    if text_arr[i].strip() == "following" and text_arr[i  - 3].strip() == "followers" :
                        followers.append(text_arr[i - 4])
                        followings.append( text_arr[i - 1])
                    if "Contact GitHub support about this user’s behavior." in text_arr[i]:
                        repo_num.append( text_arr[i + 24].strip())
                        project_num.append( text_arr[i + 31].strip())
                        star_num.append( text_arr[i + 45].strip())
                if len(followers) != index + 1:
                    followers.append(NULL)
                if len( followings) != index + 1:
                    followings.append(NULL)

            try:
                connection = psycopg2.connect(user="postgres",
                                    password="Victus.3141",
                                    host="127.0.0.1",
                                    port="5432",
                                    database="scrapingForRecruiters")
                cursor = connection.cursor()
                postgres_insert_query = """DELETE FROM github_candidates"""
                cursor.execute(postgres_insert_query)
                for i in range(canditate_num):
                    postgres_insert_query = """ INSERT INTO github_candidates (keyword, sorting, sort_type, username, name, bio, location, followers, followings, repo_num, project_num, star_num) VALUES (%s,%s,%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
                    record_to_insert = (keywords, sorting, sort_type, usernames[i], names[i], bio[i], location[i], followers[i], followings[i], repo_num[i], project_num[i], star_num[i])
                    cursor.execute(postgres_insert_query, record_to_insert)

                connection.commit()
                count = cursor.rowcount
                print(count, "Record inserted successfully into mobile table")
            except (Exception, psycopg2.Error) as error:
                print("Failed to insert record into mobile table", error)
            finally:
                # closing database connection.
                if connection:
                    cursor.close()
                    connection.close()
                    print("PostgreSQL connection is closed")
    
    form = GithubKeywords()
    return render(request, 'github/github.html', {'form': form})

def stackoverflow(request):
    if request.method == 'POST':
        form = StackoverflowKeywords(request.POST)
        if form.is_valid():
            global keywords
            keywords = form.cleaned_data['keyword']
            canditate_num = form.cleaned_data['candidate_num']
            SITE = StackAPI('stackoverflow')
            SITE.max_pages = 1
            users = SITE.fetch('posts', tagged=keywords)
            sof_link = []
            sof_username = []
            sof_name = []
            sof_user_id = []
            users = users['items'][:canditate_num]
            for index in users:
                sof_link.append(index['owner']['link'])
                sof_user_id.append( index['owner']['user_id'])
                sof_name.append( index['owner']['display_name'])
                sof_username.append( add_slash(index['owner']['display_name']).lower())
            sof_reputation = []
            sof_reached = []
            sof_member_time = []
            sof_questions = []
            sof_answers = []
            for index in sof_link: 
                resp_text = urllib.request.urlopen(index).read().decode('UTF-8')
                soup = BeautifulSoup( resp_text, "html.parser")
                text_git = soup.get_text()
                text_arr = text_git.splitlines()
                for i in range( len(text_arr)):
                    if "reputation" in text_arr[i] and len(text_arr[i - 1]) < 10:
                        sof_reputation.append( text_arr[i-1])
                    if "reached" in text_arr[i] and len(text_arr[i - 1]) < 10:
                        sof_reached.append( text_arr[i-1])
                    if "answers" in text_arr[i]  and len(text_arr[i - 1]) < 10:
                        sof_answers.append( text_arr[i - 1])
                    if "questions" in text_arr[i] and len(text_arr[i - 1]) < 10:
                        sof_questions.append( text_arr[i - 1])
                    if "Member for" in text_arr[i]:
                        sof_member_time.append( text_arr[i])
            try:
                connection = psycopg2.connect(user="postgres",
                                    password="Victus.3141",
                                    host="127.0.0.1",
                                    port="5432",
                                    database="scrapingForRecruiters")
                cursor = connection.cursor()
                postgres_insert_query = """DELETE FROM stackoverflow_candidates"""
                cursor.execute(postgres_insert_query)
                for i in range(canditate_num):
                    postgres_insert_query = """ INSERT INTO stackoverflow_candidates (keyword, username, name, reputation, reached, questions, answers, member_time, sof_link) VALUES (%s,%s,%s, %s, %s, %s, %s, %s, %s)"""
                    record_to_insert = (keywords, sof_username[i], sof_name[i], sof_reputation[i], sof_reached[i], sof_questions[i], sof_answers[i], sof_member_time[i], sof_link[i])
                    cursor.execute(postgres_insert_query, record_to_insert)

                connection.commit()
                count = cursor.rowcount
                print(count, "Record inserted successfully into mobile table")
            except (Exception, psycopg2.Error) as error:
                print("Failed to insert record into mobile table", error)
            finally:
                # closing database connection.
                if connection:
                    cursor.close()
                    connection.close()
                    print("PostgreSQL connection is closed")
    form = StackoverflowKeywords()    
    return render( request, 'github/stackoverflow.html', {"form": form})
def add_plus(keywords):
	keywords = keywords.split()
	keyword_edited = ""
	for i in keywords:
		keyword_edited += i + "+"
	keyword_edited = keyword_edited[:-1]
	return keyword_edited

def add_slash(keywords):
	keywords = keywords.split()
	keyword_edited = ""
	for i in keywords:
		keyword_edited += i + "-"
	keyword_edited = keyword_edited[:-1]
	return keyword_edited

def data_stackoverflow(ind, index, keyword, name, username, reputation, reached, questions, answers, member_time, link):
            #establishing the connection
    conn = psycopg2.connect(user="postgres",
                                    password="Victus.3141",
                                    host="127.0.0.1",
                                    port="5432",
                                    database="scrapingForRecruiters")
    #Setting auto commit false
    conn.autocommit = True

    #Creating a cursor object using the cursor() method
    cursor = conn.cursor()

    #Retrieving data
    cursor.execute('''SELECT * from stackoverflow_candidates ORDER BY id DESC''')

    #Fetching 1st row from the table
    i = 1
    result = cursor.fetchall()
    length = len( result)
    for row in result:
        index.append( length - i + 1)
        ind.append( length - i)
        i = i + 1
        name.append( row[3])
        keyword.append( row[1])
        username.append( row[2])
        reputation.append( row[4])
        reached.append( row[5])
        questions.append( row[6])
        answers.append( row[7])
        member_time.append( row[8])
        link.append( row[9])
    #Commit your changes in the database
    conn.commit()

    #Closing the connection
    conn.close()
def data_github(ind, index, name, username, bio, location, follower, following, repo_num, project_num, stars, link):
            #establishing the connection
    conn = psycopg2.connect(user="postgres",
                                    password="Victus.3141",
                                    host="127.0.0.1",
                                    port="5432",
                                    database="scrapingForRecruiters")
    #Setting auto commit false
    conn.autocommit = True

    #Creating a cursor object using the cursor() method
    cursor = conn.cursor()

    #Retrieving data
    cursor.execute('''SELECT * from github_candidates ORDER BY id DESC''')

    #Fetching 1st row from the table
    i = 1
    result = cursor.fetchall()
    length = len( result)
    for row in result:
        index.append( length - i + 1)
        ind.append( length - i)
        i = i + 1
        name.append( row[5])
        username.append( row[4])
        bio.append( row[6])
        location.append( row[7])
        follower.append( row[8])
        following.append( row[9])
        repo_num.append( row[10])
        project_num.append( row[11])
        stars.append( row[12])
        link.append("github.com/" + row[4] )
    #Commit your changes in the database
    conn.commit()

    #Closing the connection
    conn.close()
