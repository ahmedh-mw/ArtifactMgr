class Utils:
    @staticmethod
    def getList(jsonObject, listName):
        listObject  = jsonObject.get(listName)
        if not listObject:
            listObject = []
        return listObject
    
    def getBoolean(jsonObject, fieldName, defaultValue=False):
        item = jsonObject.get(fieldName)
        if not item:
            listObject = defaultValue
        return listObject
    
    def getDic(jsonObject, fieldName, defaultValue={}):
        dic = jsonObject.get(fieldName)
        if not dic:
            dic = defaultValue
        return dic