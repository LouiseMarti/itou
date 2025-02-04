from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied, ValidationError
from django.db.models import Count
from django.http.response import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils.encoding import escape_uri_path

from itou.employee_record.models import EmployeeRecord
from itou.job_applications.models import JobApplication
from itou.users.models import JobSeekerProfile
from itou.utils.pagination import pager
from itou.utils.perms.employee_record import can_create_employee_record, siae_is_allowed
from itou.utils.perms.siae import get_current_siae_or_404
from itou.www.employee_record_views.forms import (
    NewEmployeeRecordStep1Form,
    NewEmployeeRecordStep2Form,
    NewEmployeeRecordStep3Form,
    NewEmployeeRecordStep4,
    SelectEmployeeRecordStatusForm,
)


# Labels and steps for multi-steps component
STEPS = [
    (
        1,
        "Etat civil",
    ),
    (
        2,
        "Domiciliation",
    ),
    (
        3,
        "Situation",
    ),
    (
        4,
        "Annexe financière",
    ),
    (
        5,
        "Validation",
    ),
]


# Views


@login_required
def list(request, template_name="employee_record/list.html"):
    """
    Displays a list of employee records for the SIAE
    """
    siae = get_current_siae_or_404(request)

    if not siae.can_use_employee_record:
        raise PermissionDenied

    form = SelectEmployeeRecordStatusForm(data=request.GET or None)
    status = EmployeeRecord.Status.NEW

    # Employee records are created with a job application object
    # At this stage, new job applications / hirings do not have
    # an associated employee record object
    # Objects in this list can be either:
    # - employee records: iterate on their job application object
    # - basic job applications: iterate as-is
    employee_records_list = True

    navigation_pages = None
    data = None

    # Construct badges

    # Badges for "real" employee records
    employee_record_statuses = (
        EmployeeRecord.objects.filter(job_application__to_siae=siae)
        .values("status")
        .annotate(cnt=Count("status"))
        .order_by("-status")
    )
    employee_record_badges = {row["status"]: row["cnt"] for row in employee_record_statuses}

    # Set count of each status for badge display
    status_badges = [
        (
            JobApplication.objects.eligible_as_employee_record(siae).count(),
            "info",
        ),
        (employee_record_badges.get(EmployeeRecord.Status.READY, 0), "secondary"),
        (employee_record_badges.get(EmployeeRecord.Status.SENT, 0), "warning"),
        (employee_record_badges.get(EmployeeRecord.Status.REJECTED, 0), "danger"),
        (employee_record_badges.get(EmployeeRecord.Status.PROCESSED, 0), "success"),
    ]

    # Override defaut value (NEW status)
    # See comment above on `employee_records_list` var
    if form.is_valid():
        status = form.cleaned_data["status"]

    # Not needed every time (not pulled-up), and DRY here
    base_query = EmployeeRecord.objects.full_fetch()

    if status == EmployeeRecord.Status.NEW:
        data = JobApplication.objects.eligible_as_employee_record(siae)
        employee_records_list = False
    elif status == EmployeeRecord.Status.READY:
        data = base_query.ready_for_siae(siae)
    elif status == EmployeeRecord.Status.SENT:
        data = base_query.sent_for_siae(siae)
    elif status == EmployeeRecord.Status.REJECTED:
        data = EmployeeRecord.objects.rejected_for_siae(siae)
    elif status == EmployeeRecord.Status.PROCESSED:
        data = base_query.processed_for_siae(siae)

    if data:
        navigation_pages = pager(data, request.GET.get("page", 1), items_per_page=10)

    context = {
        "form": form,
        "employee_records_list": employee_records_list,
        "badges": status_badges,
        "navigation_pages": navigation_pages,
        "feature_availability_date": settings.EMPLOYEE_RECORD_FEATURE_AVAILABILITY_DATE,
    }

    return render(request, template_name, context)


@login_required
def create(request, job_application_id, template_name="employee_record/create.html"):
    """
    Create a new employee record from a given job application

    Step 1: Name and birth date / place / country of the jobseeker
    """
    job_application = can_create_employee_record(request, job_application_id)

    form = NewEmployeeRecordStep1Form(data=request.POST or None, instance=job_application.job_seeker)
    step = 1

    if request.method == "POST" and form.is_valid():
        form.save()

        # Create jobseeker_profile if needed
        employee = job_application.job_seeker
        profile, _ = JobSeekerProfile.objects.get_or_create(user=employee)

        # Try a geo lookup of the address every time we call this form
        try:
            profile.update_hexa_address()
        except ValidationError:
            # cleanup address
            profile.clear_hexa_address()

        return HttpResponseRedirect(reverse("employee_record_views:create_step_2", args=(job_application.id,)))

    context = {
        "job_application": job_application,
        "form": form,
        "steps": STEPS,
        "step": step,
    }

    return render(request, template_name, context)


