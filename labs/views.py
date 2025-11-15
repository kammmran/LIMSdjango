from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count
from django.http import JsonResponse
from datetime import date
from .models import Lab, Person, ResearchProject, Task, ProjectAttachment, Source
from .forms import LabForm, PersonForm, ResearchProjectForm, TaskForm, ProjectAttachmentForm, SourceForm


# ============== Dashboard ==============

@login_required
def labs_dashboard(request):
    """Main dashboard for labs module"""
    labs_count = Lab.objects.filter(is_active=True).count()
    people_count = Person.objects.filter(is_active=True).count()
    active_projects = ResearchProject.objects.filter(status='active').count()
    
    # Tasks statistics
    tasks_todo = Task.objects.filter(status='todo').count()
    tasks_in_progress = Task.objects.filter(status='in_progress').count()
    tasks_done = Task.objects.filter(status='done').count()
    
    # Upcoming deadlines
    upcoming_tasks = Task.objects.filter(
        deadline__gte=date.today(),
        status__in=['todo', 'in_progress']
    ).order_by('deadline')[:5]
    
    # Recent projects
    recent_projects = ResearchProject.objects.all()[:5]
    
    context = {
        'labs_count': labs_count,
        'people_count': people_count,
        'active_projects': active_projects,
        'tasks_todo': tasks_todo,
        'tasks_in_progress': tasks_in_progress,
        'tasks_done': tasks_done,
        'upcoming_tasks': upcoming_tasks,
        'recent_projects': recent_projects,
    }
    return render(request, 'labs/dashboard.html', context)


# ============== Labs Views ==============

@login_required
def lab_list(request):
    """List all labs"""
    query = request.GET.get('q', '')
    labs = Lab.objects.all()
    
    if query:
        labs = labs.filter(
            Q(name__icontains=query) |
            Q(code__icontains=query) |
            Q(location__icontains=query)
        )
    
    # Annotate with counts
    labs = labs.annotate(
        members_count=Count('members', filter=Q(members__is_active=True)),
        projects_count=Count('projects', filter=Q(projects__status='active'))
    )
    
    return render(request, 'labs/lab_list.html', {'labs': labs, 'query': query})


@login_required
def lab_detail(request, pk):
    """Lab detail with tabs"""
    lab = get_object_or_404(Lab, pk=pk)
    members = lab.members.filter(is_active=True)
    projects = lab.projects.all()
    tasks = lab.tasks.all()
    
    context = {
        'lab': lab,
        'members': members,
        'projects': projects,
        'tasks': tasks,
    }
    return render(request, 'labs/lab_detail.html', context)


@login_required
def lab_create(request):
    """Create a new lab"""
    if request.method == 'POST':
        form = LabForm(request.POST)
        if form.is_valid():
            lab = form.save()
            messages.success(request, f'Lab "{lab.name}" created successfully!')
            return redirect('labs:lab_detail', pk=lab.pk)
    else:
        form = LabForm()
    
    return render(request, 'labs/lab_form.html', {'form': form, 'action': 'Create'})


@login_required
def lab_update(request, pk):
    """Update an existing lab"""
    lab = get_object_or_404(Lab, pk=pk)
    
    if request.method == 'POST':
        form = LabForm(request.POST, instance=lab)
        if form.is_valid():
            form.save()
            messages.success(request, f'Lab "{lab.name}" updated successfully!')
            return redirect('labs:lab_detail', pk=lab.pk)
    else:
        form = LabForm(instance=lab)
    
    return render(request, 'labs/lab_form.html', {'form': form, 'action': 'Update', 'lab': lab})


@login_required
def lab_delete(request, pk):
    """Delete a lab"""
    lab = get_object_or_404(Lab, pk=pk)
    
    if request.method == 'POST':
        lab_name = lab.name
        lab.delete()
        messages.success(request, f'Lab "{lab_name}" deleted successfully!')
        return redirect('labs:lab_list')
    
    return render(request, 'labs/lab_confirm_delete.html', {'lab': lab})


# ============== People Views ==============

