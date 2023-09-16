
#https://fangpenlin.com/posts/2012/08/26/good-logging-practice-in-python/

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {
            'format': '%(asctime)s - %(name)s - %(levelname)s: %(message)s'
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',              
        },
        'file_handler': {
            'class': 'logging.FileHandler',
            'level': 'DEBUG',
            'formatter': 'simple',
            'filename': 'example.log',
            #'mode': 'a'
            'mode' : 'w'
        }        
    },
    'loggers': {
        '': {
            'level': 'DEBUG',
            'handlers': ['console', 'file_handler'],                
        },
    },
}