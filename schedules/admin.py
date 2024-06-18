from django.contrib import admin

from django import forms

from .models import WorkDay, Appointment, UserAuthenticationRequest


class WorkDayAdmin(admin.ModelAdmin):
    list_display = ('date', 'work_hour_start', 'work_hour_end', 'is_weekend', 'is_visible')
    list_filter = ('is_weekend', 'is_visible')


class AppointmentsAdmin(admin.ModelAdmin):
    list_display = ('date', 'start_time', 'end_time', 'procedure', 'user_id', 'is_cancelled', 'available_slot')
    list_filter = ('date',)


class UserAuthenticationRequestForm(forms.ModelForm):
    is_verified_user = forms.BooleanField(label='Is Verified User', required=False)

    class Meta:
        model = UserAuthenticationRequest
        fields = '__all__'

    def save(self, commit=True):
        instance = super().save(commit=False)
        user = instance.user
        user.is_verified_user = self.cleaned_data['is_verified_user']
        user.save()
        if commit:
            instance.save()
        return instance


class UserAuthenticationRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_verified_user', 'created_at')
    search_fields = ('user__username',)
    form = UserAuthenticationRequestForm  # Используем кастомную форму

    def is_verified_user(self, obj):
        return obj.user.is_verified_user

    is_verified_user.boolean = True
    is_verified_user.short_description = 'Is Verified User'


admin.site.register(WorkDay, WorkDayAdmin)
admin.site.register(Appointment, AppointmentsAdmin)
admin.site.register(UserAuthenticationRequest, UserAuthenticationRequestAdmin)
