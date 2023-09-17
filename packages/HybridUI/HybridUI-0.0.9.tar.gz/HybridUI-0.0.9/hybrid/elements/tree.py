from typing import List, Any
from ..element import Element

class Tree(Element):

    def __init__(
            self, 
            content: List[Element] = None,
            allowDrop = None,
            autoExpandParent = None,
            blockNode = None,
            checkable = None,
            checkedKeys = None,
            checkStrictly = None,
            defaultCheckedKeys = None,
            defaultExpandAll = None,
            defaultExpandedKeys = None,
            defaultExpandParent = None,
            defaultSelectedKeys = None,
            disabled = None,
            draggable = None,
            expandedKeys = None,
            fieldNames = None,
            filterTreeNode = None,
            height = None,
            icon = None,
            loadData = None,
            loadedKeys = None,
            multiple = None,
            rootStyle = None,
            selectable = None,
            selectedKeys = None,
            showIcon = None,
            showLine = None,
            switcherIcon = None,
            titleRender = None,
            treeData = None,
            virtual = None,
            onCheck = None,
            onDragEnd = None,
            onDragEnter = None,
            onDragLeave = None,
            onDragOver = None,
            onDragStart = None,
            onDrop = None,
            onExpand = None,
            onLoad = None,
            onRightClick = None,
            onSelect = None,
            ):
        super().__init__(component='Tree')
        self.children = content
        self._props["allowDrop"] = allowDrop
        self._props["autoExpandParent"] = autoExpandParent
        self._props["blockNode"] = blockNode
        self._props["checkable"] = checkable
        self._props["checkedKeys"] = checkedKeys
        self._props["checkStrictly"] = checkStrictly
        self._props["defaultCheckedKeys"] = defaultCheckedKeys
        self._props["defaultExpandAll"] = defaultExpandAll
        self._props["defaultExpandedKeys"] = defaultExpandedKeys
        self._props["defaultExpandParent"] = defaultExpandParent
        self._props["defaultSelectedKeys"] = defaultSelectedKeys
        self._props["disabled"] = disabled
        self._props["draggable"] = draggable
        self._props["expandedKeys"] = expandedKeys
        self._props["fieldNames"] = fieldNames
        self._props["filterTreeNode"] = filterTreeNode
        self._props["height"] = height
        self._props["icon"] = icon
        self._props["loadData"] = loadData
        self._props["loadedKeys"] = loadedKeys
        self._props["multiple"] = multiple
        self._props["rootStyle"] = rootStyle
        self._props["selectable"] = selectable
        self._props["selectedKeys"] = selectedKeys
        self._props["showIcon"] = showIcon
        self._props["showLine"] = showLine
        self._props["switcherIcon"] = switcherIcon
        self._props["titleRender"] = titleRender
        self._props["treeData"] = treeData
        self._props["virtual"] = virtual
        if not onCheck == None:
            self._props["onCheck"] = onCheck
        if not onCheck == None:
            self._props["onDragEnd"] = onDragEnd
        if not onCheck == None:
            self._props["onDragEnter"] = onDragEnter
        if not onCheck == None:
            self._props["onDragLeave"] = onDragLeave
        if not onCheck == None:
            self._props["onDragOver"] = onDragOver
        if not onCheck == None:
            self._props["onDragStart"] = onDragStart
        if not onCheck == None:
            self._props["onDrop"] = onDrop
        if not onCheck == None:
            self._props["onExpand"] = onExpand
        if not onCheck == None:
            self._props["onLoad"] = onLoad
        if not onCheck == None:
            self._props["onRightClick"] = onRightClick
        if not onCheck == None:
            self._props["onSelect"] = onSelect

class TreeNode(Element):
    def __init__(
            self, 
            content: List[Element] = None,
            checkable = None,
            disableCheckbox = None,
            disabled = None,
            icon = None,
            isLeaf = None,
            key = None,
            selectable = None,
            title = None,
            ):
        super().__init__(component='TreeNode')
        self.content = content
        self._props["checkable"] = checkable
        self._props["disableCheckbox"] = disableCheckbox
        self._props["disabled"] = disabled
        self._props["icon"] = icon
        self._props["isLeaf"] = isLeaf
        self._props["key"] = key
        self._props["selectable"] = selectable
        self._props["title"] = title

class DirectoryTree(Element):
    """
    expandAction: string
        Action to expand the tree node.
    """

    def __init__(self, content: List[Element] = None, expandAction= None):
        super().__init__(component='DirectoryTree')
        self.children = content
        self._props["expandAction"] = expandAction



    """    
    TreeNode props


    checkable	
    disableCheckbox	
    disabled
    icon	
    isLeaf	
    key	
    selectable	
    title	


    DirectoryTree props

    expandAction	
    """
   