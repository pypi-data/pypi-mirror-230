'''
    Recreate model base on OPD project and Outbox Project
    29th September 2022
    Grid Software, Inc.
'''
import uuid

from django.contrib.auth.models import Group
from django.contrib.sites.models import Site
from django.db import models
from django.db.models import Max
from django.utils.translation import gettext_lazy as _
from parler.models import TranslatableModel, TranslatedFields

# User = get_user_model()
# from django.contrib.auth.models import User
# from django.contrib.auth import get_user_model

class OptMenuKinds(models.IntegerChoices):
    '''
        Jenis menu : 
            0 : Front end without user login
            1 : Front end with user login
            2 : Back end with user login (nothing for none user)

            Update 17 Sept 2021
            0 : Front End
            1 : Back End
    '''
    FRONTEND = 1, _('Frontend')
    BACKEND = 2, _('Backend') 

    # Tidak jadi karena crash dengan unique together di model
    # BACKEND_DEFAULT = 3 # Penanda user baru login, belum ada company yg aktif, sehingga menu belum bisa di generate
                        # untuk itu generate menu default langsung   

class MenuGroup(models.Model):
    '''
        Group : Model Menu
        Simpan data group menu :
        1. Owner
        2. Manager
        3. Operator
        4. Kasir
        5. dll...

        Tidak ada interface, maintenance di halaman admin


        # Perubahan proses bisnis :
        --------------------------

        1. MenuGrup ini berelasi OneToOne ke tabel auth group django
        agar supaya permission mengikuti setting default django

        2. Site tetap dipertahankan, karena setiap site memiliki struktur group yang sama
        tidak ada akses untuk client mengubah struktur group ini
        Jika site kosong itu artinya group menu milik semua site

        2.a name dihapus karena sudah ada di auth group django
        2.b menu customs di hapus karena menu custom dapat langsung di create di menu utama

        3. Struktur group default adalah :
            # admin (superuser), akses melalui secret-admin (hanya dimiliki oleh owner code)
                security level 10
                # akun developer, akses melalui dashboard (ada menu khusus yg hanya muncul di group ini)
                    security level 9
                    # akun client (admin-client), akses melalui dashboard, memiliki akses untuk untuk membuat sub user di bawah client
                        security level 8
                        # akun operator-client, memiliki akses untuk membuka menu tertentu saja
                        security level 7
                        client dapat berkreasi membuat nama operator-client ini
                        nama default yg telah ada di database :
                            # owner     level 6
                            # manager   level 5
                            # operator  level 4

        4. Urutan group backend (kind=2) :
            9. Super Admin
            8. Developer
            7. Admin
            6. Owner
            5. Manager
            4. Operator
            3. ...
            2. ...
            1. ...

           Urutan group frontend (kind=1):
            3. ...
            2. ...
            1. ...
            0. Anonymous     

            level 1..3 untuk group tertentu misal user telah login, ada menu khusus yg muncul untuk group tsb.

        5. id yang digunakan adalah id dari auth_group bukan id dari menuGroup
    '''
    # Update 19 Oktober 2022
    # untuk membedakan menu project 1 dengan yg lain, dengan nama sama
    site = models.ForeignKey(Site, on_delete=models.CASCADE, null=True, blank=True)
    # site ada tambahan null true, blank true
    # jika berisi null, itu artinya milik semua site

    uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)

    # additional fields
    # null true, untuk compatibilitas dengan versi sebelumnya
    group = models.OneToOneField(Group, on_delete=models.CASCADE, null=True, blank=True)
    level = models.SmallIntegerField(default=0)     

    # Tidak boleh ada data kembar di name    
    # translations = TranslatedFields(
    #     name = models.CharField(max_length=100) # unique=True (Unique together with site)
    # )
    
    # Untuk membedakan mana menu group front end mana yg backend
    kind = models.SmallIntegerField(choices=OptMenuKinds.choices, default=OptMenuKinds.FRONTEND)

    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)    

    # Optional Fields:
    # created_at = models.DateTimeField(auto_now_add=True)
    # updated_at = models.DateTimeField(auto_now=True)

    # objects = MenuGroupManager()
    
    # def __str__(self):
    # def __unicode__(self):
    def __str__(self):
        return self.group.name

    def site_domain(self):
        return self.site.domain if self.site else 'All'

    # class Meta:
    #     ordering = ('-level',)

    # class Meta:
    #     constraints = [
    #         models.UniqueConstraint(fields=['site', 'translations__name'], name='unique_site_name')
    #     ]