@login_required
def create_step_2(request, job_application_id, template_name="employee_record/create.html"):
    """
    Create a new employee record from a given job application

    Step 2: Details and address lookup / check of the employee
    """
    job_application = can_create_employee_record(request, job_application_id)
    job_seeker = job_application.job_seeker

    if not job_seeker.has_jobseeker_profile:
        raise PermissionDenied

    # Conditions:
    # - employee record is in an updatable state (if exists)
    # - target job_application / employee record must be linked to given SIAE
    # - a job seeker profile must exist (created in step 1)
    # - if there is no HEXA address (no geolocation), allow manual input for address details

    profile = job_seeker.jobseeker_profile
    form = NewEmployeeRecordStep2Form(data=request.POST or None, instance=profile)
    maps_url = escape_uri_path(f"https://google.fr/maps/place/{job_seeker.geocoding_address}")
    step = 2
    address_updated_by_user = bool(request.GET.get("address_updated_by_user", False))

    if request.method == "POST" and form.is_valid():
        form.save()

        # Retry until we're good
        return HttpResponseRedirect(
            reverse(
                "employee_record_views:create_step_2",
                args=(job_application.id,),
            )
            + "?address_updated_by_user=true"
        )

    context = {
        "job_application": job_application,
        "form": form,
        "profile": profile,
        "job_seeker": job_seeker,
        "address_updated_by_user": address_updated_by_user,
        "maps_url": maps_url,
        "steps": STEPS,
        "step": step,
    }

    return render(request, template_name, context)


@login_required
def create_step_3(request, job_application_id, template_name="employee_record/create.html"):
    """
    Create a new employee record from a given job application

    Step 3: Training level, allocations ...
    """
    job_application = can_create_employee_record(request, job_application_id)
    job_seeker = job_application.job_seeker

    if not job_seeker.has_jobseeker_profile:
        raise PermissionDenied

    profile = job_seeker.jobseeker_profile

    if not profile.hexa_address_filled:
        raise PermissionDenied

    step = 3
    form = NewEmployeeRecordStep3Form(data=request.POST or None, instance=profile)

    if request.method == "POST" and form.is_valid():
        form.save()
        job_application.refresh_from_db()
        employee_record = None

        try:
            if not job_application.employee_record.first():
                employee_record = EmployeeRecord.from_job_application(job_application)
            else:
                employee_record = EmployeeRecord.objects.get(job_application=job_application)

            employee_record.save()

            return HttpResponseRedirect(reverse("employee_record_views:create_step_4", args=(job_application.id,)))
        except ValidationError as ex:
            # If anything goes wrong during employee record creation,
            #  catch it and show error to the user
            messages.error(
                request,
                f"Il est impossible de créer cette fiche salarié pour la raison suivante : {ex.message}.",
            )

    context = {
        "job_application": job_application,
        "form": form,
        "is_registered_to_pole_emploi": bool(job_application.job_seeker.pole_emploi_id),
        "steps": STEPS,
        "step": step,
    }

    return render(request, template_name, context)


@login_required
def create_step_4(request, job_application_id, template_name="employee_record/create.html"):
    """
    Create a new employee record from a given job application

    Step 4: Financial annex
    """
    job_application = can_create_employee_record(request, job_application_id)

    if not job_application.job_seeker.has_jobseeker_profile:
        raise PermissionDenied

    step = 4
    employee_record = (
        EmployeeRecord.objects.full_fetch()
        .select_related("job_application__to_siae__convention")
        .get(job_application=job_application)
    )
    form = NewEmployeeRecordStep4(employee_record, data=request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.employee_record.save()
        return HttpResponseRedirect(reverse("employee_record_views:create_step_5", args=(job_application.id,)))

    context = {
        "job_application": job_application,
        "form": form,
        "steps": STEPS,
        "step": step,
    }

    return render(request, template_name, context)


@login_required
def create_step_5(request, job_application_id, template_name="employee_record/create.html"):
    """
    Create a new employee record from a given job application

    Step 5: Summary and validation
    """
    job_application = can_create_employee_record(request, job_application_id)

    if not job_application.job_seeker.has_jobseeker_profile:
        raise PermissionDenied

    step = 5
    employee_record = get_object_or_404(EmployeeRecord.objects.full_fetch(), job_application=job_application)

    if request.method == "POST":
        if employee_record.status in [EmployeeRecord.Status.NEW, EmployeeRecord.Status.REJECTED]:
            employee_record.update_as_ready()
        return HttpResponseRedirect(reverse("employee_record_views:create_step_5", args=(job_application.id,)))

    context = {
        "employee_record": employee_record,
        "job_application": job_application,
        "steps": STEPS,
        "step": step,
    }

    return render(request, template_name, context)


@login_required
def summary(request, employee_record_id, template_name="employee_record/summary.html"):
    """
    Display the summary of a given employee record (no update possible)
    """
    siae = get_current_siae_or_404(request)

    if not siae.can_use_employee_record:
        raise PermissionDenied

    query_base = EmployeeRecord.objects.full_fetch()
    employee_record = get_object_or_404(query_base, pk=employee_record_id)
    job_application = employee_record.job_application

    if not siae_is_allowed(job_application, siae):
        raise PermissionDenied

    status = request.GET.get("status")

    context = {
        "employee_record": employee_record,
        "status": status,
    }

    return render(request, template_name, context)
