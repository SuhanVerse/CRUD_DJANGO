from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import GroceryItem

def index(request):
    items = GroceryItem.objects.all()
    return render(request, 'grocery/index.html', {'items': items})

def toggle_completed(request, item_id):
    if request.method == 'POST':
        item = get_object_or_404(GroceryItem, id=item_id)
        item.completed = not item.completed
        item.save()
    return redirect('grocery:index')

def delete_item(request, item_id):
    if request.method == 'POST':
        item = get_object_or_404(GroceryItem, id=item_id)
        item.delete()
        messages.success(request, f"{item.name} deleted successfully!")
    return redirect('grocery:index')
