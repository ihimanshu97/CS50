from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.db.models import Max
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_GET, require_POST

from .models import *
from .forms import *


def index(request):
    return render(request, "auctions/index.html", {
        "listings": Listing.objects.filter(winner=None)
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")




@login_required
def create(request):
    if request.method == "POST":
        form = NewListing(request.POST)

        if form.is_valid:
            # Add new listing
            new_listing = Listing(
                creater=request.user, 
                title=request.POST["title"], 
                description=request.POST["description"], 
                current_price=request.POST["current_price"],
                image=request.POST["image"],
                category=Category.objects.get(pk=int(request.POST["category"]))
            )
            new_listing.save()

            return HttpResponseRedirect(reverse("index"))

    return render(request, "auctions/create.html",{
        "form": NewListing()
    })

def listing(request, listing_id):
    listing = Listing.objects.get(pk=listing_id)
    
    # No. of bids on listing
    no_of_bids = Bid.objects.filter(listing=listing).count()

    if no_of_bids == 0:
        # If there are 0 bids, the min. bid amount must be the amount choosen
        min_bid = listing.current_price
    else:
        # Else the min. bid amount must be greater than highest bid(i.e, current_price + 1)
        min_bid = listing.current_price + 1

    # Check if listing is added to watchlist
    if request.user.is_authenticated:
        added = len(Watchlist.objects.filter(listing=listing, user=request.user))
    else:
        added = False
    
    return render(request, "auctions/listing.html", {
        "listing": listing,
        "added": added,
        "min_bid": min_bid,
        "creater": request.user == listing.creater,
        "commentform": NewComment(),
        "comments": listing.comments.all()
    })

@login_required
@require_POST
def edit_watchlist(request, listing_id):
    listing = Listing.objects.get(pk=listing_id)
    onwatch = Watchlist.objects.filter(listing=listing, user=request.user)

    if len(onwatch) == 0:
        # Add to watchlist
        add = Watchlist(listing=listing, user=request.user)
        add.save()
    else:
        # Remove from watchlist
        onwatch.delete()

    return HttpResponseRedirect(reverse("listing", kwargs={"listing_id": listing_id}))

@login_required
@require_POST
def bid(request, listing_id):
    listing = Listing.objects.get(pk=listing_id)
    
    newbid = int(request.POST["bid"])
    current_price = listing.current_price

    if newbid < current_price:
        return render(request, "auctions/error.html", {
            "message": "Invalid Bid"
        })

    # Get latest(i.e, highest bid)
    latest_bid = Bid.objects.filter(listing=listing).aggregate(Max('bid'))['bid__max']

    if latest_bid != None and newbid == latest_bid:
        return render(request, "auctions/error.html", {
            "message": "Invalid Bid"
        })

    # Save the bid and update current_price
    bid = Bid(listing=listing, bidder=request.user, bid=newbid)
    bid.save()
    listing.current_price = newbid
    listing.save()

    return HttpResponseRedirect(reverse("listing", kwargs={"listing_id": listing_id}))

@login_required
@require_POST
def close(request, listing_id):
    listing = Listing.objects.get(pk=listing_id)

    # Highest Bid
    current_price = Bid.objects.filter(listing=listing).aggregate(Max('bid'))['bid__max']

    if current_price == None:
        return render(request, "auctions/error.html", {
            "message": "As there are no bids on your listing, you can't close the auction now"
        })

    # Declare highest bidder as winner
    listing.winner = Bid.objects.get(listing=listing, bid=current_price).bidder
    listing.save()

    return HttpResponseRedirect(reverse("listing", kwargs={"listing_id": listing_id}))

@login_required
@require_POST
def comment(request, listing_id):
    comment_text = request.POST['comment']
    listing = Listing.objects.get(pk=listing_id)

    # Save the comment
    comment = Comment(listing=listing, user=request.user, comment=comment_text)
    comment.save()
    return HttpResponseRedirect(reverse("listing", kwargs={"listing_id": listing_id}))

@login_required
def view_watchlist(request):
    return render(request, "auctions/watchlist.html", {
        "watchlist": request.user.watchlist.all()
    })

def categories(request):
    return render(request, "auctions/categories.html", {
        "categories": Category.objects.all()
    })

def category(request, category):
    category = Category.objects.get(category=category)
    return render(request, "auctions/category.html", {
        "category": category,
        "listings": category.listings.all()
    })