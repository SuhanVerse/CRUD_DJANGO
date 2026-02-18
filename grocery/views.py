from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import GroceryItem


def index(request):
    """Display all grocery items and handle inline edit mode."""
    items = GroceryItem.objects.all()
    edit_id = request.GET.get('edit')
    edit_item = None

    if edit_id:
        try:
            edit_item = GroceryItem.objects.get(id=edit_id)
        except GroceryItem.DoesNotExist:
            pass  

    context = {
        'items': items,
        'edit_item': edit_item,
    }
    return render(request, 'grocery/index.html', context)


def add_item(request):
    """Add a new grocery item."""
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        if name:
            item = GroceryItem.objects.create(name=name)
            messages.success(request, f'"{item.name}" added successfully!')
        else:
            messages.error(request, 'Item name cannot be empty.')
    return redirect('grocery:index')


def edit_item(request, item_id):
    """Redirect to the index with the edit query parameter."""
    # Verify item exists before redirecting
    get_object_or_404(GroceryItem, id=item_id)
    return redirect(f'/?edit={item_id}')


def update_item(request, item_id):
    """Update an existing grocery item's name."""
    if request.method == 'POST':
        item = get_object_or_404(GroceryItem, id=item_id)
        name = request.POST.get('name', '').strip()
        if name:
            old_name = item.name
            item.name = name
            item.save()
            messages.success(
                request, f'"{old_name}" updated to "{item.name}"!')
        else:
            messages.error(request, 'Item name cannot be empty.')
    return redirect('grocery:index')


def toggle_completed(request, item_id):
    """Toggle the completed status of a grocery item."""
    if request.method == 'POST':
        item = get_object_or_404(GroceryItem, id=item_id)
        item.completed = not item.completed
        item.save()
        status = 'completed' if item.completed else 'uncompleted'
        messages.success(request, f'"{item.name}" marked as {status}.')
    return redirect('grocery:index')


def delete_item(request, item_id):
    """Delete a grocery item."""
    if request.method == 'POST':
        item = get_object_or_404(GroceryItem, id=item_id)
        item_name = item.name 
        item.delete()
        messages.success(request, f'"{item_name}" deleted successfully.')
    return redirect('grocery:index')
