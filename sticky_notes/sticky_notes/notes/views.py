# note/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from .models import Note
from .forms import NoteForm


def note_list(request):
    """
    View to display a list of all notes.

    :param request: HTTP request object.
    :return: Rendered template with a list of notes.
    """
    notes = Note.objects.all()

    # Creating a context dictionary to pass data
    context = {
        "notes": notes,
        "page_title": "List of Notes",
    }

    return render(request, "notes/note_list.html", context)


def note_detail(request, pk):
    """
    View to display details of a specific note.

    :param request: HTTP request object.
    :param pk: Primary key of the note.
    :return: Rendered template with details of the specified note.
    """
    note = get_object_or_404(Note, pk=pk)
    return render(request, "notes/note_detail.html", {"note": note})


def note_create(request):
    """
    View to create a new note.

    :param request: HTTP request object.
    :return: Rendered template for creating a new note.
    """
    if request.method == "POST":
        form = NoteForm(request.POST)
        if form.is_valid():
            note = form.save(commit=False)
            note.save()
            return HttpResponse(note_close("note_list"))
    else:
        form = NoteForm()
    return render(request, "notes/note_form.html", {"form": form})


def note_update(request, pk):
    """
    View to update an existing note.

    :param request: HTTP request object.
    :param pk: Primary key of the note to be updated.
    :return: Rendered template for updating the specified note.
    """
    note = get_object_or_404(Note, pk=pk)
    if request.method == "POST":
        form = NoteForm(request.POST, instance=note)
        if form.is_valid():
            note = form.save(commit=False)
            note.save()
            return HttpResponse(note_close("note_list"))
    else:
        form = NoteForm(instance=note)
    return render(request, "notes/note_form.html", {"form": form})


def note_delete(request, pk):
    """
    View to delete an existing note.

    :param request: HTTP request object.
    :param pk: Primary key of the note to be deleted.
    :return: Redirect to the note list after deletion.
    """
    note = get_object_or_404(Note, pk=pk)
    note.delete()
    return HttpResponse(note_close("note_list"))


def note_return(request):

    return HttpResponse(note_close("note_list"))


def note_close(request):
    """
    View that closes the popup and refreshes the parent window.
    """
    html = """
    <script type="text/javascript">
        if (window.opener && !window.opener.closed) {
            window.opener.focus();
            window.opener.location.reload(); // Refresh parent
        }
        window.close(); // Close popup
    </script>
    """
    return html
