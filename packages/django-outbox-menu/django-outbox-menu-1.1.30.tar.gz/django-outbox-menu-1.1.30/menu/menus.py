'''
    Generate menus - create by ione
    Class ini untuk generate menu sesuai dengan data di database
    Date 13-02-21

    Update v2.0:
        # Sdh mengikuti update terakhir dari project OPD
        # Atur ulang tab
        # Ikuti model tabel menu yg ada di project ini atau OPD

    Update v2.1:
        # create menu berdasarkan user yg login
        # untuk front end, karena tidak login maka generate menu berdasarkan
        # user yg berada di site tersebut

    Update v2.2:
        # perbaikan bread crumb menu
        # tambah bread crumb lengkap dengan link (tidak hanya name saja)

    Update v3.0:
        # using recursive function, all result list same as old version

    Update 12 April 2023:
        # Filter menu ada dua:
            di menu_group dan di model_list, keduanya harus ada, jika salah satu saja, maka menu tidak muncul

    ----------------------------------------------------------------------------------------------------

    # Tambah dictionary sesuai data di database, Algoritma :
    # 1. Buat query Order by parent id dan order menu
    # 2. copy data ke mDict record per pecord
    # 3. Append ke mList, sehingga jadinya list of dictionary
    # 4. Atur ulang mList, sehingga urutannya menjadi :
    #    Menu Parent
    #       |--- Menu Anak1
    #       |--- Menu Anak2, dst...
    # 5. Atur Ulang Level, sehingga menjadi :
    #    Dictionary memiliki item baru
    #       1. Level : untuk menentukan kedalaman level menu anak
    #       2. HaveChild : True or False, Untuk penanda apakah menu parent mempunyai anak atau tidak
    #       3. haveChildEndTag : Type Integer, Untuk penanda tag penutup menu anak di buat
    #          Jika level 1, buat satu tag penutup menu anak
    #          Jika level 2, buat dua tag penutup menu anak, dst...
    # 6. Atur active menu
    # Buat function baru untuk Atur BreadCrumb, tambahkan List of Dictionary dengan format 
    #       [{'Nama','href'},{'nama2','href2'}]
    #       Data ini akan di cek di template dengan cara yang sama seperti generate menu
    #  --------------------------------------------------------------------------------------------------          
'''

from django.db.models import F

from .models import Menu  # MenuCustom


