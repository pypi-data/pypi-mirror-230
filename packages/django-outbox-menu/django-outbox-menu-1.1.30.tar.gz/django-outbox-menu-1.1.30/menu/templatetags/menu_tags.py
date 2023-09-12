'''
    1. ----------------------------------------------------------------------------
    Parameter menu_group [Optional]
    Jika kosong, cek Site_ID (proses berdasarkan site ID menu default)
    Jika menu_group kosong, SITE_id harus ada, jika tidak maka ditidak datap di proses

    2. ----------------------------------------------------------------------------
    Di tabel tambahkan User_ID dan Site_ID
    Jika data SITE_ID saja yg ada maka ini untuk front end
    Jika User_ID saja yg ada maka ini sebagai backend

    3. ----------------------------------------------------------------------------
    Jika dua2nya ada, maka USER_ID saja yg di cek SITE_ID tidak di gunakan

    Update 4 Oktober 2022
'''

from django import template

from ..menus import Menus

register = template.Library()

# from ..models import Menu
# SET GLOBAL VARIABLE FORM MENU
 # cache nanti di template
 # variable global ini bukan untuk cache
global_menu = {} 
# format:
    # USER_ID, MENU_DATA, User_group, site_ID
    # Ada project_ID (untuk membedakan, project company_profile, acounting, etc)
# menugroup = MenuGroup.objects.filter(site=self.site_id, kind=1)
#         if menugroup:
#             context['menugroup'] = int(menugroup[0].id)
#             # print('menugroup[0].id = ', menugroup[0].id)

#         else:
#            raise Http404("Menu Group '%s' belum terdaftar, silahkan daftar di halaman <a href='%s'>admin</a>" % (request.get_host(), '/admin'))

# 2. Create Menu 
# class MenuCreate(template.Node):
#     '''
#         menu_kind :
#             FRONTEND = 1
#             BACKEND = 2 

#         menu_create FRONTEND menugroup as my_menu

#         menu_group :
#             jika = 0 maka front end, menu group kosong (ignore untuk mode frontend)
#     '''
#     def __init__(self, menu_kind, menu_group, var_name='menu'):       
#         self.menu_group = menu_group
#         self.menu_kind = menu_kind           
#         self.var_name = var_name
#         print(menu_group)
#         # print(request.get_host())

#     # 1. Cache server
#     #    Cek jika sudah ada data di variable maka tidak perlu ambil lagi di database
#     # def menu_cache():
#     #     lanjut = False
#     #     if global_menu:
#     #         if global_menu[self.menu_group]:

#     #     if not global_menu:
#     #         if self.menu_kind == 'FRONTEND':                  
#     #             my_menu = Menus(self.menu_group, 1)
#     #         else:                  
#     #             my_menu = Menus(self.menu_group, 2)
#     #         global_menu[self.menu_group] = my_menu
#     #         print('load from source')
#     #     else:
#     #         if not global_menu[self.menu_group]:
#     #             if self.menu_kind == 'FRONTEND':                  
#     #                 my_menu = Menus(self.menu_group, 1)
#     #             else:                  
#     #                 my_menu = Menus(self.menu_group, 2)
#     #             global_menu[self.menu_group] = my_menu
#     #             print('load from source')
#     #         else:
#     #             my_menu = global_menu[self.menu_group]
#     #             print('load from cache')   

#     def render(self, context):        
#         # print('group = ', self.menu_group)
#         # print('kinds = ', self.menu_kind)
#         # print('var_name = ', self.var_name)
        
#         # Parameter di template tidak perlu menggunakan tanda petik untuk menandakan string

#         # if not global_menu:
#         #     if self.menu_kind == 'FRONTEND':                  
#         #         my_menu = Menus(self.menu_group, 1)
#         #     else:                  
#         #         my_menu = Menus(self.menu_group, 2)
#         #     global_menu[self.menu_group] = my_menu
#         #     print('load from source')
#         # else:
#         #     if not global_menu[self.menu_group]:
#         #         if self.menu_kind == 'FRONTEND':                  
#         #             my_menu = Menus(self.menu_group, 1)
#         #         else:                  
#         #             my_menu = Menus(self.menu_group, 2)
#         #         global_menu[self.menu_group] = my_menu
#         #         print('load from source')
#         #     else:
#         #         my_menu = global_menu[self.menu_group]
#         #         print('load from cache') 

