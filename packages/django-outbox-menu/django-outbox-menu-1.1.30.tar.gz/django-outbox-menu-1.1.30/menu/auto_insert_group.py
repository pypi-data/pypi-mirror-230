from .models import MenuGroup
from django.contrib.auth.models import Group

def create_groups(apps, schema_monitor):
    '''
        # auth_group = apps.get_model('django.contrib.auth', 'Group')
    '''

    # For backend    
    mlist = [   
                'Super Admin',  # lvl 9
                'Developer',    # lvl 8
                'Admin',        # lvl 7
                'Owner',        # lvl 6
                'Manager',      # lvl 5
                'Operator'      # lvl 4
            ]

    mlevel = 9
    for i in mlist:                
        group, created = Group.objects.get_or_create(name=i)
        if created:
            MenuGroup.objects.create(group=group, kind=2, level=mlevel)
        mlevel -= 1

    # for frontend
    mlevel = 0
    mlist = [   
                'Anonymous',  # lvl 0
            ]
    for i in mlist:                
        group, created = Group.objects.get_or_create(name=i)
        if created:
            MenuGroup.objects.create(group=group, kind=1, level=mlevel)
        mlevel -= 1

    # end (run on migrate)

