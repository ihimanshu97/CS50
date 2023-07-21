from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse

from markdown2 import markdown
from  random import choice

from . import util


def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

def title(request, title):
    entry = util.get_entry(title)

    if entry == None:
        return render(request, "encyclopedia/error.html", {
                "error": "Not Found",
                "message": f"<b>Requested Page Not Found</b>"
        })

    return render(request, 'encyclopedia/entry.html', {
        # Proper Title rather than title entered by user
        "title": util.actualTitle(title),
        "entry": markdown(entry)
    })

def search(request):
    # Get Query, and erase whitespaces around query
    q = request.GET['q'].strip()

    # All entries in wiki
    entries = util.list_entries()

    # Check all possibilities of query
    if q.lower() in entries or q.upper() in entries or q.capitalize() in entries:
        # Redirect user to query's page
        return HttpResponseRedirect(reverse('title', kwargs={"title": q}))
    
    # Keeps track of entries whose substring is query (case in-sensitive)
    substrings = []
    for entry in entries:
        if q.lower() in entry.lower():
            substrings.append(entry)

    # No Results
    if len(substrings) == 0:
        return render(request, "encyclopedia/error.html", {
                "error": "No Results",
                "message": f"<b>NO RESULTS</b> for query {q}"
        })

    # Display all results found
    return render(request, 'encyclopedia/search.html', {
        "q": q,
        "substrings": substrings
    })
        
def new(request):
    if request.method == "POST":
        # Get Title
        title = request.POST['title']

        # Get content
        content = request.POST['content']

        # All entries in wiki
        entries = util.list_entries()

        # Check if new entry is already present in wiki
        if title.lower() in entries or title.upper() in entries or title.capitalize() in entries:
            # if present, let user know about it and don't save new entry
            return render(request, "encyclopedia/error.html", {
                "error": "Already Exists",
                "message": "The page you want to add, <b>ALREADY EXISTS</b> in wiki"
            })
        
        # Add new entry
        util.save_entry(title, content)
        return HttpResponseRedirect(reverse('title', kwargs={"title": title}))

    return render(request, 'encyclopedia/new.html')

def edit(request, title):
    if request.method == "POST":
        # Get content after editing
        content = request.POST['content']
        
        # Save edits
        util.save_entry(title, content)
        return HttpResponseRedirect(reverse('title', kwargs={"title": title}))

    return render(request, 'encyclopedia/edit.html', {
        "title": title,
        # Content of page, that is to be edited
        "content": util.get_entry(title)
    })

def random(request):
    # All entries in wiki
    entries = util.list_entries()

    # Choose a random title
    title = choice(entries)

    # Redirect user to title's page
    return HttpResponseRedirect(reverse('title', kwargs={"title": title}))