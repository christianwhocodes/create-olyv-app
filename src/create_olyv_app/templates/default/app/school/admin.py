from django.contrib import admin

from olyv.base.adminsite import admin_site

from .forms import AcademicTermForm, ClassLevelForm
from .models import AcademicTerm, ClassLevel, ClassTermFees


@admin.register(ClassLevel, site=admin_site)
class ClassLevelAdmin(admin.ModelAdmin):
    form = ClassLevelForm


@admin.register(AcademicTerm, site=admin_site)
class AcademicTermAdmin(admin.ModelAdmin):
    form = AcademicTermForm


@admin.register(ClassTermFees, site=admin_site)
class ClassTermFeesAdmin(admin.ModelAdmin):
    pass
