from datetime import date
from decimal import Decimal
from typing import Optional

from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.db import models


def validate_file_size(file):
    """Validate that uploaded files don't exceed 5MB"""
    max_size = 5 * 1024 * 1024  # 5MB in bytes
    if file.size > max_size:
        raise ValidationError(
            f"File size cannot exceed 5MB. Current size: {file.size / (1024 * 1024):.1f}MB"
        )


class ClassLevel(models.Model):
    """
    Represents different class levels in the school system.
    Defines progression from beginner classes through primary grades.
    """

    class Meta:
        ordering = ["class_order", "name"]

    MODEL_CHOICES = [  # Order is important as it marks class progression
        ("beginner", "Beginner Class"),
        ("pp1", "PP1"),
        ("pp2", "PP2"),
        ("grade1", "Grade 1"),
        ("grade2", "Grade 2"),
    ]

    name = models.CharField(
        max_length=100,
        unique=True,
        choices=MODEL_CHOICES,
        help_text="Select the class level.",
    )
    description = models.TextField(
        blank=True,
        help_text="Optional description of the class curriculum, age requirements etc.",
    )
    class_order = models.PositiveIntegerField(
        editable=False, help_text="Automatically set order for display and progression tracking."
    )
    age_criteria = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text="Minimum age requirement in years. Students must meet this age by June 1st of the academic year. Leave blank if no age restriction applies.",
    )
    admission_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="One-time admission fee charged when a student first enrolls in this class level (in local currency).",
    )
    assessment_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="One-time assessment fee charged during the student's first term in this class (in local currency).",
    )

    def __str__(self) -> str:
        return dict(self.MODEL_CHOICES).get(self.name, self.name)

    def save(self, *args, **kwargs):
        # Set class_order based on position in MODEL_CHOICES
        choice_values = [choice[0] for choice in self.MODEL_CHOICES]
        try:
            self.class_order = choice_values.index(self.name) + 1
        except ValueError:
            # If name is not found in choices, set to a high number
            self.class_order = 999
        super().save(*args, **kwargs)


class AcademicTerm(models.Model):
    """
    Represents academic terms/quarters in the school year.
    Tracks term dates and provides status information.
    """

    class Meta:
        ordering = ["start_date", "name"]

    TERM_CHOICES = [
        ("term1", "Term 1"),
        ("term2", "Term 2"),
        ("term3", "Term 3"),
    ]

    name = models.CharField(
        max_length=100,
        unique=True,
        choices=TERM_CHOICES,
        help_text="Select the academic term. Most schools operate on 3 terms per year.",
    )
    start_date = models.DateField(
        help_text="The official start date for this school term (YYYY-MM-DD format)."
    )
    end_date = models.DateField(
        help_text="The official end date for this school term (YYYY-MM-DD format)."
    )
    year = models.PositiveIntegerField(
        help_text="Academic year this term belongs to (e.g., 2024 for 2024 academic year)."
    )

    def __str__(self) -> str:
        return f"{dict(self.TERM_CHOICES).get(self.name, self.name)} {self.year}"

    def clean(self):
        """Custom validation to ensure logical date relationships."""
        super().clean()

        if self.start_date and self.end_date:
            if self.end_date <= self.start_date:
                raise ValidationError({"end_date": "End date must be after the start date."})

            # Check that term duration is reasonable (between 60-120 days)
            duration = (self.end_date - self.start_date).days
            if duration < 60:
                raise ValidationError(
                    {
                        "end_date": "Term duration seems too short (less than 60 days). Please verify dates."
                    }
                )
            elif duration > 120:
                raise ValidationError(
                    {
                        "end_date": "Term duration seems too long (more than 120 days). Please verify dates."
                    }
                )

    def save(self, *args, **kwargs):
        """Override save to ensure validation is run."""
        self.clean()
        super().save(*args, **kwargs)

    def get_term_status(self) -> str:
        """
        Get the current status of the term.
        Returns: 'upcoming', 'active', or 'ended'
        """
        today = date.today()

        if today < self.start_date:
            return "upcoming"
        elif today > self.end_date:
            return "ended"
        else:
            return "active"

    def days_remaining(self) -> Optional[int]:
        """
        Get the number of days remaining in the term.
        Returns None if term has ended.
        Returns negative number if term hasn't started yet.
        """
        today = date.today()
        if today > self.end_date:
            return None  # Term has ended

        return (self.end_date - today).days

    @property
    def is_active(self) -> bool:
        """Check if the term is currently active."""
        return self.get_term_status() == "active"