@login_required
def person_list(request):
    """List all people"""
    query = request.GET.get('q', '')
    role = request.GET.get('role', '')
    lab_id = request.GET.get('lab', '')
    
    people = Person.objects.all()
    
    if query:
        people = people.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(email__icontains=query)
        )
    
    if role:
        people = people.filter(role=role)
    
    if lab_id:
        people = people.filter(lab_id=lab_id)
    
    labs = Lab.objects.all()
    
    context = {
        'people': people,
        'query': query,
        'role': role,
        'lab_id': lab_id,
        'labs': labs,
        'role_choices': Person.ROLE_CHOICES,
    }
    return render(request, 'labs/person_list.html', context)


@login_required
def person_detail(request, pk):
    """Person detail page"""
    person = get_object_or_404(Person, pk=pk)
    projects_led = person.projects_led.all()
    projects_member = person.projects.all()
    assigned_tasks = person.assigned_tasks.all()
    
    context = {
        'person': person,
        'projects_led': projects_led,
        'projects_member': projects_member,
        'assigned_tasks': assigned_tasks,
    }
    return render(request, 'labs/person_detail.html', context)


@login_required
def person_create(request):
    """Create a new person"""
    if request.method == 'POST':
        form = PersonForm(request.POST, request.FILES)
        if form.is_valid():
            person = form.save()
            messages.success(request, f'Person "{person.full_name}" created successfully!')
            return redirect('labs:person_detail', pk=person.pk)
    else:
        form = PersonForm()
    
    return render(request, 'labs/person_form.html', {'form': form, 'action': 'Create'})


@login_required
def person_update(request, pk):
    """Update an existing person"""
    person = get_object_or_404(Person, pk=pk)
    
    if request.method == 'POST':
        form = PersonForm(request.POST, request.FILES, instance=person)
        if form.is_valid():
            form.save()
            messages.success(request, f'Person "{person.full_name}" updated successfully!')
            return redirect('labs:person_detail', pk=person.pk)
    else:
        form = PersonForm(instance=person)
    
    return render(request, 'labs/person_form.html', {'form': form, 'action': 'Update', 'person': person})


@login_required
def person_delete(request, pk):
    """Delete a person"""
    person = get_object_or_404(Person, pk=pk)
    
    if request.method == 'POST':
        person_name = person.full_name
        person.delete()
        messages.success(request, f'Person "{person_name}" deleted successfully!')
        return redirect('labs:person_list')
    
    return render(request, 'labs/person_confirm_delete.html', {'person': person})


# ============== Research Projects Views ==============

@login_required
def project_list(request):
    """List all research projects"""
    query = request.GET.get('q', '')
    status = request.GET.get('status', '')
    lab_id = request.GET.get('lab', '')
    
    projects = ResearchProject.objects.all()
    
    if query:
        projects = projects.filter(
            Q(title__icontains=query) |
            Q(summary__icontains=query)
        )
    
    if status:
        projects = projects.filter(status=status)
    
    if lab_id:
        projects = projects.filter(lab_id=lab_id)
    
    labs = Lab.objects.all()
    
    context = {
        'projects': projects,
        'query': query,
        'status': status,
        'lab_id': lab_id,
        'labs': labs,
        'status_choices': ResearchProject.STATUS_CHOICES,
    }
    return render(request, 'labs/project_list.html', context)


@login_required
def project_detail(request, pk):
    """Project detail page"""
    project = get_object_or_404(ResearchProject, pk=pk)
    tasks = project.tasks.all()
    attachments = project.attachments.all()
    
    context = {
        'project': project,
        'tasks': tasks,
        'attachments': attachments,
    }
    return render(request, 'labs/project_detail.html', context)


@login_required
def project_create(request):
    """Create a new research project"""
    if request.method == 'POST':
        form = ResearchProjectForm(request.POST)
        if form.is_valid():
            project = form.save()
            messages.success(request, f'Project "{project.title}" created successfully!')
            return redirect('labs:project_detail', pk=project.pk)
    else:
        form = ResearchProjectForm()
    
    return render(request, 'labs/project_form.html', {'form': form, 'action': 'Create'})