class Menus:    
    '''
        Class Menus
    '''
    # mLvl_prev = -1   # catat level sebelumnya  
    mList_recursive = []
    mList_active = []
    
    #mMenu_list = [] # diambil dari parameter di create_menu
    # menu_custom_list = []   # exclude this menu from default menus
    # mlist_model = []

    # mDict = {}     
    # mList = []      # result ada di mList
    site_id = 1
    lang = 'id'
    group_id = 0      # simpan group_id untuk digunakan di recursive

    # defailt menu_group = 0 artinya all
    # kinds = 1 Front end
    # kinds =2 backend
    # kinds =0 all
    def __init__(self, menu_group = 0, kinds = 0, model_list = [], exclude_menu = -1): #, site_id = 1): #, pIs_master_menu = False):         # menu_group adalah filter untuk company tertentu saja
        '''
            Jika pKind = 0 maka ambil data semua, frontend dan backend

            Filter menu ada dua:
                di menu_group dan di model_list, keduanya harus ada, jika salah satu saja, maka menu tidak muncul
        '''
        # self.site_id = site_id

        # get active language
        obj = Menu()
        self.lang = obj.get_current_language()
        self.group_id = menu_group
        # print('init', menu_group, kinds, model_list, exclude_menu)

        if len(self.mList_recursive) == 0:
            #if menu_group != "":
            self.create_menus(menu_group, kinds, model_list, exclude_menu) #, pIs_master_menu)
        else:
            # self.mDict = {}  # clear dulu (karena prosedur init ini sekali dijalankan saat class di buat)
            self.mList_recursive = []
            self.mList_active = []
            self.create_menus(menu_group, kinds, model_list, exclude_menu) #, pIs_master_menu)                    

    def get_menus(self):
        return self.mList_recursive

    def get_list_active(self):
        return self.mList_active

    # def get_menu_custom_list(self, menu_group):
    #     # select custom menu for ignoring
    #     self.menu_custom_list = []
    #     menu_custom = list(MenuCustom.objects.filter(site_id=self.site_id). \
    #         exclude(menu_group_id=menu_group).values('menu_id'))
    #     # print(menu_custom)

    #     for i in menu_custom:
    #         self.menu_custom_list.append(i['menu_id'])

    #     # print(self.menu_custom_list)

    def ignore_circular_parent(self):
        # 0. Sebelum proses menu, update dulu seluruh menu yg id = id parent set id parent = NULL untuk menghindari
        Menu.objects.filter(id=F('parent_id')).update(parent_id=None)    # query pengaman

    def create_menus(self, menu_group, kinds, menu_list, exclude_menu): 
        # Update 24 Juli 2022
        # exluclude_menu :
        # -1: all
        # 0 : false    
        # 1 : true
        
        if not menu_group:
            return "menu group is empty"

        # 0. Sebelum proses menu, update dulu seluruh menu yg id = id parent set id parent = NULL untuk menghindari
        # Menu.objects.filter(id=F('parent_id')).update(parent_id=None)    # query pengaman
        # 1. Clear circular reference (ignore it, or set as None)
        self.ignore_circular_parent()
        #print('menu_group', menu_group)
        #print('kinds', kinds)
        #print('menu_list', menu_list)
        
        #self.mMenu_list = menu_list

        # exclude custom menu tidak digunakan disini karena hanya di ambil root menu saja
        # [UPDATE] tetap digunakan untuk antisipasi root menu digunakan sebagai custom menu
        # self.get_menu_custom_list(menu_group)

        # get active language
        # print('FROM menu.menu_group',menu_group)
        # 2. Get data by user options (UPDATE only get ROOT MENU base on User OPTION)
        # Harus konversi ke integer karena tidak masuk ke kondisi        
        if int(kinds) == 0: # jika kind = 0 ambil semua data front end dan back end            
            # .exclude(id__in=self.menu_custom_list) \
            # UPADATE menu_group__id menjadi menu_group__group_id
            # ,id__in = model_list \
            # menu_group__group_id=menu_group is_visibled=True, 
            mData = Menu.objects.language(self.lang).filter(menu_group__id=menu_group \
                ,parent=None) \
                .order_by('parent_id','order_menu').values('id')     

        # elif int(menu_group) == 0:   # menu group = 0 artinya menu frontend            
        #     # .exclude(id__in=self.menu_custom_list) \
        #     mData = Menu.objects.language(self.lang).filter(kind=kinds, is_visibled=True, parent=None) \
        #         .order_by('parent_id','order_menu').values('id')     

        # !!!!!!! UPDATE !!!!!!!
        # ----------------------
        # Update 30 januari 2023, Frontend juga harus jelas menugroup milik frontend (Annonymous)
        # kondisi ambil semua yg bertipe front end tidak ada lagi
        # karena front end juga bisa berbeda susunan menunya tergantung user yg lagi aktif (default annonymous)

        # kondisi is_visible dan menu_group_id di perlukan untuk cek apakah menu root visible dan benar milik user yg aktif
        # kondisi ini juga perlu di cek di recursive create menu, untuk mendeteksi sub menu is_visible dan milik user aktif atau bukan
        # ---------------------

        else:   
            # .exclude(id__in=self.menu_custom_list) \         is_visibled=True, 
            mData = Menu.objects.language(self.lang).filter(menu_group__id=menu_group \
                ,kind=kinds, parent=None) \
                .order_by('parent_id','order_menu').values('id')                  

        # print('mDATA',mData)        
        # .exclude(id__in=menu_custom_list) \
        #print('mData',mData)
        # 3. Get root menu
        # get menu id only
        # print(mData)
        # menu_id = []
        # for i in mData:
        #     menu_id.append(i.id)

        # Entry point from root menu
        # root_menu = self.get_root_menu(menu_id)
        root_menu = []
        for i in mData:
            root_menu.append(i['id'])

        # print('root_menu=', root_menu)
        # print('menu_list=', menu_list)
        # print('root_menu', root_menu)

        # 4. begin process recursive menu
        if kinds==2: # khusus backend saja
            self.create_menu_recursive(root_menu,0,menu_list)   # for backend
        else:
            self.create_menu_recursive(root_menu,0) # for frontend
        
        # print('MENU.after',self.mList_recursive)

        # 5. Update End Tag
        self.update_end_tag()

        # 6. get complete data base on mData
        self.get_menus_complete(exclude_menu)

        # clean data yg tidak ada di menu_list
        # print('before',self.mList_recursive)
        # self.get_menus_clean(menu_list)
        #print('after',self.mList_recursive)
        
        # 6. return result
        #return self.get_menus()

    def get_menus_complete(self, exclude_menu):
        # obj = Menu()
        # lang = obj.get_current_language()
        
        mCount = 0
        mFound = False

        while mCount < len(self.mList_recursive):
            #if self.mList_recursive[mCount]['id'] in menu_list:
            mData = Menu.objects.language(self.lang).get(id=self.mList_recursive[mCount]['id'])
            
            mFound = False
            if exclude_menu == 1: # True (Ambil yg exlude_menu=True saja)
                if mData.exclude_menu == True:
                    mFound = True
            elif exclude_menu == 0: # False (Ambil yg exclude_menu=False saja)
                if mData.exclude_menu == False:
                    mFound = True
            else: # ambil semua
                mFound = True
            
            if mFound:        
                #print('ADD array')
                # print(mData.order_menu)
                self.mList_recursive[mCount]['uuid'] = mData.uuid
                self.mList_recursive[mCount]['order_menu'] = mData.order_menu
                self.mList_recursive[mCount]['name'] = mData.name
                self.mList_recursive[mCount]['link'] = mData.link
                self.mList_recursive[mCount]['icon'] = mData.icon
                self.mList_recursive[mCount]['is_external'] = mData.is_external
                self.mList_recursive[mCount]['is_visibled'] = mData.is_visibled
                self.mList_recursive[mCount]['exclude_menu'] = mData.exclude_menu
                self.mList_recursive[mCount]['is_new'] = mData.is_new
                self.mList_recursive[mCount]['parent_id'] = mData.parent_id
                # self.mList_recursive[mCount]['order_menu'] = mData.order_menu      
                
                mCount += 1
            else:
                #print(f'REMOVE array {mCount}')
                self.mList_recursive.pop(mCount)      # bug found

    # def get_root_menu(self, menu_id):
    #     data = Menu.objects.filter(id__in=menu_id, parent=None).values('id')        
    #     ret = []
    #     for i in data:
    #         ret.append(i['id'])

    #     return ret
    
    # def get_menus_clean(self, menu_list):
    #     # Clean dengan data menu_list jika data tidak ada di menu_list maka hapus dari mList_recursive
        
    #     # obj = Menu()
    #     # lang = obj.get_current_language()
    #     #print('menu_list [get_menus_complete]',menu_list)
    #     mCount = 0
    #     while mCount < len(self.mList_recursive):
    #         if self.mList_recursive[mCount]['id'] not in menu_list:
    #             self.mList_recursive.pop(mCount)
    #         else:
    #             mCount += 1

    def is_have_child(self, menu_id):
        '''
            cek apakah ada menu dengan parent = menu_id?
            jika ya return True, else False
        '''
        # tidak perlu lang disini karena tidak ada field name di ambil
        # .exclude(id__in=self.menu_custom_list) \
        # menu_group__group_id ,is_visibled=True) \
        data = Menu.objects.filter(parent_id=menu_id \
            ,menu_group__id=self.group_id) \
            .order_by('parent_id','order_menu').values('id')      
              
        ret = []
        for i in data:
            ret.append(i['id'])

        return ret

    def create_menu_recursive(self, root_menu_id, lvl, menu_list=[]): # , menu_group, kinds):     
        '''
            menu_group, kinds : untuk mendapatkan kondisi where, data selalu sama
            root_menu_id : berisi ID menu root untuk level 0
                           berisi ID menu[0] (data satu index saja) untuk level 1..n
                           Hanya berisi ID dengan format ['id_1', 'id_2', 'id_n']
        '''        
        # print('root_menu_id',  root_menu_id)

        for i in root_menu_id:
            # print('recursive', i)
            child_id = self.is_have_child(i)
            # print('is_have_child', child_id)
            
            if child_id:
                if menu_list:
                    if i in menu_list:
                        self.mList_recursive.append({'id':i, 'level':lvl, 'haveChild':True})

                # MenuList Kosong untuk backend
                #else: Jika di menu list setting, masih kosong, maka kembalikan data kosong juga (BUG FOUND)
                #    self.mList_recursive.append({'id':i, 'level':lvl, 'haveChild':True})
                else: # untuk front end ini
                    # print('append dulu datanya data', i)
                    self.mList_recursive.append({'id':i, 'level':lvl, 'haveChild':True})

                lvl += 1                                    
                self.create_menu_recursive(child_id, lvl, menu_list)                
                lvl -= 1
            else:
                # print('menu_list',menu_list)
                if menu_list:
                    if i in menu_list:
                        self.mList_recursive.append({'id':i, 'level':lvl, 'haveChild':False})
                # Jika menu list setting kosong
                # MenuList Kosong, untuk front end
                else: 
                    # print('append data', i)
                    self.mList_recursive.append({'id':i, 'level':lvl, 'haveChild':False})

    def update_end_tag(self):
        '''
            parameter mList_recursive
            cari yang next level turun (misal dari 1 ke 0, atau dari 2 ke 1, 2 ke 0, semua yg menurun tandai sebagai true end_tag nya)
        '''
        mCount = 0
        while mCount < len(self.mList_recursive):
            # kondisi akhir 
            if mCount == len(self.mList_recursive)-1:
                if self.mList_recursive[mCount]['level'] == 0:  # kondisi tag akhir 0, langsung set end tag = 1
                    self.mList_recursive[mCount]['haveChildEndTag'] = [1]
                else:
                    tmp = self.mList_recursive[mCount]['level']
                    self.mList_recursive[mCount]['haveChildEndTag'] = list(range(1,tmp+1))

            # kondisi lvl skr dan next sama2 nol (root)
            elif self.mList_recursive[mCount]['level'] == 0 and self.mList_recursive[mCount+1]['level'] == 0:
                self.mList_recursive[mCount]['haveChildEndTag'] = [1]

            # kondisi lvl menurun
            else:
                selisih = self.mList_recursive[mCount]['level'] - self.mList_recursive[mCount+1]['level']
                if selisih > 0:
                    self.mList_recursive[mCount]['haveChildEndTag'] = list(range(1,selisih+1))
                else:
                    self.mList_recursive[mCount]['haveChildEndTag'] = []

            mCount += 1

    # Menu bisa diberikan dengan nama yg sama, oleh karena itu cari active menu dan breadcrumb menggunakan ID
    def get_active_menu(self, menu_id):
        '''
            Find active menu recursively
        '''        
        data = Menu.objects.language(self.lang).filter(id=menu_id)
                # .exclude(id__in=self.menu_custom_list) 
        if data:
            for i in data:
                # print(i.parent_id)
                parent_id = i.parent_id
                self.mList_active.insert(0, {'id': i.id, 'name': i.name, 'link': i.link, 'icon': i.icon, 'is_external':i.is_external})
                self.get_active_menu(parent_id)
        
    # function ini sama seperti diatas, hanya saja parameter berupa menu name
    # find dulu id dari menu name, jika di temukan lebih dari satu munculkan warning
    # data yg sesuai lebih dari satu
    def get_active_menu_by_name(self, menu_name):
        #data = Menu.objects.filter()
        # cari data yg sesuai di self.mList_recursive
        # tidak perlu baca database lagi
        self.mList_active.clear()
        #print('mList_recursive = ', self.mList_recursive)

        for i in self.mList_recursive:
            #print('i',i)
            # print(i['name'].lower(), menu_name)

            if i['name'].lower() == menu_name.lower():
                parent_id = i['parent_id']
                self.mList_active.insert(0, {'id': i['id'], 'name': i['name'], 'link': i['link'], 'icon': i['icon'], 'is_external':i['is_external']})

                # recursive ke get_active_menu BY ID
                self.get_active_menu(parent_id)

        result_list = []
        for i in self.mList_active:
            result_list.append(i['name'])

        return result_list
        


# END OF FILE