class ClassTermFees(models.Model):
    """
    Defines fee structure for each class level during specific academic terms.
    Allows flexible pricing per class and term combination.
    """

    class Meta:
        verbose_name_plural = "Class Term Fees"
        unique_together = ("class_level", "academic_term")
        ordering = ["academic_term__start_date", "class_level__class_order"]

    class_level = models.ForeignKey(
        ClassLevel, on_delete=models.CASCADE, help_text="The class level these fees apply to."
    )
    academic_term = models.ForeignKey(
        AcademicTerm,
        on_delete=models.CASCADE,
        help_text="The specific term these fees are valid for.",
    )
    tuition_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Academic tuition fee for this class during this term (in local currency).",
    )
    meal_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text="Meal/lunch fee for this class during this term (in local currency). Set to 0 if meals not provided.",
    )
    activity_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text="Extra-curricular activities fee (sports, arts, etc.) for this term (in local currency).",
    )

    def get_total_fees(self) -> Decimal:
        """Calculate total fees for this class and term."""
        return self.tuition_fee + self.meal_fee + self.activity_fee

    def __str__(self) -> str:
        return f"{self.class_level} - {self.academic_term}: KES {self.get_total_fees()}"


class Learner(models.Model):
    """
    Represents a student enrolled in the school.
    Contains personal information, academic placement, and enrollment details.
    """

    class Meta:
        ordering = ["class_level__class_order", "last_name", "first_name"]

    GENDER_CHOICES = [
        ("male", "Male"),
        ("female", "Female"),
    ]

    class_level = models.ForeignKey(
        ClassLevel,
        on_delete=models.CASCADE,
        related_name="students",
        help_text="The current class level this student is enrolled in.",
    )
    first_name = models.CharField(
        max_length=100,
        help_text="Student's first name as it appears on official documents (birth certificate, etc.).",
    )
    last_name = models.CharField(
        max_length=100, help_text="Student's last name/surname as it appears on official documents."
    )
    middle_name = models.CharField(
        max_length=100,
        blank=True,
        help_text="Student's middle name (optional). Leave blank if not applicable.",
    )
    date_of_birth = models.DateField(
        help_text="Student's exact date of birth (YYYY-MM-DD format). This is used to verify age requirements."
    )
    gender = models.CharField(
        max_length=10,
        choices=GENDER_CHOICES,
        help_text="Student's gender for record-keeping and facilities planning.",
    )
    birth_certificate = models.FileField(
        upload_to="learners/birth_certificates/%Y/",
        blank=True,
        null=True,
        validators=[
            FileExtensionValidator(allowed_extensions=["pdf", "jpg", "jpeg", "png"]),
            validate_file_size,
        ],
        help_text="Upload the student's birth certificate (PDF, JPG, or PNG format, max 5MB). Required for age verification.",
    )
    admission_date = models.DateField(
        auto_now_add=True,
        help_text="Date when the student was officially admitted to the school (automatically recorded).",
    )
    student_id = models.CharField(
        max_length=20,
        unique=True,
        blank=True,
        help_text="Unique student identification number (automatically generated if left blank).",
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Indicates if the student is currently enrolled. Uncheck to mark as withdrawn/transferred.",
    )

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name} ({self.class_level}) - {self.student_id}"

    @property
    def full_name(self) -> str:
        """Get the student's full name."""
        if self.middle_name:
            return f"{self.first_name} {self.middle_name} {self.last_name}"
        return f"{self.first_name} {self.last_name}"

    def save(self, *args, **kwargs):
        # Generate student ID if not provided
        if not self.student_id:
            # Simple format: year + class + sequential number
            year = (
                str(self.admission_date.year)[2:]
                if hasattr(self, "admission_date")
                else str(date.today().year)[2:]
            )
            class_code = self.class_level.name[:3].upper() if self.class_level else "STU"

            # Get the next sequential number for this year/class combination
            existing_count = Learner.objects.filter(
                student_id__startswith=f"{year}{class_code}"
            ).count()

            self.student_id = f"{year}{class_code}{existing_count + 1:03d}"

        super().save(*args, **kwargs)

    def is_admission_term(self, term: AcademicTerm) -> bool:
        """Check if the given term is when this student was first admitted."""
        return term.start_date <= self.admission_date <= term.end_date

    def get_term_fees(self, term: AcademicTerm) -> Optional[Decimal]:
        """Calculate total fees owed by this student for a specific term."""
        try:
            fees = ClassTermFees.objects.get(class_level=self.class_level, academic_term=term)
            term_fees = fees.get_total_fees()

            # Add one-time fees if this is the admission term
            if self.is_admission_term(term):
                term_fees += self.class_level.admission_fee + self.class_level.assessment_fee

            return term_fees
        except ClassTermFees.DoesNotExist:
            return None

    def _get_age_as_of_date(self, as_of_date: date) -> int:
        """Calculate age in years as of a specific date."""
        age = as_of_date.year - self.date_of_birth.year

        # Adjust if birthday hasn't occurred yet this year
        if (as_of_date.month, as_of_date.day) < (self.date_of_birth.month, self.date_of_birth.day):
            age -= 1
        return age

    @property
    def age(self) -> int:
        """Get the current age of the student."""
        return self._get_age_as_of_date(date.today())

    def age_by_june_first(self, year: Optional[int] = None) -> int:
        """Get student's age as of June 1st of specified year (or current year)."""
        if year is None:
            year = date.today().year
        june_first = date(year, 6, 1)
        return self._get_age_as_of_date(june_first)

    def meets_age_criteria_for_class(self) -> bool:
        """Check if student meets the minimum age requirement for their current class."""
        if not self.class_level.age_criteria:
            return True  # No age criteria set for this class

        age_by_june = self.age_by_june_first()
        return age_by_june >= self.class_level.age_criteria


