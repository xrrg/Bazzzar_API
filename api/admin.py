from django.contrib import admin
from .models import *

"""
class AdminCategory(admin.ModelAdmin):
    exclude = ('subscribers_table', 'extrafield_values_table')

    def save_model(self, request, obj, form, change):
        # super(AdminCategory, self).save_model(request, obj, form, change)
        obj.save()
        obj.subscribers_table = self.create_table_subscribers(name=str(self.name))
        obj.extrafield_values_table = self.create_table_extrafield(name=str(self.name))
        obj.save()

    def delete_model(self, request, obj):
        # super(AdminCategory, self).delete_model(request, obj)
        subscribers_table = self.subscribers_table
        extrafield_values_table = self.extrafield_values_table
        obj.delete()
        Category.drop_table(table_name=subscribers_table)
        Category.drop_table(table_name=extrafield_values_table)
"""


class AdminAdvertisement(admin.ModelAdmin):
    exclude = ('image_titles',)

admin.site.register(Profile)
admin.site.register(Advertisement, AdminAdvertisement)
admin.site.register(Category)
admin.site.register(ExtraFieldDescription)
admin.site.register(City)
admin.site.register(Commercial)
admin.site.register(DatatimeTable)

# additional models for Advertisement
# admin.site.register(Housing)
# admin.site.register(Transport)
# admin.site.register(Clothes)
# admin.site.register(KidsThings)
# admin.site.register(Recreation)
