from django.contrib import admin
from django.contrib.admin.actions import delete_selected
from .models import *


class Admin(admin.ModelAdmin):
    actions = ['delete_selected']
    
    @staticmethod
    def delete_selected(self, request, obj):
        for o in obj.all():
            Category.objects.filter(invoice=o).update(billed=False)
            o.delete()

admin.site.register(Profile)
admin.site.register(Advertisement)
admin.site.register(Category)
admin.site.register(City)
admin.site.register(AdvertisementPhoto)

# additional models for Advertisement
admin.site.register(Housing)
admin.site.register(Transport)
admin.site.register(Clothes)
admin.site.register(KidsThings)
admin.site.register(Recreation)