class LearnerMedicalInfo(models.Model):
    """
    Stores medical information and emergency contacts for students.
    Critical for student safety and emergency response.
    """

    learner = models.OneToOneField(
        Learner,
        on_delete=models.CASCADE,
        related_name="medical_info",
        help_text="The student this medical information belongs to.",
    )
    allergies = models.TextField(
        blank=True,
        help_text="List any known allergies (food, medication, environmental). Be specific about severity and reactions. Write 'None' if no known allergies.",
    )
    medications = models.TextField(
        blank=True,
        help_text="List any regular medications the student takes, including dosage and timing. Include emergency medications like inhalers. Write 'None' if no medications.",
    )
    medical_conditions = models.TextField(
        blank=True,
        help_text="Any ongoing medical conditions, disabilities, or special health needs the school should be aware of (e.g., asthma, diabetes, epilepsy).",
    )
    dietary_restrictions = models.TextField(
        blank=True,
        help_text="Any dietary restrictions or special nutritional needs (religious, medical, or personal preferences).",
    )
    medical_facility = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Preferred Medical Facility",
        help_text="Name and location of preferred hospital/clinic for emergencies. Include contact number if possible. (Costs covered by parent/guardian)",
    )
    emergency_contact_name = models.CharField(
        max_length=100,
        help_text="Name of primary emergency contact (usually parent/guardian).",
    )
    emergency_contact_phone = models.CharField(
        max_length=15,
        help_text="Primary emergency contact phone number (must be reachable during school hours).",
    )
    secondary_emergency_contact = models.CharField(
        max_length=100,
        blank=True,
        help_text="Name of secondary emergency contact (optional but recommended).",
    )
    secondary_emergency_phone = models.CharField(
        max_length=15,
        blank=True,
        help_text="Secondary emergency contact phone number (optional).",
    )

    def __str__(self) -> str:
        return f"Medical Info - {self.learner}"


class LearnerAdditionalInformation(models.Model):
    """
    Captures additional enrollment information and feedback.
    Helps with marketing analysis and special accommodations.
    """

    learner = models.OneToOneField(
        Learner,
        on_delete=models.CASCADE,
        related_name="additional_info",
        help_text="The student this additional information belongs to.",
    )
    referral_source = models.TextField(
        blank=True,
        verbose_name="How did you hear about us?",
        help_text="Please tell us how you learned about our school (friend, website, advertisement, etc.). This helps us improve our outreach.",
    )
    previous_school = models.CharField(
        max_length=200,
        blank=True,
        help_text="Name of previous school or daycare (if applicable). This helps us understand the student's educational background.",
    )
    special_needs = models.TextField(
        blank=True,
        help_text="Any learning disabilities, behavioral considerations, or special educational needs we should be aware of.",
    )
    additional_information = models.TextField(
        blank=True,
        verbose_name="Questions or Comments",
        help_text="Any questions about our programs, concerns, or additional information you'd like to share with us.",
    )

    def __str__(self) -> str:
        return f"Additional Info - {self.learner}"


