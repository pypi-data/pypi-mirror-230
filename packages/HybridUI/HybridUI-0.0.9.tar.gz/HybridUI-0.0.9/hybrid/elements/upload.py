from typing import List
from ..element import Element

# Annahme: `Element` und andere Abhängigkeiten sind bereits definiert

class Upload(Element):
    """
    
        children, 
        accept,	
        action,	
        beforeUpload,	
        customRequest,	
        data,	
        defaultFileList,
        directory,	
        disabled,	
        fileList,	
        headers,	
        iconRender,		
        isImageUrl,	
        itemRender,	 
        listType,	
        maxCount,	
        method,	
        multiple,	
        name,	
        openFileDialogOnClick,	
        previewFile	,
        progress,	
        showUploadList,	
        withCredentials,	
        onChange,	
        onDrop	,
        onDownload,	
        onPreview,		
        onRemove	

    
    """
    def __init__(
            self, 
            text = None,
            accept= None,	
            action= None,	
            beforeUpload= None,	
            customRequest= None,
            data= None,	
            defaultFileList= None,	
            directory= None,
            disabled= None,	
            fileList= None,	
            headers= None,	
            iconRender= None,	
            isImageUrl= None,	
            itemRender= None,	
            listType= None,	
            maxCount	= None,
            method	= None,
            multiple= None,	
            name	= None,
            openFileDialogOnClick= None,	
            previewFile		= None,
            progress= None,	
            showUploadList	= None,
            withCredentials	= None,	
            onChange	= None,
            onDrop	= None,
            onDownload	= None,
            onPreview= None,	
            onRemove= None,
            
            ):
        super().__init__(component='Upload')
        self.children = [text] 
        if  action  is not  None:
            self._props["action"] = action
        if  accept  is not  None:
            self._props["accept"] = accept
        if  beforeUpload  is not  None:
            self._props["beforeUpload"] = beforeUpload
        if  customRequest  is not  None:
            self._props["customRequest"] = customRequest
        if  data   is not  None:
            self._props["data"] = data
        if  defaultFileList  is not  None:
            self._props["defaultFileList"] = defaultFileList
        if   directory  is not  None:
            self._props["directory"] = directory
        if   disabled is not  None:
            self._props["disabled"] = disabled
        if  fileList  is not  None:
            self._props["fileList"] = fileList
        if   headers is not  None:
            self._props["headers"] = headers
        if  iconRender  is not  None:
            self._props["iconRender"] = iconRender
        if   isImageUrl is not  None:
            self._props["isImageUrl"] = isImageUrl
        if   itemRender is not  None:
            self._props["itemRender"] = itemRender
        if  listType  is not  None:
            self._props["listType"] = listType
        if  maxCount  is not  None:
            self._props["maxCount"] = maxCount
        if   method is not  None:
            self._props["method"] = method
        if  multiple  is not  None:
            self._props["multiple"] = multiple
        if   name is not  None:
            self._props["name"] = name
        if   openFileDialogOnClick is not  None:
            self._props["openFileDialogOnClick"] = openFileDialogOnClick
        if   previewFile is not  None:
            self._props["previewFile"] = previewFile
        if   progress is not  None:
            self._props["progress"] = progress
        if   showUploadList is not  None:
            self._props["showUploadList"] = showUploadList
        if   withCredentials is not  None:
            self._props["withCredentials"] = withCredentials
        if   onChange is not  None:
            self._props["onChange"] = onChange
        if   onDrop is not  None:
            self._props["onDrop"] = onDrop
        if   onDownload is not  None:
            self._props["onDownload"] = onDownload
        if   onPreview is not  None:
            self._props["onPreview"] = onPreview
        if   onRemove is not  None:
            self._props["onRemove"] = onRemove

 