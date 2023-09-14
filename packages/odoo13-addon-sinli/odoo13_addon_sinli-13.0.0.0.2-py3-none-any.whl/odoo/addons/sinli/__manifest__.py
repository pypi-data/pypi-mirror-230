# -*- coding: utf-8 -*-
######################################################################################
#
#         License**
#
########################################################################################
{
    'name': 'Integración de sinli en Odoo',
    'version': '13.0.0.0.2',
    'summary': 'Módulo para la integración de sinli en Odoo.',
    'description': 'Módulo para la integración de sinli en Odoo.',
    'category': 'Industries',
    'author': 'Colectivo DEVCONTROL',
    'author_email': 'devcontrol@zici.fr',
    'maintainer': 'Colectivo DEVCONTROL',
    'company': 'Colectivo DEVCONTROL',
    'website': 'https://framagit.org/devcontrol',
    'depends': ['sale'],
    "external_dependencies": {"python" : [
        "sinli",
        "python-stdnum"
    ]},
    'data': [
        'views/export_libro_view.xml',
        'views/download_file.xml'
    ],
    'images': ['static/description/logo-devcontrol.png'],
    'license': 'OPL-1',
    'price': 0,
    'currency': 'EUR',
    'installable': True,
    'application': False,
    'auto_install': False,
}