class LearnerGuardian(models.Model):
    """
    Represents parents or guardians of students.
    Stores contact information and legal documentation.
    """

    class Meta:
        verbose_name = "Parent/Guardian"
        verbose_name_plural = "Parents/Guardians"
        ordering = ["learner", "relationship", "last_name"]

    RELATIONSHIP_CHOICES = [
        ("mother", "Mother"),
        ("father", "Father"),
        ("guardian", "Legal Guardian"),
        ("grandparent", "Grandparent"),
        ("other", "Other Relative"),
    ]

    learner = models.ForeignKey(
        Learner,
        on_delete=models.CASCADE,
        related_name="guardians",
        help_text="The student this parent/guardian is responsible for.",
    )
    relationship = models.CharField(
        max_length=20,
        choices=RELATIONSHIP_CHOICES,
        help_text="Relationship to the student (mother, father, legal guardian, etc.).",
    )
    first_name = models.CharField(
        max_length=100, help_text="Parent/guardian's first name as it appears on official documents."
    )
    last_name = models.CharField(
        max_length=100,
        help_text="Parent/guardian's last name/surname as it appears on official documents.",
    )
    phone_number = models.CharField(
        max_length=15,
        help_text="Primary phone number (must be reachable during school hours for emergencies).",
    )
    email = models.EmailField(
        blank=True,
        help_text="Email address for school communications (newsletters, reports, alerts). Optional but recommended.",
    )
    occupation = models.CharField(
        max_length=100,
        blank=True,
        help_text="Current occupation or job title (optional, for school records).",
    )
    workplace = models.CharField(
        max_length=200,
        blank=True,
        help_text="Name of employer or workplace (optional, for emergency contact purposes).",
    )
    national_id_document = models.FileField(
        upload_to="guardians/ids/%Y/",
        validators=[
            FileExtensionValidator(allowed_extensions=["pdf", "jpg", "jpeg", "png"]),
            validate_file_size,
        ],
        help_text="Upload national ID document (both front and back sides - can be combined PDF or separate images, max 5MB). Required for verification.",
    )
    is_primary_contact = models.BooleanField(
        default=False,
        help_text="Check if this is the primary contact for school communications and emergencies.",
    )
    can_pick_up_student = models.BooleanField(
        default=True,
        help_text="Check if this person is authorized to pick up the student from school.",
    )

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name} ({dict(self.RELATIONSHIP_CHOICES).get(self.relationship, self.relationship)} of {self.learner.first_name})"

    @property
    def full_name(self) -> str:
        """Get the guardian's full name."""
        return f"{self.first_name} {self.last_name}"


class MealPlan(models.Model):
    """
    Defines weekly meal schedules for different programs.
    Supports both daycare and school meal planning.
    """

    class Meta:
        unique_together = ("plan_type", "day")
        ordering = ["plan_type", "day"]

    PLAN_TYPE_CHOICES = [
        ("daycare", "Daycare Meal Plan"),
        ("school", "School Meal Plan"),
    ]

    DAY_CHOICES = [
        ("monday", "Monday"),
        ("tuesday", "Tuesday"),
        ("wednesday", "Wednesday"),
        ("thursday", "Thursday"),
        ("friday", "Friday"),
        ("saturday", "Saturday"),
    ]

    plan_type = models.CharField(
        max_length=20,
        choices=PLAN_TYPE_CHOICES,
        help_text="Choose whether this meal plan is for daycare or regular school program.",
    )
    day = models.CharField(
        max_length=20,
        choices=DAY_CHOICES,
        help_text="Day of the week this meal schedule applies to.",
    )
    morning_snack = models.CharField(
        max_length=200,
        help_text="Morning snack items (around 10:00 AM). List main items and any alternatives.",
    )
    lunch = models.CharField(
        max_length=200,
        help_text="Main lunch menu items (around 12:30 PM). Include main dish, sides, and drinks.",
    )
    evening_snack = models.CharField(
        max_length=200,
        help_text="Afternoon/evening snack items (around 3:00 PM). List main items and beverages.",
    )
    special_notes = models.TextField(
        blank=True,
        help_text="Any special dietary notes, allergen warnings, or preparation instructions for this day.",
    )

    def __str__(self) -> str:
        plan_type_display = dict(self.PLAN_TYPE_CHOICES).get(self.plan_type, self.plan_type)
        day_display = dict(self.DAY_CHOICES).get(self.day, self.day)
        return f"{plan_type_display} - {day_display}"