# def company_name_validate(value):
#     if len(value) < 3:
#         raise ValidationError("Company name mush be more than 3 character")
#     else:
#         return value

class Menu(TranslatableModel):
    '''    
        Relase :
            User --1:N-- Menu
        Deskripsi :
            # Menu di buat per user,
            # Satu company bisa mempunyai banyak user,
            # Satu User bisa punya banyak menu
            # Tetapkan satu user sebagai user master (berguna sebagai menu master), di copy ke menu user lain
    
        # ada 1 company dengan site ID = 1 sebagai master menu
        # seluruh menu di create dari site ini (berarti is_master_menu tidak di perlukan lagi)
        # Untuk menu di app blog, user tidak dalam kondisi login
        # Untuk menu di app inventory, user harus login dulu        
        # Jika user telah di create, langsung generate menu untuk user tersebut
        # dapat di visible sesuai kebutuhan
    '''      
    # ID tetap di create otomaris
    uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False) 
    translations = TranslatedFields(
        name = models.CharField(max_length=100)
    )

    # menu group, relasi many to many 
    # Untuk frontend menu group kosong
    menu_group = models.ManyToManyField(MenuGroup, related_name="menu_group_menu", blank=True) # , null=True, blank=True)  not effect to m2m relation

    # Optional Fields:
    # user = models.ForeignKey(User, null=True, blank=True, on_delete=models.PROTECT)        # Menu di generate per user   
    # user harus diimport dulu

    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE)    

    # link: adalah name menu yg di slugify
    # href di ubah menjadi link
    # jika ada ://www maka dianggap link luar
    # /home/dashboard is not valid URLField (change back to CharField)
    # link = models.URLField(max_length=255, null=True, blank=True)  # , verbose_name='Link'

    # Update 4 Desember 22
    link = models.CharField(max_length=255, default='#', blank=True)  # Tambah # agar tidan None di link menu # null=True, 

    # urut menu (ambil dari id, tapi user dapat mengubah sendiri ordernya)
    order_menu = models.SmallIntegerField(default=0)

    # awesome icon
    # data berupa blok <i class="icon"></i>
    icon = models.CharField(max_length=50, null=True, blank=True)    

    #is_admin_menu = models.BooleanField(default=False)	    
    # is_admin_menu: jika true, menu untuk backend, jika false menu untuk frontend
    # jenis menu
    kind = models.SmallIntegerField(choices=OptMenuKinds.choices, default=OptMenuKinds.FRONTEND)

    # is_visibled: untuk menyembunyikan menu
    is_visibled = models.BooleanField(default=True)	    

    # is_master_menu: adalah menu yg digunakan oleh banyak user
    # tidak bisa dihapus, hanya super user yg bisa menghapus
    # is_master_menu adalah menu yg di copy oleh user lain saat pertama kali di buat

    # Update 17 Sept 2021 
    # is_master_menu tidak digunakan lagi karena seluruh menu di create sesuai dengan
    # data menu di SITE 1
    # (menu di SITE 1 sebagai menu master yg akan di copy ke site lain saat User pertama kali di create)
    # is_master_menu = models.BooleanField(default=False)	 

    # is_statis_menu: penanda halaman statis
    # semua menu yg di create oleh user adalah statis menu
    # diakses khusus melalui link tertentu di halaman statis   
    # is_statis_menu = models.BooleanField(default=False)	
    is_external = models.BooleanField(default=False)	    # Jika external menu True, maka otomatis target _BLANK

    # Penanda menu baru untuk di dashboard (Input dari halaman secret-admin)
    # Update 3 Desember 2022
    is_new = models.BooleanField(default=False)	    

    # timestamp
    # created_at = models.DateTimeField(auto_now_add=True)
    # updated_at = models.DateTimeField(auto_now=True)

    # untuk status sinkronisasi ke server
    # penanda di server lokal apakah sudah di sinkronisasi atau belum
    # yg paling penting tanggal harus valid 
    # is_already_sync = models.BooleanField(default=False)	
    
    # checkbox untuk pembeda antara menu yang otomatis di generate dan menu
    # untuk footer, yang tidak perlu di generate untuk menu header
    exclude_menu = models.BooleanField(default=False) # false artinya digenerate di menu header

    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)    

    # def __str__(self):
    #     return self.name

    # class Meta:
    #     constraints = [
    #         models.UniqueConstraint(fields=['menu_group', 'name'], name='unique_menu_group_name')
    #     ]

    # def updated_at_(self):
    #     return get_natural_datetime(self.updated_at)

    # def created_at_(self):
    #     return get_natural_datetime(self.created_at)

    # def parent_(self):
    #     if self.parent:
    #         return self.parent.name
    #     else:
    #         return '-'

    # def updated_at_(self):
    #     return get_natural_datetime(self.updated_at)        
    
    # def updated_at_(self):
    #     return  "naturalday(self.updated_at)"
       # return serializers.serialize("json",' naturalday(self.updated_at)')
        #return serializers.serialize('json', naturalday(self.updated_at))

    # class meta:
    #     ordering = ('-parent_id', '-order_menu',)

    # def __str__(self):          
    def __str__(self):
        if self.kind == OptMenuKinds.FRONTEND:
            res = '[ Front-End ]'       # halaman depan
        # elif self.kind == OptMenuKinds.BACKEND_DEFAULT:
        #     res = '[ Default ]'
        else:
            res = '[ Back-End ]'        # halaman dashboard

        # res = get_kind_display() # tidak ada selfnya kemungkinan tidak bisa

        if self.parent:
            par = self.parent.name      # tampilkan name parent jika ada    
        else:
            par = 'ROOT'

        return "{} {} > {}".format(res, par, self.name)      

    # untuk slug
    def save(self, *args, **kwargs):   
        # menggunakan ID bisa menyebabkan data overload karena tipe data ID BIGINT
        if self.order_menu == 0:     
            #     self.order_menu
            # print('menu_group = ' , self.menu_group.exists())
            # print('parent = ' , self.parent_id)
            # print('kind = ' , self.kind)
            obj = Menu.objects.filter(parent=self.parent, kind=self.kind).aggregate(max=Max('order_menu'))
            if obj:
                # max = obj['max'] + 1
                #if obj['max']: # kondisi obj['max'] == 0 maka kondisi ini tidak masuk
                if not obj['max'] is None: 
                    self.order_menu = obj['max'] + 1

        # print(tmp)

        super(Menu, self).save(*args, **kwargs)   


# class MenuCustom(models.Model):
#     '''
#         # Akan di hapus di versi berikutnya
#         # status deprecated

#         # tidak ada update ke multi language khusus model ini
#         Custom menu adalah menu yg hanya muncul di site dan menu_group tertentu saja
#         tidak muncul di tempat lain
#     '''
#     # Menu ini digunakan untuk filter custom menu yg ada di site, exlude menu_group ada di get_menu_custom_list menus.py
#     site = models.ForeignKey(Site, on_delete=models.CASCADE)

#     menu_group = models.ForeignKey(MenuGroup, on_delete=models.PROTECT) #, blank=True, null=True)    
#     menu = models.OneToOneField(Menu, on_delete=models.CASCADE) # One to One Relations to menu

#     created_at = models.DateTimeField(auto_now_add=True, editable=False)
#     updated_at = models.DateTimeField(auto_now=True, editable=False)    


#     def __str__(self):  
#         return "{}".format(self.menu)  

