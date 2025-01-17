from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from core.models import Review
from django.db.models import Avg


@receiver(post_save, sender=Review)
def update_watchlist_on_review_save(sender, instance, **kwargs):
    """Update total_reviews and average_rating on Review save."""
    watchlist = instance.watchlist
    reviews = watchlist.reviews.all()
    total_reviews = reviews.count()
    average_rating = (reviews.aggregate(avg_rating=Avg('rating'))['avg_rating']
                      or 0)

    watchlist.total_reviews = total_reviews
    watchlist.average_rating = average_rating
    watchlist.save()


@receiver(post_delete, sender=Review)
def update_watchlist_on_review_delete(sender, instance, **kwargs):
    """Update total_reviews and average_rating on Review delete."""
    watchlist = instance.watchlist
    reviews = watchlist.reviews.all()
    total_reviews = reviews.count()
    average_rating = (reviews.aggregate(avg_rating=Avg('rating'))['avg_rating']
                      or 0)

    watchlist.total_reviews = total_reviews
    watchlist.average_rating = average_rating
    watchlist.save()