#         if self.menu_kind == 'FRONTEND':    
#             # print('oke')
#             print('self.menu_group = ', self.menu_group)
#             my_menu = Menus(self.menu_group, 1)
#         else:
#             my_menu = Menus(self.menu_group, 2)

#         global_menu['0'] = my_menu
#         context[self.var_name] = my_menu.get_menus()
#         return ''

# @register.tag(name='menu_create')            
# def get_menu_list(parser, token):
#     error = False
#     try :
#         tag_name, menu_kind, menu_group, _as, var_name = token.split_contents()
#         print('menu grou p= ', menu_group)
#         if _as != 'as':
#             error = True
#     except:
#         error = True

#     if error:
#         raise template.TemplateSyntaxError('menu_create must be of the form, "menu_create <menu_group> <menu_kind> as <var_name>"')
#     else:
#         return MenuCreate(menu_kind, menu_group, var_name)    


# Gunakan simple tag untuk create menu
# karena tidak bisa menerima variable di template tag
@register.simple_tag 
def menu_create(kind, menugroup): 
    ''' 
        2: backend; 1 Frontend
    '''
    # if not global_menu: # var global menu masih kosong
    #     my_menu = Menus(menugroup, kind) # 1 = frontend
    #     global_menu['0'] = my_menu
    # else:
    #     my_menu = global_menu['0']

    # Pending update cache, belum disimpan site, dan tgl expired
    
    my_menu = Menus(menugroup, kind) # 1 = frontend
    global_menu['0'] = my_menu
    
    return my_menu.get_menus()
    
# ------------------------
# get active mnu
# @register.simple_tag(takes_context=True)
# def menu_active_simple_tag(context, active_menu, menu_group):    
#     my_menu = global_menu['1']
#     print('simple tag = ', my_menu.find_activeMenuList(active_menu))
#     return my_menu.get_menus()
# # OKE pakai simple tag

@register.simple_tag    #(takes_context=True) context, 
def menu_active(active_menu):    
    my_menu = global_menu['0']  # harus tipe data string    
    my_menu.get_active_menu(active_menu)
    return my_menu.get_list_active()

# @register.simple_tag # (takes_context=True) context
# def menu_breadcrumb(active_menu):    
#     # print('active_menu =' ,active_menu)
#     my_menu = global_menu['0']  # harus tipe data string  
#     # print(my_menu)  
#     return my_menu.create_breadcrumb(active_menu)


# OKE pakai simple tag untuk create bread crumb
# @register.simple_tag
# def menu_bread_crumb():
#     my_menu = global_menu['0']
#     print('bread  =', my_menu.create_breadCrumb('profile')    )
#     return my_menu.create_breadCrumb('profile')    


# UPDATE 22 Nop 2022
@register.simple_tag    #(takes_context=True) context, 
def menu_active_by_name(active_menu_name):    
    '''
        Jika active_menu_name mengandung underscore (_)
        maka ubah menjadi spasi
        karena di template jango tidak bisa menerima spasi untuk kondisi ini

        var active_menu = 'company name'
        {% menu_breadcrumb active_menu as my_active %}
        template akan error
        jadi solusinya ubah :
        var active_menu = 'company_name'
        proses di dalam fungsi ini ubah under score menjadi spasi
        kemudian baru bisa di compare dengan menu real.lowercase()
    '''

    # Update 22 Nop 22 :
    # tambahan .replace('_','')
    # replace underscore dengan spasi
    my_menu = global_menu['0']  # harus tipe data string    
    return my_menu.get_active_menu_by_name(active_menu_name.replace('_',' '))
    # return my_menu.get_list_active()
    