from django.contrib import admin
from .models import (
    Intermediary,
    Organization,
    OrganizationDID,
    OrganizationKeys,
    Issuer,
    UserProxy,
    OperatorDID,
    Subject,
    SubjectDID,
    OrganizationOnboardingNotification,
)
from .enums import OrganizationsSwitches
import waffle
from .forms import UserProxyForm


class OperatorDIDAdmin(admin.ModelAdmin):
    model = OperatorDID

    def get_model_perms(self, request):
        if not waffle.switch_is_active(
            OrganizationsSwitches.Organizations.value
        ) and not waffle.switch_is_active(OrganizationsSwitches.OperatorsDID.value):
            return {}

        return super(OperatorDIDAdmin, self).get_model_perms(request)


class SubjectDIDAdmin(admin.ModelAdmin):
    model = SubjectDID

    def get_model_perms(self, request):
        if (
            not waffle.switch_is_active(OrganizationsSwitches.Organizations.value)
            or waffle.switch_is_active(OrganizationsSwitches.Organizations.value)
            and not waffle.switch_is_active(OrganizationsSwitches.OrganizationsIntermediary.value)
        ):
            return {}

        return super(SubjectDIDAdmin, self).get_model_perms(request)


class SubjectAdmin(admin.ModelAdmin):
    model = Subject

    def get_model_perms(self, request):
        if (
            not waffle.switch_is_active(OrganizationsSwitches.Organizations.value)
            or waffle.switch_is_active(OrganizationsSwitches.Organizations.value)
            and not waffle.switch_is_active(OrganizationsSwitches.OrganizationsIntermediary.value)
        ):
            return {}

        return super(SubjectAdmin, self).get_model_perms(request)


class IntermediaryAdmin(admin.ModelAdmin):
    model = Intermediary

    def get_model_perms(self, request):
        if (
            not waffle.switch_is_active(OrganizationsSwitches.Organizations.value)
            or waffle.switch_is_active(OrganizationsSwitches.Organizations.value)
            and not waffle.switch_is_active(OrganizationsSwitches.OrganizationsIntermediary.value)
        ):
            return {}

        return super(IntermediaryAdmin, self).get_model_perms(request)


class OrganizationAdmin(admin.ModelAdmin):
    model = Organization
    list_filter = ["networks"]
    search_fields = [
        "name",
        "email",
        "phone",
    ]

    def get_model_perms(self, request):
        if not waffle.switch_is_active(OrganizationsSwitches.Organizations.value):
            return {}

        return super(OrganizationAdmin, self).get_model_perms(request)


class OrganizationDIDAdmin(admin.ModelAdmin):
    model = OrganizationDID
    list_filter = ["network_name", "organization"]
    search_fields = [
        "network_name",
        "organization",
        "did",
    ]

    def get_model_perms(self, request):
        if not waffle.switch_is_active(
            OrganizationsSwitches.Organizations.value
        ) or not waffle.switch_is_active(OrganizationsSwitches.OrganizationsDID.value):
            return {}

        return super(OrganizationDIDAdmin, self).get_model_perms(request)


class OrganizationKeysAdmin(admin.ModelAdmin):
    model = OrganizationKeys

    def get_model_perms(self, request):
        if not waffle.switch_is_active(OrganizationsSwitches.Organizations.value):
            return {}

        return super(OrganizationKeysAdmin, self).get_model_perms(request)


class IssuerAdmin(admin.ModelAdmin):
    model = Issuer
    readonly_fields = ["active"]
    list_filter = ["organization"]

    def get_model_perms(self, request):
        if (
            not waffle.switch_is_active(OrganizationsSwitches.Organizations.value)
            or waffle.switch_is_active(OrganizationsSwitches.Organizations.value)
            and not waffle.switch_is_active(OrganizationsSwitches.OrganizationsIssuer.value)
        ):
            return {}

        return super(IssuerAdmin, self).get_model_perms(request)


class UserProxyAdmin(admin.ModelAdmin):
    form = UserProxyForm

    def get_model_perms(self, request):
        if not waffle.switch_is_active(OrganizationsSwitches.Organizations.value):
            return {}

        return super(UserProxyAdmin, self).get_model_perms(request)


class OrganizationOnboardingNotificationAdmin(admin.ModelAdmin):
    model = OrganizationOnboardingNotification
    list_filter = ["organization"]

    def get_model_perms(self, request):
        if not waffle.switch_is_active(OrganizationsSwitches.Organizations.value):
            return {}

        return super(OrganizationOnboardingNotificationAdmin, self).get_model_perms(request)


admin.site.register(OrganizationOnboardingNotification, OrganizationOnboardingNotificationAdmin)
admin.site.register(SubjectDID, SubjectDIDAdmin)
admin.site.register(Subject, SubjectAdmin)
admin.site.register(OperatorDID, OperatorDIDAdmin)
admin.site.register(Intermediary, IntermediaryAdmin)
admin.site.register(Organization, OrganizationAdmin)
admin.site.register(OrganizationDID, OrganizationDIDAdmin)
admin.site.register(OrganizationKeys, OrganizationKeysAdmin)
admin.site.register(Issuer, IssuerAdmin)
admin.site.register(UserProxy, UserProxyAdmin)
