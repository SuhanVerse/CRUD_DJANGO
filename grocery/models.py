from django.db import models


class GroceryItem(models.Model):
    name = models.CharField(max_length=200)
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Grocery Item'
        verbose_name_plural = 'Grocery Items'
