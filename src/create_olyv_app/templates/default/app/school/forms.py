from django import forms

from olyv.base.mixins import UniqueChoiceFormMixin

from .models import AcademicTerm, ClassLevel


class ClassLevelForm(UniqueChoiceFormMixin, forms.ModelForm):
    class Meta:
        model = ClassLevel
        fields = "__all__"


class AcademicTermForm(UniqueChoiceFormMixin, forms.ModelForm):
    class Meta:
        model = AcademicTerm
        fields = "__all__"
