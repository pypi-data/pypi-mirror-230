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
        self.props["allowDrop"] = allowDrop
        self.props["autoExpandParent"] = autoExpandParent
        self.props["blockNode"] = blockNode
        self.props["checkable"] = checkable
        self.props["checkedKeys"] = checkedKeys
        self.props["checkStrictly"] = checkStrictly
        self.props["defaultCheckedKeys"] = defaultCheckedKeys
        self.props["defaultExpandAll"] = defaultExpandAll
        self.props["defaultExpandedKeys"] = defaultExpandedKeys
        self.props["defaultExpandParent"] = defaultExpandParent
        self.props["defaultSelectedKeys"] = defaultSelectedKeys
        self.props["disabled"] = disabled
        self.props["draggable"] = draggable
        self.props["expandedKeys"] = expandedKeys
        self.props["fieldNames"] = fieldNames
        self.props["filterTreeNode"] = filterTreeNode
        self.props["height"] = height
        self.props["icon"] = icon
        self.props["loadData"] = loadData
        self.props["loadedKeys"] = loadedKeys
        self.props["multiple"] = multiple
        self.props["rootStyle"] = rootStyle
        self.props["selectable"] = selectable
        self.props["selectedKeys"] = selectedKeys
        self.props["showIcon"] = showIcon
        self.props["showLine"] = showLine
        self.props["switcherIcon"] = switcherIcon
        self.props["titleRender"] = titleRender
        self.props["treeData"] = treeData
        self.props["virtual"] = virtual
        if not onCheck == None:
            self.props["onCheck"] = onCheck
        if not onCheck == None:
            self.props["onDragEnd"] = onDragEnd
        if not onCheck == None:
            self.props["onDragEnter"] = onDragEnter
        if not onCheck == None:
            self.props["onDragLeave"] = onDragLeave
        if not onCheck == None:
            self.props["onDragOver"] = onDragOver
        if not onCheck == None:
            self.props["onDragStart"] = onDragStart
        if not onCheck == None:
            self.props["onDrop"] = onDrop
        if not onCheck == None:
            self.props["onExpand"] = onExpand
        if not onCheck == None:
            self.props["onLoad"] = onLoad
        if not onCheck == None:
            self.props["onRightClick"] = onRightClick
        if not onCheck == None:
            self.props["onSelect"] = onSelect

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
        self.props["checkable"] = checkable
        self.props["disableCheckbox"] = disableCheckbox
        self.props["disabled"] = disabled
        self.props["icon"] = icon
        self.props["isLeaf"] = isLeaf
        self.props["key"] = key
        self.props["selectable"] = selectable
        self.props["title"] = title

class DirectoryTree(Element):
    """
    expandAction: string
        Action to expand the tree node.
    """

    def __init__(self, content: List[Element] = None, expandAction= None):
        super().__init__(component='DirectoryTree')
        self.children = content
        self.props["expandAction"] = expandAction



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
   