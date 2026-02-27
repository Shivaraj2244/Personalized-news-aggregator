from django.db import models
from django.contrib.auth.models import User

class UserPreference(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    categories = models.TextField(default="technology")  # stores CSV like: "tech,sports"

    def get_categories_list(self):
        return [c.strip() for c in self.categories.split(",") if c.strip()]

    def __str__(self):
        return f"{self.user.username} - {self.categories}"