@login_required
def project_update(request, pk):
    """Update an existing research project"""
    project = get_object_or_404(ResearchProject, pk=pk)
    
    if request.method == 'POST':
        form = ResearchProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            messages.success(request, f'Project "{project.title}" updated successfully!')
            return redirect('labs:project_detail', pk=project.pk)
    else:
        form = ResearchProjectForm(instance=project)
    
    return render(request, 'labs/project_form.html', {'form': form, 'action': 'Update', 'project': project})


@login_required
def project_delete(request, pk):
    """Delete a research project"""
    project = get_object_or_404(ResearchProject, pk=pk)
    
    if request.method == 'POST':
        project_title = project.title
        project.delete()
        messages.success(request, f'Project "{project_title}" deleted successfully!')
        return redirect('labs:project_list')
    
    return render(request, 'labs/project_confirm_delete.html', {'project': project})


# ============== Task Views ==============

@login_required
def task_list(request):
    """List all tasks"""
    query = request.GET.get('q', '')
    status = request.GET.get('status', '')
    priority = request.GET.get('priority', '')
    
    tasks = Task.objects.all()
    
    if query:
        tasks = tasks.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query)
        )
    
    if status:
        tasks = tasks.filter(status=status)
    
    if priority:
        tasks = tasks.filter(priority=priority)
    
    context = {
        'tasks': tasks,
        'query': query,
        'status': status,
        'priority': priority,
        'status_choices': Task.STATUS_CHOICES,
        'priority_choices': Task.PRIORITY_CHOICES,
    }
    return render(request, 'labs/task_list.html', context)


@login_required
def task_kanban(request):
    """Kanban board view for tasks"""
    tasks_todo = Task.objects.filter(status='todo')
    tasks_in_progress = Task.objects.filter(status='in_progress')
    tasks_done = Task.objects.filter(status='done')
    
    context = {
        'tasks_todo': tasks_todo,
        'tasks_in_progress': tasks_in_progress,
        'tasks_done': tasks_done,
    }
    return render(request, 'labs/task_kanban.html', context)


@login_required
def task_detail(request, pk):
    """Task detail page"""
    task = get_object_or_404(Task, pk=pk)
    return render(request, 'labs/task_detail.html', {'task': task})


@login_required
def task_create(request):
    """Create a new task"""
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save()
            messages.success(request, f'Task "{task.title}" created successfully!')
            return redirect('labs:task_detail', pk=task.pk)
    else:
        form = TaskForm()
    
    return render(request, 'labs/task_form.html', {'form': form, 'action': 'Create'})


@login_required
def task_update(request, pk):
    """Update an existing task"""
    task = get_object_or_404(Task, pk=pk)
    
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            messages.success(request, f'Task "{task.title}" updated successfully!')
            return redirect('labs:task_detail', pk=task.pk)
    else:
        form = TaskForm(instance=task)
    
    return render(request, 'labs/task_form.html', {'form': form, 'action': 'Update', 'task': task})


@login_required
def task_delete(request, pk):
    """Delete a task"""
    task = get_object_or_404(Task, pk=pk)
    
    if request.method == 'POST':
        task_title = task.title
        task.delete()
        messages.success(request, f'Task "{task_title}" deleted successfully!')
        return redirect('labs:task_list')
    
    return render(request, 'labs/task_confirm_delete.html', {'task': task})


@login_required
def task_update_status(request, pk):
    """AJAX endpoint to update task status"""
    if request.method == 'POST':
        task = get_object_or_404(Task, pk=pk)
        new_status = request.POST.get('status')
        
        if new_status in dict(Task.STATUS_CHOICES):
            task.status = new_status
            if new_status == 'done':
                task.completed_date = date.today()
            task.save()
            return JsonResponse({'success': True, 'status': task.status})
    
    return JsonResponse({'success': False})


# ============== Project Attachments ==============

@login_required
def attachment_create(request, project_pk):
    """Upload attachment to a project"""
    project = get_object_or_404(ResearchProject, pk=project_pk)
    
    if request.method == 'POST':
        form = ProjectAttachmentForm(request.POST, request.FILES)
        if form.is_valid():
            attachment = form.save(commit=False)
            attachment.project = project
            # Set uploaded_by if Person model is linked to User
            try:
                person = Person.objects.get(user=request.user)
                attachment.uploaded_by = person
            except Person.DoesNotExist:
                pass
            attachment.save()
            messages.success(request, 'Attachment uploaded successfully!')
            return redirect('labs:project_detail', pk=project.pk)
    else:
        form = ProjectAttachmentForm()
    
    return render(request, 'labs/attachment_form.html', {
        'form': form,
        'project': project
    })


