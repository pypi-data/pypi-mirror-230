# DJANGO OUTBOX MENU

Menu is almost use in every web project. 

With this library you can create menu for backend and frontend project without headache.
All you need to do is:   


## In your django Environment

### Install package to your environment
    > pip install django-outbox-menu

### Add to INSTALLED_APPS
    INSTALLED_APPS = [        
        'django.contrib.sites', 
        'menu',
    ]

### Add SITE_ID in user settings.py
    SITE_ID = 1

### Include library URLS
    urlpatterns += [
        path('', include('menu.urls')),
    ]

### Install requirements
    Activate your environment using
    > mkvirtualenv env_menu    

### Migrate to create table to your database
    > python manage.py migrate

## In your django Templates

### Load menu tags
    > {% load menu_tags %}

### Generate menu
    > {% menu_create FRONTEND 0 as my_menu %}     
    syntax :
        > menu_create <menu_kind> <menu_group> as var_name
        > menu_kind  : FRONTEND or BACKEND
        > menu_group : 
            0 : None (use only for FRONTEND)
            1 : Owner
            2 : Manager
            3 : Operator
            4 : Cashier
            etc ... (Update in admin page section [Menu Groups])

    > {% for n in my_menu %}
        n have all menu fields such as :
        n.id
        n.parent_id
        n.name
        n.link
        n.icon
        n.is_external
        n.level
        n.haveChild
        n.haveChildEndTag
        You can use it inside for loop

    > example in you templates
        <ul class="main-menu">
            {% menu_create FRONTEND 0 as my_menu %}                    
            {% for n in my_menu %}

                {% if forloop.first %}                      
                    <li class="main-menu-active">
                {% else %}
                    <li>
                {% endif %}

                {% if n.haveChild %}
                    <a href="#"> {{n.name}}
                        {% if n.parent_id %}
                            <i class="zmdi zmdi-chevron-right text-to-right"></i>
                        {% endif %}
                    </a>
                    <ul class="sub-menu">                            
                {% else %}                                
                    <a class="clear-content-right" href="#"> {{n.name}} </a>                            
                {% endif %}
                                                                
                
                {% for i in n.haveChildEndTag %}
                    <!-- Count = {{forloop.counter}} -->
                    {% if forloop.last %}
                        {% if n.parent_id %}
                            </li></ul>
                            {% if not n.haveChild %}                                                
                                </li> <!-- li -->                            
                            {% endif %}  
                        {% else %}
                            </li> <!-- Root -->
                        {% endif %}

                    {% else %}
                        </li></ul>
                    {% endif %}       

                {% endfor %}                            
                                            
            {% endfor %}                                        
        </ul> 

### Run project
    > python manage.py runserver
    on you browser :
    127.0.0.1:8000
    127.0.0.1:8000/menu
    127.0.0.1:8000/admin
