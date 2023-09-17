from typing import List
from ..element import Element

# Annahme: `Element` und andere Abhängigkeiten sind bereits definiert

from typing import List, Any
from ..element import Element

class TreeSelect(Element):

    def __init__(
            self, 
            content: List[Element] = None,
            allowClear = None,
            autoClearSearchValue = None,
            bordered = None,
            defaultValue = None,
            disabled = None,
            popupClassName = None,
            popupMatchSelectWidth = None,
            dropdownRender = None,
            dropdownStyle = None,
            fieldNames = None,
            filterTreeNode = None,
            getPopupContainer = None,
            labelInValue = None,
            listHeight = None,
            loadData = None,
            maxTagCount = None,
            maxTagPlaceholder = None,
            maxTagTextLength = None,
            multiple = None,
            notFoundContent = None,
            placeholder = None,
            placement = None,
            searchValue = None,
            showCheckedStrategy = None,
            showSearch = None,
            size = None,
            status = None,
            suffixIcon = None,
            switcherIcon = None,
            tagRender = None,
            treeCheckable = None,
            treeCheckStrictly = None,
            treeData = None,
            treeDataSimpleMode = None,
            treeDefaultExpandAll = None,
            treeDefaultExpandedKeys = None,
            treeExpandAction = None,
            treeExpandedKeys = None,
            treeIcon = None,
            treeLoadedKeys = None,
            treeLine = None,
            treeNodeFilterProp = None,
            treeNodeLabelProp = None,
            value = None,
            virtual = None,
            onChange = None,
            onDropdownVisibleChange = None,
            onSearch = None,
            onSelect = None,
            onTreeExpand = None,
            ):
        super().__init__(component='TreeSelect')
        self.children = content
        self.props["allowClear"] = allowClear
        self.props["autoClearSearchValue"] = autoClearSearchValue
        self.props["bordered"] = bordered
        self.props["defaultValue"] = defaultValue
        self.props["disabled"] = disabled
        self.props["popupClassName"] = popupClassName
        self.props["popupMatchSelectWidth"] = popupMatchSelectWidth
        self.props["dropdownRender"] = dropdownRender
        self.props["dropdownStyle"] = dropdownStyle
        self.props["fieldNames"] = fieldNames
        self.props["filterTreeNode"] = filterTreeNode
        self.props["getPopupContainer"] = getPopupContainer
        self.props["labelInValue"] = labelInValue
        self.props["listHeight"] = listHeight
        self.props["loadData"] = loadData
        self.props["maxTagCount"] = maxTagCount
        self.props["maxTagPlaceholder"] = maxTagPlaceholder
        self.props["maxTagTextLength"] = maxTagTextLength
        self.props["multiple"] = multiple
        self.props["notFoundContent"] = notFoundContent
        self.props["placeholder"] = placeholder
        self.props["placement"] = placement
        self.props["searchValue"] = searchValue
        self.props["showCheckedStrategy"] = showCheckedStrategy
        self.props["showSearch"] = showSearch
        self.props["size"] = size
        self.props["status"] = status
        self.props["suffixIcon"] = suffixIcon
        self.props["switcherIcon"] = switcherIcon
        self.props["tagRender"] = tagRender
        self.props["treeCheckable"] = treeCheckable
        self.props["treeCheckStrictly"] = treeCheckStrictly
        self.props["treeData"] = treeData
        self.props["treeDataSimpleMode"] = treeDataSimpleMode
        self.props["treeDefaultExpandAll"] = treeDefaultExpandAll
        self.props["treeDefaultExpandedKeys"] = treeDefaultExpandedKeys
        self.props["treeExpandAction"] = treeExpandAction
        self.props["treeExpandedKeys"] = treeExpandedKeys
        self.props["treeIcon"] = treeIcon
        self.props["treeLoadedKeys"] = treeLoadedKeys
        self.props["treeLine"] = treeLine
        self.props["treeNodeFilterProp"] = treeNodeFilterProp
        self.props["treeNodeLabelProp"] = treeNodeLabelProp
        self.props["value"] = value
        self.props["virtual"] = virtual
        if not onChange == None:
            self.props["onChange"] = onChange
        if not onDropdownVisibleChange == None:
            self.props["onDropdownVisibleChange"] = onDropdownVisibleChange
        if not onSearch == None:
            self.props["onSearch"] = onSearch
        if not onSelect == None:
            self.props["onSelect"] = onSelect
        if not onTreeExpand == None:
            self.props["onTreeExpand"] = onTreeExpand
