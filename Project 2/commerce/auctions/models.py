from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):

    def __str__(self):
        return f"{self.username}"

class Category(models.Model):
    category = models.CharField(max_length=32)

    def __str__(self):
        return f"{self.category}"

class Listing(models.Model):
    creater = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listings")
    title = models.CharField(max_length=150)
    description = models.TextField()
    current_price = models.IntegerField()
    image = models.URLField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="listings")
    winner = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title}"

class Bid(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    bidder = models.ForeignKey(User, on_delete=models.CASCADE)
    bid = models.IntegerField()
    date_bid = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.bid} on {self.listing.title} by {self.bidder.username}"

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="comments")
    comment = models.CharField(max_length=300)
    date_commented = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user} on {self.listing}"

class Watchlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="watchlist")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user} | {self.listing}"