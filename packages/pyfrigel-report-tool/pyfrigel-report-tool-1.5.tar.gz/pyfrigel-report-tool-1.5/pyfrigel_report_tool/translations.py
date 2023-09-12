MISSING_STRING = '__missing__'
AVAILABLE_LANGUAGES = ['en']

REPORT_TRANSLATIONS ={
    'SYNCRO PERFORMANCE REPORT': {
        'en': 'SYNCRO PERFORMANCE REPORT'
    },

    'Machine operation': {
        'en': 'Machine operation'
    },
    
    'ON Time': {
        'en': 'ON Time'
    },
    
    'vs {}h (prev week)': {
        'en': 'vs {}h (prev week)'
    },
    
    '{}% (prev week)': {
        'en': '{}% (prev week)'
    },

    'ON': {
        'en': 'ON'
    },
    
    'OFF': {
        'en': 'OFF'
    },
 
    'Working hours': {
        'en': 'Working hours'
    },
    
    'Working modes': {
        'en': 'Working modes'
    },

    'Phases': {
        'en': 'Phases'
    },
    
    'Time': {
        'en': 'Time'
    },
    
    'Trend (prev. week)': {
        'en': 'Trend (prev. week)'
    },
    
    'Standard': {
        'en': 'Standard'
    },
    
    'Production': {
        'en': 'Production'
    },
    
    'Maintenance': {
        'en': 'Maintenance'
    },
    
    'Phases hours': {
        'en': 'Phases hours'
    },
    'Performance Overview':{
         'en': 'Performance Overview'
    },
    'Mold':{
         'en': 'Mold'
    }, 
    'Time ON':{
         'en': 'Time ON'
    },
    'Std':{
         'en': 'Standard'
    },
    'Sync':{
         'en': 'Syncro'
    }, 
    'Cycle time' : {
        'en': 'Cycle time'
    },
    'Recipes':{
         'en': 'Recipes'
    },
    'Recipe name':{
         'en': 'Recipe name'
    },
    'Machine SN:':{
         'en': 'Machine SN:'
    },
    'Custom name:':{
         'en': 'Custom name:'
    },
    'Model:':{
         'en': 'Model:'
    },
    'Reference period:':{
         'en': 'Reference period:'
    },
    'Cycle time':{
         'en': 'Cycle time'
    },

}



class Translations():
    
    def __init__(self, language):
        '''
        
        '''
        self.language = language
        
    def getTranslation(self, id) -> str:
        try:
            return REPORT_TRANSLATIONS[id][self.language]
        except:
             try:
                 return REPORT_TRANSLATIONS[id][self.language]
             except:
                 return MISSING_STRING