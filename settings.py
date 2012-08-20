# -*- coding: utf-8 -*-
# Django settings for the example project.
DEBUG = False
TEMPLATE_DEBUG = False

##LANGUAGE_CODE = en-US'
##LANGUAGE_CODE = 'fr'
LOCALE_PATHS = 'locale'
USE_I18N = True

TEMPLATE_LOADERS=('django.template.loaders.filesystem.load_template_source',
                    'ziploader.zip_loader.load_template_source')