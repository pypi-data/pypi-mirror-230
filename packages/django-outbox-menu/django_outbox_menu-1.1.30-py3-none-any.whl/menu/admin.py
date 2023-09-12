from django.contrib import admin
from parler.admin import TranslatableAdmin

from .models import Menu, MenuGroup  # , MenuCustom

class MenuAdmin(TranslatableAdmin):     # admin.ModelAdmin
    #list_filter = ('name',) 
    list_display = ['name', 'parent', 'link', 'order_menu', 'kind', 'exclude_menu', 'updated_at']
    search_fields = ('name', 'parent')
    ordering = ('-updated_at',)
# .order_by('parent_id','order_menu')

admin.site.register(Menu, MenuAdmin)

class MenuGroupAdmin(admin.ModelAdmin):
    list_filter = ('kind',) 
    list_display = ['group', 'site_domain', 'level', 'kind', 'updated_at']
    search_fields = ('group',)
    ordering = ('-level',)

admin.site.register(MenuGroup, MenuGroupAdmin)

# tidak di update model yg ini
# class MenuCustomAdmin(admin.ModelAdmin):
#     list_filter = ('menu',) 
#     list_display = ['menu', 'menu_group', 'updated_at']
#     search_fields = ('menu',)
#     ordering = ('-updated_at',)

# admin.site.register(MenuCustom, MenuCustomAdmin)
