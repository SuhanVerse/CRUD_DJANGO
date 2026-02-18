from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import GroceryItem


def index(request):
    """Display all grocery items and handle edit mode"""
    items = GroceryItem.objects.all()
    edit_id = request.GET.get('edit')
    edit_item = None

    if edit_id:
        edit_item = get_object_or_404(GroceryItem, id=edit_id)

    context = {
        'items': items,
        'edit_item': edit_item,
    }
    return render(request, 'grocery/index.html', context)


def edit_item(request, item_id):
    """Redirect to index with edit parameter"""
    return redirect(f"/?edit={item_id}")


def update_item(request, item_id):
    """Update an existing grocery item name"""
    if request.method == 'POST':
        item = get_object_or_404(GroceryItem, id=item_id)
        name = request.POST.get('name', '').strip()

        if name:
            item.name = name
            item.save()

    return redirect('grocery:index')


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


def add_item(request):
    """Add a new grocery item"""
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()

        if name:
            item = GroceryItem.objects.create(name=name)
            messages.success(request, f"{item.name} added successfully!")
    return redirect('grocery:index')
