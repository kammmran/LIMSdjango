from django.contrib import admin
from .models import TestResult, ParameterResult


class ParameterResultInline(admin.TabularInline):
    model = ParameterResult
    extra = 0


@admin.register(TestResult)
class TestResultAdmin(admin.ModelAdmin):
    list_display = ['test_assignment', 'status', 'entered_by', 'reviewed_by', 'entered_date']
    list_filter = ['status', 'entered_date', 'reviewed_date']
    search_fields = ['test_assignment__sample__sample_id', 'test_assignment__test__name']
    readonly_fields = ['entered_by', 'reviewed_by', 'entered_date', 'reviewed_date']
    inlines = [ParameterResultInline]


@admin.register(ParameterResult)
class ParameterResultAdmin(admin.ModelAdmin):
    list_display = ['test_result', 'parameter', 'value_numeric', 'value_text', 'is_abnormal']
    list_filter = ['is_abnormal']
    search_fields = ['test_result__test_assignment__sample__sample_id', 'parameter__name']