@login_required
def attachment_delete(request, pk):
    """Delete an attachment"""
    attachment = get_object_or_404(ProjectAttachment, pk=pk)
    project_pk = attachment.project.pk
    
    if request.method == 'POST':
        attachment.delete()
        messages.success(request, 'Attachment deleted successfully!')
        return redirect('labs:project_detail', pk=project_pk)
    
    return render(request, 'labs/attachment_confirm_delete.html', {'attachment': attachment})


# ============================================================
# Source (Customer/Patient/Lab) Views
# ============================================================

@login_required
def source_list(request):
    """List all sources with filtering"""
    sources = Source.objects.select_related('lab_reference', 'created_by').annotate(
        sample_count=Count('samples')
    )
    
    # Filter by type
    source_type = request.GET.get('type')
    if source_type:
        sources = sources.filter(source_type=source_type)
    
    # Filter by active status
    is_active = request.GET.get('active')
    if is_active:
        sources = sources.filter(is_active=is_active == 'true')
    
    # Search
    search = request.GET.get('search')
    if search:
        sources = sources.filter(
            Q(name__icontains=search) |
            Q(code__icontains=search) |
            Q(email__icontains=search) |
            Q(organization_name__icontains=search) |
            Q(patient_id__icontains=search)
        )
    
    # Get statistics by type
    source_stats = Source.objects.values('source_type').annotate(count=Count('id'))
    
    context = {
        'sources': sources,
        'source_stats': source_stats,
        'source_type': source_type,
        'is_active': is_active,
        'search': search,
    }
    return render(request, 'labs/source_list.html', context)


@login_required
def source_detail(request, pk):
    """View source details"""
    source = get_object_or_404(
        Source.objects.select_related('lab_reference', 'created_by').annotate(
            sample_count=Count('samples')
        ),
        pk=pk
    )
    
    # Get recent samples from this source
    recent_samples = source.samples.select_related(
        'processing_lab', 'originating_lab'
    ).order_by('-created_at')[:10]
    
    context = {
        'source': source,
        'recent_samples': recent_samples,
    }
    return render(request, 'labs/source_detail.html', context)


@login_required
def source_create(request):
    """Create a new source"""
    if request.method == 'POST':
        form = SourceForm(request.POST)
        if form.is_valid():
            source = form.save(commit=False)
            # Set created_by if Person exists for current user
            try:
                person = Person.objects.get(user=request.user)
                source.created_by = person
            except Person.DoesNotExist:
                pass
            source.save()
            messages.success(request, f'Source "{source.name}" created successfully!')
            return redirect('labs:source_detail', pk=source.pk)
    else:
        form = SourceForm()
    
    return render(request, 'labs/source_form.html', {'form': form, 'title': 'Add Source'})


@login_required
def source_update(request, pk):
    """Update an existing source"""
    source = get_object_or_404(Source, pk=pk)
    
    if request.method == 'POST':
        form = SourceForm(request.POST, instance=source)
        if form.is_valid():
            form.save()
            messages.success(request, f'Source "{source.name}" updated successfully!')
            return redirect('labs:source_detail', pk=source.pk)
    else:
        form = SourceForm(instance=source)
    
    return render(request, 'labs/source_form.html', {
        'form': form,
        'title': 'Edit Source',
        'source': source
    })


@login_required
def source_delete(request, pk):
    """Delete a source"""
    source = get_object_or_404(Source, pk=pk)
    
    if request.method == 'POST':
        name = source.name
        source.delete()
        messages.success(request, f'Source "{name}" deleted successfully!')
        return redirect('labs:source_list')
    
    # Check if source has samples
    sample_count = source.samples.count()
    
    return render(request, 'labs/source_confirm_delete.html', {
        'source': source,
        'sample_count': sample_count
    })

