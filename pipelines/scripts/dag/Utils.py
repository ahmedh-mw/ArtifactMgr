class Utils:
    @staticmethod
    def getList(jsonObject, listName):
        listObject  = jsonObject.get(listName)
        if listObject is None:
            listObject = []
        return listObject
    
    def getBoolean(jsonObject, fieldName, defaultValue=False):
        item = jsonObject.get(fieldName)
        if item is None:
            item = defaultValue
        return item
    
    def getDic(jsonObject, fieldName, defaultValue={}):
        dic = jsonObject.get(fieldName)
        if dic is None:
            dic = defaultValue
        return dic